"""
Permission Cache Utility Module

This module provides convenient functions to access cached permissions
without making database calls. Use these functions throughout your application
to get permissions from the in-memory cache instead of hitting the database.
"""

from typing import Dict, List, Optional
from utils.permission_middleware import (
    get_permissions_from_cache, 
    get_role_permissions_from_cache,
    refresh_permissions_cache,
    clear_permissions_cache
)
from utils.custom_logger import logger


def get_user_permissions(role_name: str, scope: str) -> Dict[str, List[str]]:
    """
    Get permissions for a specific user role and scope from cache.
    
    Args:
        role_name: The name of the role (e.g., 'Admin', 'Member', 'Lead')
        scope: The scope of permissions ('organization', 'team', etc.)
    
    Returns:
        Dictionary mapping routes to allowed HTTP methods
        
    Example:
        permissions = get_user_permissions('Admin', 'organization')
        # Returns: {'/rbac/teams': ['GET'], '/rbac/teams/create': ['POST'], ...}
    """
    try:
        role_permissions = get_role_permissions_from_cache(role_name, scope)
        return role_permissions.get("routes", {})
    except Exception as e:
        logger.error(f"Error getting user permissions for role {role_name}, scope {scope}: {e}")
        return {}


def can_user_access_route(role_name: str, scope: str, route: str, method: str) -> bool:
    """
    Check if a user with specific role can access a route with given HTTP method.
    
    Args:
        role_name: The name of the role
        scope: The scope of permissions
        route: The route path (e.g., '/rbac/teams/create')
        method: HTTP method (e.g., 'GET', 'POST')
    
    Returns:
        True if user can access, False otherwise
    """
    try:
        permissions = get_user_permissions(role_name, scope)
        
        # Check for wildcard permissions
        if "*" in permissions:
            return method.upper() in permissions["*"]
        
        # Check specific route permissions
        route_permissions = permissions.get(route, [])
        return method.upper() in route_permissions
    except Exception as e:
        logger.error(f"Error checking route access for {role_name}: {e}")
        return False


def get_all_cached_permissions() -> Dict:
    """
    Get all cached permissions.
    
    Returns:
        Complete permissions dictionary from cache
    """
    return get_permissions_from_cache()


def get_permissions_by_scope(scope: str) -> Dict:
    """
    Get all permissions for a specific scope from cache.
    
    Args:
        scope: The scope to filter by ('organization', 'team', etc.)
    
    Returns:
        Dictionary of roles and their permissions for the given scope
    """
    try:
        all_permissions = get_permissions_from_cache()
        return all_permissions.get(scope, {})
    except Exception as e:
        logger.error(f"Error getting permissions for scope {scope}: {e}")
        return {}


def get_available_roles(scope: str) -> List[str]:
    """
    Get list of available roles for a specific scope.
    
    Args:
        scope: The scope to get roles for
    
    Returns:
        List of role names
    """
    try:
        scope_permissions = get_permissions_by_scope(scope)
        return list(scope_permissions.keys())
    except Exception as e:
        logger.error(f"Error getting available roles for scope {scope}: {e}")
        return []


def get_routes_for_role(role_name: str, scope: str) -> List[str]:
    """
    Get all accessible routes for a specific role and scope.
    
    Args:
        role_name: The name of the role
        scope: The scope of permissions
    
    Returns:
        List of route paths the role can access
    """
    try:
        permissions = get_user_permissions(role_name, scope)
        return list(permissions.keys())
    except Exception as e:
        logger.error(f"Error getting routes for role {role_name}, scope {scope}: {e}")
        return []


async def refresh_cache():
    """
    Refresh the permissions cache from database.
    Async wrapper for the refresh function.
    """
    try:
        await refresh_permissions_cache()
        logger.info("Permissions cache refreshed successfully via utility")
    except Exception as e:
        logger.error(f"Error refreshing permissions cache: {e}")
        raise


def clear_cache():
    """
    Clear the permissions cache.
    """
    try:
        clear_permissions_cache()
        logger.info("Permissions cache cleared successfully via utility")
    except Exception as e:
        logger.error(f"Error clearing permissions cache: {e}")
        raise


# Convenience functions for common permission checks
def is_admin(role_name: str) -> bool:
    """Check if role is an admin role."""
    return role_name.lower() in ['admin', 'super_admin', 'administrator']


def is_super_admin(role_name: str) -> bool:
    """Check if role is super admin."""
    return role_name.lower() == 'super_admin'


def has_wildcard_permissions(role_name: str, scope: str) -> bool:
    """Check if role has wildcard permissions (access to all routes)."""
    permissions = get_user_permissions(role_name, scope)
    return "*" in permissions 