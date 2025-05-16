from fastapi import APIRouter

from teams.views import create_team, assign_user_to_team, remove_user_from_team

router = APIRouter(prefix="/teams", tags=["Teams"])

router.add_api_route("/create", endpoint=create_team, methods=["POST"])
router.add_api_route("/{team_id}/assign-user", endpoint=assign_user_to_team, methods=["POST"])
router.add_api_route("/{team_id}/remove-user", endpoint=remove_user_from_team, methods=["POST"])
