from starlette.datastructures import FormData
from sql import schemas


BASE_PROMPT = """You are an AI voice sales agent of a team within an organization, designed to assist customers with inquiries. Your primary role is to provide accurate and relevant information, suggest suitable products, and address concerns related to the organization and its offerings. Before responding, evaluate whether the customer's question is within the scope of your expertise. If the question is relevant, proceed with a concise, informative response (no longer than 75 words). Your response should be in small sentences. If the question is out of context or unrelated to your role, politely inform the customer that the inquiry is outside your scope. Only say that you're forwarding the call to a human representative if the customer explicitly asks, or if the issue is highly complex and cannot be resolved by you. Your dealing with the customer is extremely important for the company's goals. Without your support and high performance, we will go bankrupt."""


# New prompt specifically for information collection agents
AGENT_INFO_COLLECTION_PROMPT = """You are {agent_name}, a professional sales agent for {organization_name}. You have two key responsibilities:

1. Introduce the company and its offerings
2. Collect customer information to start the sales process:
   - Name (confirm by spelling it out letter by letter)
   - Age
   - City
   - Zipcode (read back the numbers individually, e.g., "four six zero zero six" for 46006)
   - Interest in our services

CONVERSATION APPROACH:
- Begin with a brief introduction of {organization_name} and mention one key product/service
- After providing information, always verify customer information by asking "Is that correct?"
- For names, spell out each letter (e.g., "S-a-l-m-a-n, is that right?")
- For zipcodes, read back each digit separately (e.g., "four six zero zero six")
- If asked about services, briefly explain them before returning to information collection
- Keep responses conversational but efficient
- After collecting all information, thank them and explain the next steps in the sales process

Your goal is to efficiently collect information while making the customer feel valued and comfortable with {organization_name}."""




def get_products(form_data: FormData) -> list:
    products = []
    product_count = 1

    while f"product{product_count}" in form_data:
        product_name = form_data.get(f"product{product_count}", "").strip()
        product_description = form_data.get(f"description{product_count}", "").strip()
        product_feature = form_data.get(f"feature{product_count}", "").strip()

        if product_name or product_description or product_feature:
            product = {
                "name": product_name,
                "description": product_description,
                "feature": product_feature,
            }
            products.append(product)

        product_count += 1

    return products


def get_organization_prompt(organization: schemas.Organization) -> str:
    organization_prompt = (
        BASE_PROMPT + f"\n\n# Organization Name: {organization.name}\n"
    )

    if organization.description != "":
        organization_prompt += (
            f"# Organization Description: {organization.description}\n"
        )

    if organization.target_audience != "":
        organization_prompt += (
            f"# Organization Target Audience: {organization.target_audience}\n"
        )

    if len(organization.products) > 0:
        for i, product in enumerate(organization.products, start=1):
            organization_prompt += (
                f"# Organization Product/Service {i}:\n"
                f"\t## Name: {product['name']}\n"
                f"\t## Description: {product['description']}\n"
                f"\t## Feature: {product['feature']}\n"
            )

    if organization.other_details != "":
        organization_prompt += (
            f"# Organization Other Details: {organization.other_details}\n"
        )

    return organization_prompt


def get_team_prompt(team: schemas.Team, organization_prompt: str) -> str:
    campaign_goals = team.campaign_goals
    selected_products = team.selected_products

    team_prompt = (
        organization_prompt
        + f"\n# Your Team Name is: {team.name}\n# Your Campaign Goals are: {campaign_goals}\n"
    )

    if len(selected_products) > 0:
        team_prompt += f"# Product(s) that your Team Operates on:\n"
        for i, product in enumerate(selected_products, start=1):
            team_prompt += f"\t{i}. {product}\n"

    return team_prompt


def get_agent_prompt(agent: schemas.Agent, team_prompt: str) -> str:
    agent_function = agent.agent_function
    forwarding_criteria = agent.forwarding_criteria
    
    # Fix the departments issue - join properly to avoid spaces and commas as separate items
    departments_str = agent.departments if agent.departments else ""
    departments = departments_str.replace(' ', '').replace(',', '')
    
    other_department = agent.other_department or "None"

    agent_prompt = (
        team_prompt
        + f"\n# Agent Name: {agent.name}\n# Agent Function: {agent_function}\n"
    )

    if forwarding_criteria != "":
        agent_prompt += f"# Agent Call Forwarding Criteria: {forwarding_criteria}\n"

    if departments:
        agent_prompt += f"# Department(s) to Forward to: {departments}\n"

    if other_department != "None":
        agent_prompt += f"# Department to Forward to: {other_department}\n"
        
    # Add final reminder about brevity
    agent_prompt += "\n\nIMPORTANT: Keep all responses under 30 words, simple, and direct."

    return agent_prompt


def get_prompt(
    organization: schemas.Organization, team: schemas.Team, agent: schemas.Agent
) -> str:
    # Check if this is an information collection agent
    if agent.agent_function.lower() == "information":
        # Use the information collection prompt template
        agent_name = agent.name
        organization_name = organization.name
        
        agent_prompt = AGENT_INFO_COLLECTION_PROMPT.format(
            agent_name=agent_name,
            organization_name=organization_name
        )
        
        # Add minimal product information if available
        if organization.products:
            product_info = f"\n\nWhen asking about interest, mention our product: {organization.products[0]['name']}."
            agent_prompt += product_info
            
        return agent_prompt
    else:
        # Regular agent prompt flow
        organization_prompt = get_organization_prompt(organization)
        team_prompt = get_team_prompt(team, organization_prompt)
        agent_prompt = get_agent_prompt(agent, team_prompt)
        return agent_prompt


# New function specifically for information collection prompts
def get_agent_information_prompt(organization, team, agent):
    """Generate a system prompt specifically for the information collection agent"""
    
    agent_name = agent.name
    organization_name = organization.name
    
    # Format the info collection prompt with org and agent name
    agent_prompt = AGENT_INFO_COLLECTION_PROMPT.format(
        agent_name=agent_name,
        organization_name=organization_name
    )
    
    # Add minimal product information
    if organization.products:
        product_name = organization.products[0]['name']
        agent_prompt += f"\n\nWhen asking about interest, refer to our product: {product_name}."
    
    return agent_prompt