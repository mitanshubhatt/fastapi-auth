# roles/routes.py

from fastapi import APIRouter, status

from roles.views import (
    create_role_view,
    get_role_by_id_view,
    get_role_by_slug_view,
    get_all_roles_view,
    update_role_view,
    delete_role_view
)

router = APIRouter(prefix="/roles", tags=["Roles Management"])

# Using the generic ResponseData for single item create/update/delete as per user's team example
# Using specific RolesListResponseData for list GET operations

router.add_api_route(
    "/",
    endpoint=create_role_view,
    methods=["POST"],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role"
)

router.add_api_route(
    "/",
    endpoint=get_all_roles_view,
    methods=["GET"],
    summary="Get all roles with pagination"
)

router.add_api_route(
    "/{role_id}",
    endpoint=get_role_by_id_view,
    methods=["GET"],
    summary="Get a role by its ID"
)

router.add_api_route(
    "/slug/{slug}",
    endpoint=get_role_by_slug_view,
    methods=["GET"],
    summary="Get a role by its slug"
)


