from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from db.connection import get_db
from RBAC.models import User, Organization, OrganizationUser, Team, TeamMember
from RBAC.schemas import OrganizationCreate, OrganizationRead, TeamCreate, TeamRead

router = APIRouter(prefix="/rbac")

@router.post("/create-organization", response_model=OrganizationRead)
async def create_organization(org: OrganizationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_org = Organization(name=org.name)
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)
    return db_org

@router.post("/assign-user-to-organization")
async def assign_user_to_organization(user_id: int, organization_id: int, role: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = await db.get(User, user_id)
    organization = await db.get(Organization, organization_id)
    if not user or not organization:
        raise HTTPException(status_code=404, detail="User or Organization not found")
    
    org_user = OrganizationUser(user_id=user_id, organization_id=organization_id, role=role)
    db.add(org_user)
    await db.commit()
    return {"message": "User assigned to organization successfully"}

@router.post("/create-team", response_model=TeamRead)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_team = Team(organization_id=team.organization_id, product_id=team.product_id, name=team.name)
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return db_team

@router.post("/assign-user-to-team")
async def assign_user_to_team(user_id: int, team_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = await db.get(User, user_id)
    team = await db.get(Team, team_id)
    if not user or not team:
        raise HTTPException(status_code=404, detail="User or Team not found")
    
    team_member = TeamMember(user_id=user_id, team_id=team_id)
    db.add(team_member)
    await db.commit()
    return {"message": "User assigned to team successfully"}

@router.get("/organization-users/{organization_id}", response_model=list[OrganizationUser])
async def get_organization_users(organization_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await db.execute(select(OrganizationUser).where(OrganizationUser.organization_id == organization_id))
    return result.scalars().all()

@router.get("/team-members/{team_id}", response_model=list[TeamMember])
async def get_team_members(team_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await db.execute(select(TeamMember).where(TeamMember.team_id == team_id))
    return result.scalars().all()
