import streamlit as st
import sqlite3
import json
import pandas as pd
from html import escape

# Set page configuration
st.set_page_config(page_title="Chat History Viewer", layout="wide")

# Apply custom styling
st.markdown("""
<style>
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 10px;
    }
    .user-message-container {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 10px;
    }
    .bot-message-container {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #DCF8C6;
        color: #000;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-right-radius: 5px;
        max-width: 80%;
        word-wrap: break-word;
    }
    .bot-message {
        background-color: #E8E8E8;
        color: #000;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-left-radius: 5px;
        max-width: 80%;
        word-wrap: break-word;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f3ff;
        border-bottom: 2px solid #4e89e3;
    }
</style>
""", unsafe_allow_html=True)

def fetch_chat_history(db_path="schema.db"):
    """
    Directly connect to the SQLite database and fetch chat history
    """
    try:
        conn = sqlite3.connect(db_path)
        query = """SELECT id, chat_data FROM chat_history"""
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

def parse_chat_data(chat_data_str):
    """
    Parse the chat_data string into a JSON object
    """
    try:
        # Handle case where the data is already a list
        if isinstance(chat_data_str, list):
            return chat_data_str
            
        # Try to parse as JSON
        return json.loads(chat_data_str)
    except (json.JSONDecodeError, TypeError) as e:
        st.error(f"Error parsing chat data: {e}")
        return None

def display_chat(messages):
    """Display chat messages using Streamlit components"""
    if not messages:
        st.warning("No messages found in this chat.")
        return
        
    for msg in messages:
        if msg.get("role") == "system":
            continue  # Skip system messages
            
        content = msg.get("content", "")
        # Remove Filler prefix from assistant messages
        if msg.get("role") == "assistant":
            content = content.replace("Filler:", "").strip()
            
        if msg.get("role") == "user":
            st.markdown(f'<div class="user-message-container"><div class="user-message">{escape(content)}</div></div>', 
                        unsafe_allow_html=True)
        elif msg.get("role") == "assistant":
            st.markdown(f'<div class="bot-message-container"><div class="bot-message">{escape(content)}</div></div>', 
                        unsafe_allow_html=True)

def main():
    st.title("💬 Chat History Viewer")
    
    # Allow user to input database path
    db_path = st.text_input("Database Path", value="schema.db")
    
    # Fetch data from database
    df = fetch_chat_history(db_path)
    
    if df is not None and not df.empty:
        # Create tabs for different chats
        chat_tabs = st.tabs([f"Chat {chat_id}" for chat_id in df['id']])
        
        for i, (_, row) in enumerate(df.iterrows()):
            with chat_tabs[i]:
                chat_data = parse_chat_data(row['chat_data'])
                
                if chat_data:
                    # Create tabs for view modes
                    tab1, tab2 = st.tabs(["Chat View", "Debug View"])
                    
                    with tab1:
                        display_chat(chat_data)
                    
                    with tab2:
                        st.json(chat_data)
                else:
                    st.error("Could not parse chat data for this chat.")
    else:
        st.warning("No chat history found in the database.")
        
        # Add a button to retry connection
        if st.button("Retry Database Connection"):
            st.experimental_rerun()

if __name__ == "__main__":
    main()