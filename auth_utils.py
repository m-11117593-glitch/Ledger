import urllib.parse
import requests
import streamlit as st

def get_oauth_config():
    """Retrieves Google OAuth client ID, secret, and redirect URI from secrets."""
    client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
    client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = st.secrets.get("REDIRECT_URI", "http://localhost:8501")
    return client_id, client_secret, redirect_uri

def get_google_auth_url() -> str:
    """Generates the official Google OAuth 2.0 authorization URL."""
    client_id, _, redirect_uri = get_oauth_config()
    if not client_id:
        return ""
        
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

def exchange_code_for_user(code: str) -> dict:
    """
    Exchanges authorization code for Google access token and fetches verified profile.
    Returns:
        dict: {"email": str, "name": str, "picture": str, "success": bool, "error": str}
    """
    client_id, client_secret, redirect_uri = get_oauth_config()
    token_url = "https://oauth2.googleapis.com/token"
    
    token_payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    try:
        token_res = requests.post(token_url, data=token_payload, timeout=10)
        token_data = token_res.json()
        
        if "access_token" not in token_data:
            err_msg = token_data.get("error_description", token_data.get("error", "Failed to retrieve access token."))
            return {"success": False, "error": err_msg}
            
        access_token = token_data["access_token"]
        
        # Query verified userinfo endpoint
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_res = requests.get(userinfo_url, headers=headers, timeout=10)
        user_data = user_res.json()
        
        email = user_data.get("email")
        if not email:
            return {"success": False, "error": "No email returned from Google account."}
            
        return {
            "success": True,
            "email": email.strip().lower(),
            "name": user_data.get("name", email),
            "picture": user_data.get("picture", ""),
            "email_verified": user_data.get("email_verified", True)
        }
    except Exception as e:
        return {"success": False, "error": f"OAuth connection error: {str(e)}"}
