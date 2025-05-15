from fastapi import APIRouter


router = APIRouter(prefix="/rbac/teams", tags=["Teams"])

router.add_api_route("/create", endpoint=create_team, methods=["POST"])
router.add_api_route("/assign-user", endpoint=assign_user_to_team, methods=["POST"])
router.add_api_route("/remove-user", endpoint=remove_user_from_team, methods=["POST"])
