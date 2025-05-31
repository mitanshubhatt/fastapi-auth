# roles/routes.py

from fastapi import APIRouter

from roles.views import (
    create_role, get_role_by_id, get_role_by_slug, get_all_roles,
    update_role, delete_role, assign_permission_to_role, remove_permission_from_role
)

router = APIRouter(prefix="/rbac/roles", tags=["Roles"])

# Role CRUD routes
router.add_api_route("/", endpoint=create_role, methods=["POST"])
router.add_api_route("/", endpoint=get_all_roles, methods=["GET"])
router.add_api_route("/{role_id}", endpoint=get_role_by_id, methods=["GET"])
router.add_api_route("/slug/{slug}", endpoint=get_role_by_slug, methods=["GET"])
router.add_api_route("/{role_id}", endpoint=update_role, methods=["PUT"])
router.add_api_route("/{role_id}", endpoint=delete_role, methods=["DELETE"])

# Role-Permission assignment routes
router.add_api_route("/{role_id}/permissions/{permission_id}", endpoint=assign_permission_to_role, methods=["POST"])
router.add_api_route("/{role_id}/permissions/{permission_id}", endpoint=remove_permission_from_role, methods=["DELETE"])


