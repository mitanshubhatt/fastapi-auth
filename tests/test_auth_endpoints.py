import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock
import json

from app.server import app


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""

    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)

    def test_register_user_success(self, client):
        """Test successful user registration"""
        user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890",
            "password": "SecurePass123!"
        }
        
        with patch('auth.services.AuthService.register_user') as mock_register:
            mock_register.return_value = {
                "success": True,
                "message": "User registered successfully",
                "data": {"user_id": 1}
            }
            
            response = client.post("/auth/register", json=user_data)
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["success"] is True
            assert "User registered successfully" in result["message"]

    def test_register_user_invalid_email(self, client):
        """Test user registration with invalid email"""
        user_data = {
            "email": "invalid-email",
            "first_name": "Test",
            "last_name": "User", 
            "phone_number": "+1234567890",
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_weak_password(self, client):
        """Test user registration with weak password"""
        user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890", 
            "password": "weak"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_existing_email(self, client):
        """Test user registration with existing email"""
        user_data = {
            "email": "existing@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890",
            "password": "SecurePass123!"
        }
        
        with patch('auth.services.AuthService.register_user') as mock_register:
            mock_register.side_effect = Exception("User already exists")
            
            response = client.post("/auth/register", json=user_data)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_login_user_success(self, client):
        """Test successful user login"""
        login_data = {
            "username": "test@example.com",
            "password": "SecurePass123!"
        }
        
        with patch('auth.services.AuthService.authenticate_and_create_tokens') as mock_auth:
            mock_auth.return_value = {
                "success": True,
                "message": "Login successful",
                "data": {
                    "access_token": "fake_access_token",
                    "refresh_token": "fake_refresh_token",
                    "token_type": "bearer"
                }
            }
            
            response = client.post("/auth/login", data=login_data)
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["success"] is True
            assert "access_token" in result["data"]
            assert "refresh_token" in result["data"]

    def test_login_user_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        login_data = {
            "username": "test@example.com",
            "password": "wrong_password"
        }
        
        with patch('auth.services.AuthService.authenticate_and_create_tokens') as mock_auth:
            mock_auth.side_effect = Exception("Invalid credentials")
            
            response = client.post("/auth/login", data=login_data)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_refresh_token_success(self, client):
        """Test successful token refresh"""
        with patch('auth.services.AuthService.refresh_user_token') as mock_refresh:
            mock_refresh.return_value = {
                "success": True,
                "message": "Token refreshed successfully",
                "data": {
                    "access_token": "new_access_token",
                    "refresh_token": "same_refresh_token",
                    "token_type": "bearer"
                }
            }
            
            response = client.post("/auth/refresh?refresh_token=valid_refresh_token")
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["success"] is True
            assert "access_token" in result["data"]

    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid token"""
        with patch('auth.services.AuthService.refresh_user_token') as mock_refresh:
            mock_refresh.side_effect = Exception("Invalid token")
            
            response = client.post("/auth/refresh?refresh_token=invalid_token")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_revoke_token_success(self, client):
        """Test successful token revocation"""
        with patch('auth.services.AuthService.revoke_user_token') as mock_revoke:
            mock_revoke.return_value = {
                "success": True,
                "message": "Token revoked successfully"
            }
            
            response = client.post("/auth/revoke?refresh_token=valid_refresh_token")
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["success"] is True
            assert "revoked successfully" in result["message"]

    def test_verify_email_success(self, client):
        """Test successful email verification"""
        with patch('auth.services.AuthService.verify_user_email') as mock_verify:
            mock_verify.return_value = {
                "success": True,
                "message": "Email verified successfully"
            }
            
            response = client.post("/auth/verify-email?code=valid_verification_code")
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["success"] is True

    def test_verify_email_invalid_code(self, client):
        """Test email verification with invalid code"""
        with patch('auth.services.AuthService.verify_user_email') as mock_verify:
            mock_verify.side_effect = Exception("Invalid verification code")
            
            response = client.post("/auth/verify-email?code=invalid_code")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_forgot_password_success(self, client):
        """Test successful forgot password request"""
        forgot_data = {"email": "test@example.com"}
        
        with patch('auth.services.AuthService.initiate_password_reset') as mock_forgot:
            mock_forgot.return_value = {
                "success": True,
                "message": "Password reset email sent successfully"
            }
            
            response = client.post("/auth/forgot-password", json=forgot_data)
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["success"] is True

    def test_forgot_password_user_not_found(self, client):
        """Test forgot password with non-existent email"""
        forgot_data = {"email": "nonexistent@example.com"}
        
        with patch('auth.services.AuthService.initiate_password_reset') as mock_forgot:
            mock_forgot.side_effect = Exception("User not found")
            
            response = client.post("/auth/forgot-password", json=forgot_data)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_reset_password_success(self, client):
        """Test successful password reset"""
        reset_data = {
            "code": "valid_reset_code",
            "new_password": "NewSecurePass123!"
        }
        
        with patch('auth.services.AuthService.reset_user_password') as mock_reset:
            mock_reset.return_value = {
                "success": True,
                "message": "Password reset successfully"
            }
            
            response = client.post("/auth/reset-password", json=reset_data)
            
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["success"] is True

    def test_reset_password_invalid_code(self, client):
        """Test password reset with invalid code"""
        reset_data = {
            "code": "invalid_code",
            "new_password": "NewSecurePass123!"
        }
        
        with patch('auth.services.AuthService.reset_user_password') as mock_reset:
            mock_reset.side_effect = Exception("Invalid reset code")
            
            response = client.post("/auth/reset-password", json=reset_data)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_reset_password_weak_password(self, client):
        """Test password reset with weak password"""
        reset_data = {
            "code": "valid_reset_code",
            "new_password": "weak"
        }
        
        response = client.post("/auth/reset-password", json=reset_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # OAuth Tests
    def test_microsoft_login(self, client):
        """Test Microsoft OAuth login initiation"""
        with patch('auth.services.AuthService.handle_microsoft_login') as mock_ms:
            mock_ms.return_value = {"redirect_url": "https://login.microsoftonline.com/..."}
            
            response = client.get("/auth/microsoft")
            assert response.status_code == status.HTTP_200_OK

    def test_microsoft_callback(self, client):
        """Test Microsoft OAuth callback"""
        with patch('auth.services.AuthService.handle_microsoft_callback') as mock_callback:
            mock_callback.return_value = {
                "success": True,
                "message": "Login successful",
                "data": {"access_token": "token", "refresh_token": "refresh", "token_type": "bearer"}
            }
            
            response = client.get("/auth/microsoft/callback?code=auth_code")
            assert response.status_code == status.HTTP_200_OK

    def test_google_login(self, client):
        """Test Google OAuth login initiation"""
        with patch('auth.services.AuthService.handle_google_login') as mock_google:
            mock_google.return_value = {"redirect_url": "https://accounts.google.com/..."}
            
            response = client.get("/auth/google")
            assert response.status_code == status.HTTP_200_OK

    def test_google_callback(self, client):
        """Test Google OAuth callback"""
        with patch('auth.services.AuthService.handle_google_callback') as mock_callback:
            mock_callback.return_value = {
                "success": True,
                "message": "Login successful",
                "data": {"access_token": "token", "refresh_token": "refresh", "token_type": "bearer"}
            }
            
            response = client.get("/auth/google/callback?code=auth_code")
            assert response.status_code == status.HTTP_200_OK

    def test_github_login(self, client):
        """Test GitHub OAuth login initiation"""
        with patch('auth.services.AuthService.handle_github_login') as mock_github:
            mock_github.return_value = {"redirect_url": "https://github.com/login/oauth/..."}
            
            response = client.get("/auth/github")
            assert response.status_code == status.HTTP_200_OK

    def test_github_callback(self, client):
        """Test GitHub OAuth callback"""
        with patch('auth.services.AuthService.handle_github_callback') as mock_callback:
            mock_callback.return_value = {
                "success": True,
                "message": "Login successful", 
                "data": {"access_token": "token", "refresh_token": "refresh", "token_type": "bearer"}
            }
            
            response = client.get("/auth/github/callback?code=auth_code")
            assert response.status_code == status.HTTP_200_OK 