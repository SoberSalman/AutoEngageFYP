from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Dict, Any, Optional
import os

from .tools import ValidateZipcodeTool, GetProductInfoTool, create_user_info_tools

class InfoCollectionAgent:
    """Agent for collecting user information in a conversational manner."""
    
    def __init__(
        self, 
        user_info_instance, 
        agent_name: str, 
        organization_name: str,
        products: Optional[List[Dict[str, Any]]] = None,
        api_key: Optional[str] = None
    ):
        self.user_info = user_info_instance
        self.agent_name = agent_name
        self.organization_name = organization_name
        
        # Set up the OpenAI API key
        api_key = api_key or os.getenv("LLM_EC2_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        # Convert products to the expected format
        product_dict = {}
        if products:
            for product in products:
                product_dict[product.get('name', '')] = {
                    'description': product.get('description', ''),
                    'feature': product.get('feature', '')
                }
        
        # Create tools
        self.tools = create_user_info_tools(user_info_instance)
        self.tools.append(ValidateZipcodeTool())
        self.tools.append(GetProductInfoTool(products=product_dict))
        
        # Create LLM
        self.llm = ChatOpenAI(
            temperature=0.7, 
            api_key=api_key, 
            model="gpt-4o-mini", 
            streaming=True
        )
        
        # Create conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )
        
        # Store the base system message template for later updates
        self.system_message_template = """You are {agent_name}, a friendly sales agent for {organization_name}. Your goal is to:

1. Introduce {organization_name} and its offerings
2. Collect and verify the following information from the user:
   - Name (confirm by spelling it out letter by letter)
   - Age
   - City
   - Zipcode (read back as individual digits, e.g., "four six zero zero six")
   - Interest in services

Follow these guidelines:
- Be conversational but efficient
- After collecting each piece of information, verify it by asking "Is that correct?"
- For names, spell out each letter (e.g., "S-a-l-m-a-n, is that right?")
- For zipcodes, read back each digit individually
- If asked about services, explain them before returning to information collection
- After collecting all information, thank the user and explain next steps
- IMPORTANT: Never ask for information you already have

Current user information: {user_info}
"""
        
        # Create the executor with initial setup
        self._create_agent_executor()
    
    def _create_agent_executor(self):
        """Create a new agent executor with updated system message"""
        # Format the system message with current information
        system_message = self.system_message_template.format(
            agent_name=self.agent_name,
            organization_name=self.organization_name,
            user_info=str(self.user_info)
        )
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def process_message(self, message: str) -> str:
        """Process a user message and return the agent's response."""
        # Recreate the agent with updated system message
        self._create_agent_executor()
        
        try:
            # Run the agent executor
            return self.agent_executor.invoke({"input": message})["output"]
        except Exception as e:
            print(f"Error in agent: {e}")
            # Fallback response if there's an error
            return "I'm sorry, I'm having trouble processing that. Could you please try again?"