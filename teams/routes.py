from fastapi import APIRouter

from teams.views import (
    create_team, get_team_by_id, get_user_teams, get_organization_teams,
    get_team_members, update_team, delete_team, assign_user_to_team, remove_user_from_team
)

router = APIRouter(prefix="/rbac/teams", tags=["Teams"])

# Team CRUD routes
router.add_api_route("/", endpoint=create_team, methods=["POST"])
router.add_api_route("/{team_id}", endpoint=get_team_by_id, methods=["GET"])
router.add_api_route("/{team_id}", endpoint=update_team, methods=["PUT"])
router.add_api_route("/{team_id}", endpoint=delete_team, methods=["DELETE"])

# User-Team relationship routes
router.add_api_route("/my-teams", endpoint=get_user_teams, methods=["GET"])
router.add_api_route("/organization/{organization_id}", endpoint=get_organization_teams, methods=["GET"])

# Team member management routes
router.add_api_route("/{team_id}/members", endpoint=get_team_members, methods=["GET"])
router.add_api_route("/{team_id}/members", endpoint=assign_user_to_team, methods=["POST"])
router.add_api_route("/{team_id}/members/{user_email}", endpoint=remove_user_from_team, methods=["DELETE"])
