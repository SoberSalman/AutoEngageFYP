from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    username: str
    password: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    organization_id: Optional[int] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    organization_id: Optional[int] = None

    class Config:
        from_attributes = True


# Organization Schemas
class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    products: Optional[List[Dict[str, str]]] = None
    other_details: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int
    users: List[User] = []
    teams: List["Team"] = []

    class Config:
        from_attributes = True


# Team Schemas
class TeamBase(BaseModel):
    name: str
    campaign_goals: Optional[str] = None
    selected_products: Optional[List[str]] = None


class TeamCreate(TeamBase):
    organization_id: int


class TeamUpdate(TeamBase):
    organization_id: int


class Team(TeamBase):
    id: int
    organization_id: int
    agents: List["Agent"] = []

    class Config:
        from_attributes = True


# Agent Schemas
class AgentBase(BaseModel):
    name: str
    agent_function: Optional[str] = None
    forwarding_criteria: Optional[str] = None
    departments: Optional[str] = None
    other_department: Optional[str] = None
    use_elevenlabs: bool = False
    voice_id: Optional[str] = None


class AgentCreate(AgentBase):
    team_id: int


class AgentUpdate(AgentBase):
    team_id: int


class Agent(AgentBase):
    id: int
    team_id: int

    class Config:
        from_attributes = True


# Chat History Schemas
class ChatHistoryBase(BaseModel):
    organization_id: int
    team_id: int
    agent_id: int
    chat_data: Optional[List[dict]] = None
    response_time: Optional[float] = None


class ChatHistoryCreate(ChatHistoryBase):
    pass


class ChatHistoryUpdate(ChatHistoryBase):
    pass


class ChatHistory(ChatHistoryBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
