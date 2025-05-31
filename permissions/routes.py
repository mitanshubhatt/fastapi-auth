from fastapi import APIRouter

from permissions.views import (
    get_all_permissions, get_permission_by_id, get_permission_by_name,
    get_permissions_by_role, get_permissions_by_scope,
    create_permission, update_permission, delete_permission,
    assign_permission_to_role, remove_permission_from_role,
    refresh_permissions_cache_endpoint, get_cached_permissions_endpoint
)

router = APIRouter(prefix="/rbac/permissions", tags=["Permissions"])

# Permission CRUD routes
router.add_api_route("/", endpoint=get_all_permissions, methods=["GET"])
router.add_api_route("/{permission_id}", endpoint=get_permission_by_id, methods=["GET"])
router.add_api_route("/name/{name}", endpoint=get_permission_by_name, methods=["GET"])
router.add_api_route("/", endpoint=create_permission, methods=["POST"])
router.add_api_route("/{permission_id}", endpoint=update_permission, methods=["PUT"])
router.add_api_route("/{permission_id}", endpoint=delete_permission, methods=["DELETE"])

# Permission filtering routes
router.add_api_route("/role/{role_id}", endpoint=get_permissions_by_role, methods=["GET"])
router.add_api_route("/scope/{scope}", endpoint=get_permissions_by_scope, methods=["GET"])

# Role-Permission assignment routes
router.add_api_route("/assign/{role_id}/{permission_id}", endpoint=assign_permission_to_role, methods=["POST"])
router.add_api_route("/remove/{role_id}/{permission_id}", endpoint=remove_permission_from_role, methods=["DELETE"])

# Cache management routes
router.add_api_route("/cache/refresh", endpoint=refresh_permissions_cache_endpoint, methods=["POST"])
router.add_api_route("/cache", endpoint=get_cached_permissions_endpoint, methods=["GET"]) 