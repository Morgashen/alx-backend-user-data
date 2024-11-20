#!/usr/bin/env python3
"""
Authentication module for user registration, session management,
and password reset functionality.
"""
import bcrypt
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4
from typing import Union, Optional


def hash_password(password: str) -> bytes:
    """
    Generate a secure hash for the given password.

    Args:
        password (str): Plain text password to be hashed

    Returns:
        bytes: Securely hashed password
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def generate_uuid() -> str:
    """
    Generate a unique identifier.

    Returns:
        str: Unique UUID as a string
    """
    return str(uuid4())


class Auth:
    """
    Authentication class to manage user authentication and session processes.
    """

    def __init__(self):
        """
        Initialize the Auth class with a database connection.
        """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Register a new user in the database.

        Args:
            email (str): User's email address
            password (str): User's password

        Returns:
            User: Newly created user object

        Raises:
            ValueError: If user with the email already exists
        """
        try:
            # Check if user already exists
            self._db.find_user_by(email=email)
        except NoResultFound:
            # Add new user if not found
            return self._db.add_user(email, hash_password(password))

        # If user exists, raise an error
        raise ValueError(f'User {email} already exists')

    def valid_login(self, email: str, password: str) -> bool:
        """
        Validate user login credentials.

        Args:
            email (str): User's email address
            password (str): User's password

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            user = self._db.find_user_by(email=email)
            return bcrypt.checkpw(
                password.encode('utf-8'),
                user.hashed_password
            )
        except NoResultFound:
            return False

    def create_session(self, email: str) -> Optional[str]:
        """
        Create a new session for the user.

        Args:
            email (str): User's email address

        Returns:
            Optional[str]: Session ID or None if user not found
        """
        try:
            user = self._db.find_user_by(email=email)
            user.session_id = generate_uuid()
            self._db.update_user(user.id, session_id=user.session_id)
            return user.session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(
            self,
            session_id: Optional[str]
    ) -> Optional[User]:
        """
        Retrieve user by session ID.

        Args:
            session_id (Optional[str]): Session identifier

        Returns:
            Optional[User]: User object or None if not found
        """
        if not session_id:
            return None

        try:
            return self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None

    def destroy_session(self, user_id: str) -> None:
        """
        Destroy user's current session.

        Args:
            user_id (str): User's unique identifier
        """
        try:
            self._db.update_user(user_id, session_id=None)
        except (NoResultFound, ValueError):
            return None

    def get_reset_password_token(self, email: str) -> str:
        """
        Generate a password reset token for a user.

        Args:
            email (str): User's email address

        Returns:
            str: Generated reset token

        Raises:
            ValueError: If user is not found
        """
        try:
            user = self._db.find_user_by(email=email)
            reset_token = generate_uuid()
            self._db.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError("User not found")

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Update user's password using reset token.

        Args:
            reset_token (str): Password reset token
            password (str): New password

        Raises:
            ValueError: If reset token is invalid
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed_pw = hash_password(password)
            self._db.update_user(
                user.id,
                hashed_password=hashed_pw,
                reset_token=None
            )
        except NoResultFound:
            raise ValueError("Invalid reset token")
