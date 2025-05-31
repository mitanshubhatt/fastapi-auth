from datetime import timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from context.schemas import (
    SwitchOrganizationRequest, SwitchTeamRequest, SwitchContextRequest,
    TokenResponse, CurrentContextResponse, AvailableContextsResponse
)
from context.services import ContextService, extract_context_from_token
from db.pg_connection import get_db
from auth.dependencies import get_current_user, get_current_user_token_payload
from auth.models import User
from config.settings import settings
from utils.custom_logger import logger


async def switch_organization(
    request: SwitchOrganizationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Switch user's active organization and return a new enriched token
    """
    try:
        context_service = ContextService(db)
        
        # Validate user has access to the organization
        has_access = await context_service.validate_user_access_to_organization(
            current_user.id, request.organization_id
        )
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this organization"
            )
        
        # Create new token with the organization context
        new_token = await context_service.create_new_token_with_context(
            user_email=current_user.email,
            organization_id=request.organization_id,
            team_id=None  # Reset team when switching orgs
        )
        
        # Get context info for response
        payload = await settings.auth_instance.verify_token(new_token)
        context = extract_context_from_token(payload)
        
        logger.info(f"User {current_user.email} switched to organization {request.organization_id}")
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            context=context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching organization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch organization"
        )


async def switch_team(
    request: SwitchTeamRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Switch user's active team and return a new enriched token
    """
    try:
        context_service = ContextService(db)
        
        # Validate user has access to the team
        has_access = await context_service.validate_user_access_to_team(
            current_user.id, request.team_id
        )
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this team"
            )
        
        # Get the team's organization ID
        team = await context_service.dao.get_team_by_id(request.team_id)
        
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Create new token with the team context
        new_token = await context_service.create_new_token_with_context(
            user_email=current_user.email,
            organization_id=team.organization_id,
            team_id=request.team_id
        )
        
        # Get context info for response
        payload = await settings.auth_instance.verify_token(new_token)
        context = extract_context_from_token(payload)
        
        logger.info(f"User {current_user.email} switched to team {request.team_id}")
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            context=context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch team"
        )


async def switch_context(
    request: SwitchContextRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Switch user's active context (both organization and team) and return a new enriched token
    """
    try:
        context_service = ContextService(db)
        
        # Validate access to organization if provided
        if request.organization_id:
            has_org_access = await context_service.validate_user_access_to_organization(
                current_user.id, request.organization_id
            )
            if not has_org_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this organization"
                )
        
        # Validate access to team if provided
        if request.team_id:
            has_team_access = await context_service.validate_user_access_to_team(
                current_user.id, request.team_id
            )
            if not has_team_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this team"
                )
            
            # If team is provided, ensure it belongs to the organization
            if request.organization_id:
                team_belongs = await context_service.validate_team_belongs_to_organization(
                    request.team_id, request.organization_id
                )
                if not team_belongs:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Team does not belong to the specified organization"
                    )
        
        # Create new token with the specified context
        new_token = await context_service.create_new_token_with_context(
            user_email=current_user.email,
            organization_id=request.organization_id,
            team_id=request.team_id
        )
        
        # Get context info for response
        payload = await settings.auth_instance.verify_token(new_token)
        context = extract_context_from_token(payload)
        
        logger.info(f"User {current_user.email} switched context - org: {request.organization_id}, team: {request.team_id}")
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            context=context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch context"
        )


async def get_current_context(
    current_user_token_payload: dict = Depends(get_current_user_token_payload)
) -> CurrentContextResponse:
    """
    Get the current context information from the token
    """
    try:
        context_service = ContextService(None)  # No DB needed for this operation
        return await context_service.get_current_context(current_user_token_payload)
        
    except Exception as e:
        logger.error(f"Error getting current context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get current context"
        )


async def get_available_contexts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AvailableContextsResponse:
    """
    Get all available contexts (organizations and teams) for the current user
    """
    try:
        context_service = ContextService(db)
        return await context_service.get_available_contexts(current_user.id)
        
    except Exception as e:
        logger.error(f"Error getting available contexts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available contexts"
        ) 