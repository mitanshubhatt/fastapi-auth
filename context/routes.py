from fastapi import APIRouter

from context.views import (
    switch_organization, switch_team, switch_context,
    get_current_context, get_available_contexts
)

router = APIRouter(prefix="/rbac/context", tags=["Context"])

# Context switching routes
router.add_api_route("/switch-organization", endpoint=switch_organization, methods=["POST"])
router.add_api_route("/switch-team", endpoint=switch_team, methods=["POST"])
router.add_api_route("/switch-context", endpoint=switch_context, methods=["POST"])

# Context information routes
router.add_api_route("/current", endpoint=get_current_context, methods=["GET"])
router.add_api_route("/available", endpoint=get_available_contexts, methods=["GET"]) 