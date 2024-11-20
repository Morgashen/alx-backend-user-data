#!/usr/bin/env python3
"""
Integration test module for authentication web service.
"""
import requests

BASE_URL = 'http://0.0.0.0:5000'

def register_user(email: str, password: str) -> None:
    """Register a new user."""
    response = requests.post(f'{BASE_URL}/users', data={
        'email': email, 
        'password': password
    })
    assert response.status_code == 201, "User registration failed"
    assert response.json() == {"email": email, "message": "user created"}

def log_in_wrong_password(email: str, password: str) -> None:
    """Attempt login with incorrect password."""
    response = requests.post(f'{BASE_URL}/sessions', data={
        'email': email, 
        'password': password
    })
    assert response.status_code == 401, "Incorrect login should be rejected"

def log_in(email: str, password: str) -> str:
    """Perform successful login."""
    response = requests.post(f'{BASE_URL}/sessions', data={
        'email': email, 
        'password': password
    })
    assert response.status_code == 200
    assert 'session_id' in response.cookies
    return response.cookies['session_id']

def profile_unlogged() -> None:
    """Check profile access without logging in."""
    response = requests.get(f'{BASE_URL}/profile')
    assert response.status_code == 403, "Unlogged profile access should be forbidden"

def profile_logged(session_id: str) -> None:
    """Check profile access after logging in."""
    response = requests.get(f'{BASE_URL}/profile', 
                             cookies={'session_id': session_id})
    assert response.status_code == 200
    assert 'email' in response.json()

def log_out(session_id: str) -> None:
    """Logout and verify."""
    response = requests.delete(f'{BASE_URL}/sessions', 
                                cookies={'session_id': session_id})
    assert response.status_code == 200

def reset_password_token(email: str) -> str:
    """Get password reset token."""
    response = requests.post(f'{BASE_URL}/reset_password', 
                              data={'email': email})
    assert response.status_code == 200
    return response.json()['reset_token']

def update_password(email: str, reset_token: str, new_password: str) -> None:
    """Update user password."""
    response = requests.put(f'{BASE_URL}/reset_password', data={
        'email': email,
        'reset_token': reset_token,
        'new_password': new_password
    })
    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "Password updated"}

EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"

if __name__ == "__main__":
    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
