from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sql import crud, schemas
from sql.database import SessionLocal


router = APIRouter()


# Database Dependency Function to Manage Database Sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoint to Create a User
@router.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user(db=db, username=user.username):
        raise HTTPException(status_code=400, detail="User already exists.")
    return crud.create_user(db=db, user=user)


# Endpoint to Get all Users
@router.get("/users/", response_model=list[schemas.User])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db=db, skip=skip, limit=limit)


# Endpoint to Update a User
@router.put("/users/{username}", response_model=schemas.User)
async def update_user(
    username: str, user: schemas.UserUpdate, db: Session = Depends(get_db)
):
    existing_user = crud.update_user(db=db, username=username, user=user)
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return existing_user


# Endpoint to Delete a User
@router.delete("/users/{username}", response_model=schemas.User)
async def delete_user(username: str, db: Session = Depends(get_db)):
    if not crud.get_user(db=db, username=username):
        raise HTTPException(status_code=404, detail="User not found.")
    return crud.delete_user(db=db, username=username)


# Endpoint to Get all Organizations
@router.get("/organizations/", response_model=list[schemas.Organization])
async def get_organizations(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_organizations(db=db, skip=skip, limit=limit)


# Endpoint to Update an Organization
@router.put("/organizations/{organization_id}", response_model=schemas.Organization)
async def update_organization(
    organization_id: int,
    organization: schemas.OrganizationUpdate,
    db: Session = Depends(get_db),
):
    existing_organization = crud.update_organization(
        db=db, organization_id=organization_id, organization=organization
    )
    if existing_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found.")
    return existing_organization


# Endpoint to Delete an Organization
@router.delete("/organizations/{organization_id}", response_model=schemas.Organization)
async def delete_organization(organization_id: int, db: Session = Depends(get_db)):
    if not crud.get_organization(db=db, organization_id=organization_id):
        raise HTTPException(status_code=404, detail="Organization not found.")
    return crud.delete_organization(db=db, organization_id=organization_id)


# Endpoint to Get all Teams
@router.get("/teams/", response_model=list[schemas.Team])
async def get_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_teams(db=db, skip=skip, limit=limit)


# Endpoint to Update a Team
@router.put("/teams/{team_id}", response_model=schemas.Team)
async def update_team(
    team_id: int,
    team: schemas.TeamUpdate,
    db: Session = Depends(get_db),
):
    db_team = crud.update_team(db=db, team_id=team_id, team=team)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found.")
    return db_team


# Endpoint to Delete a Team
@router.delete("/teams/{team_id}", response_model=schemas.Team)
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    if not crud.get_team(db=db, team_id=team_id):
        raise HTTPException(status_code=404, detail="Team not found.")
    return crud.delete_team(db=db, team_id=team_id)


# Endpoint to Get all Agents
@router.get("/agents/", response_model=list[schemas.Agent])
async def get_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_agents(db=db, skip=skip, limit=limit)


# Endpoint to Update an Agent
@router.put("/agents/{agent_id}", response_model=schemas.Agent)
async def update_agent(
    agent_id: int,
    agent: schemas.AgentUpdate,
    db: Session = Depends(get_db),
):
    db_agent = crud.update_agent(db=db, agent_id=agent_id, agent=agent)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found.")
    return db_agent


# Endpoint to Delete an Agent
@router.delete("/agents/{agent_id}", response_model=schemas.Agent)
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    if not crud.get_agent(db=db, agent_id=agent_id):
        raise HTTPException(status_code=404, detail="Agent not found.")
    return crud.delete_agent(db=db, agent_id=agent_id)


# Endpoint to Get All Chat Histories
@router.get("/chat_histories/", response_model=List[schemas.ChatHistory])
async def get_chat_histories(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_chat_histories(db=db, skip=skip, limit=limit)


# Endpoint to Update a Chat History
@router.put("/chat_histories/{chat_history_id}", response_model=schemas.ChatHistory)
async def update_chat_history(
    chat_history_id: int,
    chat_history: schemas.ChatHistoryUpdate,
    db: Session = Depends(get_db),
):
    db_chat_history = crud.update_chat_history(
        db=db, chat_history_id=chat_history_id, chat_history=chat_history
    )
    if db_chat_history is None:
        raise HTTPException(status_code=404, detail="Chat History not found.")
    return db_chat_history


# Endpoint to Delete a Chat History
@router.delete("/chat_histories/{chat_history_id}", response_model=schemas.ChatHistory)
async def delete_chat_history(chat_history_id: int, db: Session = Depends(get_db)):
    if not crud.get_chat_history(db=db, chat_history_id=chat_history_id):
        raise HTTPException(status_code=404, detail="Chat History not found.")
    return crud.delete_chat_history(db=db, chat_history_id=chat_history_id)
