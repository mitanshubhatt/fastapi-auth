from fastapi import APIRouter

from organizations.views import create_organization, assign_user_to_organization

router = APIRouter(prefix="/rbac/organizations", tags=["Organizations"])

router.add_api_route("/create", endpoint=create_organization, methods=["POST"])
router.add_api_route("/assign-user", endpoint=assign_user_to_organization, methods=["POST"])