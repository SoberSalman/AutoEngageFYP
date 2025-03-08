from langchain.agents import AgentExecutor, LLMSingleActionAgent
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from typing import List, Dict, Any, Optional
import os

from .prompts import InfoCollectionAgentPrompt, get_agent_prompt
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
        api_key = api_key or os.getenv("OPENAI_API_KEY")
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
        self.tools.append(GetProductInfoTool(product_dict))
        
        # Create LLM
        self.llm = ChatOpenAI(temperature=0.7, api_key=api_key)
        
        # Create prompt
        prompt_template = get_agent_prompt(agent_name, organization_name)
        self.prompt = InfoCollectionAgentPrompt(
            template=prompt_template,
            input_variables=["input", "user_info", "agent_scratchpad"]
        )
        
        # Create LLM chain
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)
        
        # Create agent
        self.agent = LLMSingleActionAgent(
            llm_chain=self.llm_chain,
            allowed_tools=[tool.name for tool in self.tools],
            verbose=True
        )
        
        # Create memory
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Create agent executor
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory
        )
    
    def process_message(self, message: str) -> str:
        """Process a user message and return the agent's response."""
        return self.agent_executor.run(
            input=message,
            user_info=str(self.user_info)
        )