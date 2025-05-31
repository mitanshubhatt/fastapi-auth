from fastapi import APIRouter

from organizations.views import (
    create_organization, get_organization_by_id, get_user_organizations,
    get_organization_members, update_organization, assign_user_to_organization,
    remove_user_from_organization
)

router = APIRouter(prefix="/rbac/organizations", tags=["Organizations"])

# Organization CRUD routes
router.add_api_route("/", endpoint=create_organization, methods=["POST"])
router.add_api_route("/{organization_id}", endpoint=get_organization_by_id, methods=["GET"])
router.add_api_route("/{organization_id}", endpoint=update_organization, methods=["PUT"])

# User-Organization relationship routes
router.add_api_route("/my-organizations", endpoint=get_user_organizations, methods=["GET"])

# Organization member management routes
router.add_api_route("/{organization_id}/members", endpoint=get_organization_members, methods=["GET"])
router.add_api_route("/{organization_id}/members", endpoint=assign_user_to_organization, methods=["POST"])
router.add_api_route("/{organization_id}/members/{user_id}", endpoint=remove_user_from_organization, methods=["DELETE"])