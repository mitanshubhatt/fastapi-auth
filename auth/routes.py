from fastapi import APIRouter

from auth.views import (
    register_user, login_user, refresh_token, revoke_token, verify_email,
    forgot_password, reset_password, microsoft_login, microsoft_callback,
    google_login, google_callback, github_login, github_callback
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# User authentication routes
router.add_api_route("/register", endpoint=register_user, methods=["POST"])
router.add_api_route("/login", endpoint=login_user, methods=["POST"])
router.add_api_route("/refresh", endpoint=refresh_token, methods=["POST"])
router.add_api_route("/revoke", endpoint=revoke_token, methods=["POST"])
router.add_api_route("/verify-email", endpoint=verify_email, methods=["POST"])
router.add_api_route("/forgot-password", endpoint=forgot_password, methods=["POST"])
router.add_api_route("/reset-password", endpoint=reset_password, methods=["POST"])

# OAuth routes
router.add_api_route("/microsoft", endpoint=microsoft_login, methods=["GET"])
router.add_api_route("/microsoft/callback", endpoint=microsoft_callback, methods=["GET"])
router.add_api_route("/google", endpoint=google_login, methods=["GET"])
router.add_api_route("/google/callback", endpoint=google_callback, methods=["GET"])
router.add_api_route("/github", endpoint=github_login, methods=["GET"])
router.add_api_route("/github/callback", endpoint=github_callback, methods=["GET"]) 