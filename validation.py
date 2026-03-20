"""Authentication and validation module for DeckSmith."""

import logging
import os
import re
from typing import Optional

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DJANGO_BACKEND_URL: Optional[str] = os.getenv("DJANGO_BACKEND_URL")
API_KEY: Optional[str] = os.getenv("API_KEY")
FRONTENDURL: Optional[str] = os.getenv("FRONTENDURL")
DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"

REQUEST_TIMEOUT: int = 30


def sanitize_input(value: str) -> str:
    """Sanitize input by removing potentially dangerous characters.

    Args:
        value: The input string to sanitize.

    Returns:
        A sanitized string with control characters removed.
    """
    if not value:
        return ""
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    return value.strip()


def authenticate_session() -> bool:
    """Authenticate the user session using token, session cookie, or API key.

    Returns:
        True if authentication is successful, False otherwise.
    """
    token: Optional[str] = st.session_state.get('auth_token', None)
    session_cookie: Optional[str] = st.session_state.get('sessionid', None)
    api_key: Optional[str] = st.session_state.get('api_key', None)

    if DEBUG_MODE:
        logger.debug("Session token: %s", token[:10] + "..." if token else None)
        logger.debug("Session cookie: %s", session_cookie[:10] + "..." if session_cookie else None)

    if api_key and API_KEY and api_key == API_KEY:
        logger.info("Authenticated via API key")
        return True

    if token:
        token = sanitize_input(token)
        headers = {'Authorization': f'Token {token}'}
        logger.debug("Attempting token authentication")
        try:
            response = requests.get(
                f'{DJANGO_BACKEND_URL}/api/dj-rest-auth/user/',
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            logger.debug("Token authentication response status: %s", response.status_code)
            if response.status_code == 200:
                return True
            else:
                st.session_state['auth_token'] = None
        except requests.RequestException as e:
            logger.error("Token authentication request failed: %s", e)
            st.session_state['auth_token'] = None

    if session_cookie:
        session_cookie = sanitize_input(session_cookie)
        cookies = {'sessionid': session_cookie}
        try:
            response = requests.get(
                f'{DJANGO_BACKEND_URL}/api/dj-rest-auth/user/',
                cookies=cookies,
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                return True
            else:
                st.session_state['sessionid'] = None
        except requests.RequestException as e:
            logger.error("Session cookie authentication request failed: %s", e)
            st.session_state['sessionid'] = None

    return False

def validate_credentials() -> bool:
    """Validate user credentials from query parameters and session state.

    Returns:
        True if credentials are valid, False otherwise.
    """
    token: Optional[str] = None
    sessionid: Optional[str] = None
    api_key: Optional[str] = None

    if st.session_state.get("auth_checked", None) is None:
        if st.query_params:
            token = st.query_params.get('token')
            sessionid = st.query_params.get('sessionid')
            api_key = st.query_params.get('api_key')

            if DEBUG_MODE:
                logger.debug("Query params received for authentication")

        if token:
            st.session_state['auth_token'] = sanitize_input(token)
        if sessionid:
            st.session_state['sessionid'] = sanitize_input(sessionid)
        if api_key:
            st.session_state['api_key'] = sanitize_input(api_key)

        st.session_state["auth_checked"] = True

    return authenticate_session()