import requests
import streamlit as st
from functools import wraps
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

DJANGO_BACKEND_URL = os.getenv("DJANGO_BACKEND_URL")
API_KEY = os.getenv("API_KEY")
FRONTENDURL = os.getenv("FRONTENDURL")
def authenticate_session():
    """Authenticate the user session using token, session cookie, or API key."""
    token = st.session_state.get('auth_token', None)
    session_cookie = st.session_state.get('sessionid', None)
    api_key = st.session_state.get('api_key', None)

    # For testing only
    #api_key = API_KEY

    # Debug: Print the current session states
    #st.write(f"Session token: {token}")
    #st.write(f"Session cookie: {session_cookie}")
    #st.write(f"Session API key: {api_key}")

    if api_key and api_key == API_KEY:
        return True

    if token:
        headers = {'Authorization': f'Token {token}'}
        response = requests.get(f'{DJANGO_BACKEND_URL}/api/dj-rest-auth/user/', headers=headers)
        #st.write(f"Token authentication response status: {response.status_code}")
        if response.status_code == 200:
            return True
        else:
            st.session_state['auth_token'] = None  # Clear invalid token

    if session_cookie:
        cookies = {'sessionid': session_cookie}
        response = requests.get(f'{DJANGO_BACKEND_URL}/api/dj-rest-auth/user/', cookies=cookies)
        if response.status_code == 200:
            return True
        else:
            st.session_state['sessionid'] = None  # Clear invalid session

    return False

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if authenticate_session():
            return func(*args, **kwargs)
        else:
            st.warning("You need to be logged in to access this page.")
            login_url = FRONTENDURL  # Replace with your actual login page URL
            st.markdown(f"[Go to Login Page]({login_url})")
            st.stop()
    return wrapper

def validate_credentials():
    token = None
    sessionid = None
    api_key = None

    if st.query_params:
        token = st.query_params.token
        #sessionid = st.query_params.sessionid
        #api_key = st.query_params.api_key

        # Debug: Print the query parameters
        #st.write(f"Query params: {st.query_params}")
        #st.write(f"Token from query params: {token}")
        #st.write(f"Session ID from query params: {sessionid}")
        #st.write(f"API key from query params: {api_key}")

    if token:
        st.session_state['auth_token'] = token

    if sessionid:
        st.session_state['sessionid'] = sessionid

    if api_key:
        st.session_state['api_key'] = api_key

    return authenticate_session()

validate_credentials()