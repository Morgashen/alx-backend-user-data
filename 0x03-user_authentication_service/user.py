#!/usr/bin/env python3
"""
SQLAlchemy User model definition for the users table.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    User model representing the users table in the database.

    Attributes:
        id (int): Primary key for the user.
        email (str): User's email address (non-nullable).
hashed_password (str): Hashed password for user authentication (non-nullable).
        session_id (str, optional): Current session identifier (nullable).
        reset_token (str, optional): Token for password reset (nullable).
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250), nullable=True)
    reset_token = Column(String(250), nullable=True)
