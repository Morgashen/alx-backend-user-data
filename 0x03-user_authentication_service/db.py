#!/usr/bin/env python3
"""
Database management module for user authentication and operations.

This module provides a DB class for interacting with a SQLite database,
handling user-related database operations using SQLAlchemy ORM.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

from user import Base, User


class DB:

    """
    Database management class for user operations.

    Provides methods to add, find, and update user records in the database.
    Uses SQLAlchemy for database interactions with a SQLite backend.
    """

    def __init__(self) -> None:
        """
        Initialize a new database instance.

        Creates a SQLite engine, drops existing tables,
        and prepares for new table creation.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """
        Provide a memoized database session.

        Returns:
            Session: A SQLAlchemy database session, created if not existing.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Add a new user to the database.

        Args:
            email (str): User's email address
            hashed_password (str): Securely hashed password

        Returns:
            User: The newly created and saved user object
        """
        try:
            new_user = User(email=email, hashed_password=hashed_password)
            self._session.add(new_user)
            self._session.commit()
            return new_user
        except Exception as e:
            self._session.rollback()
            raise ValueError(f"Failed to add user: {str(e)}")

    def find_user_by(self, **kwargs) -> User:
        """
        Find a user in the database by given search criteria.

        Args:
            **kwargs: Arbitrary keyword arguments to filter the user query

        Returns:
            User: The first user matching the given criteria

        Raises:
            InvalidRequestError: If no search criteria are provided
            NoResultFound: If no user matches the search criteria
        """
        if not kwargs:
            raise InvalidRequestError("No search criteria provided")

        try:
            user = self._session.query(User).filter_by(**kwargs).first()
            if not user:
                raise NoResultFound("No user found with given criteria")
            return user
        except (InvalidRequestError, NoResultFound):
            raise
        except Exception as e:
            raise ValueError(f"Error searching for user: {str(e)}")

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update a user's attributes in the database.

        Args:
            user_id (int): ID of the user to update
            **kwargs: Arbitrary keyword arguments to update user attributes

        Raises:
            ValueError: If an invalid attribute is passed or update fails
        """
        try:
            user = self.find_user_by(id=user_id)

            for key, value in kwargs.items():
                if not hasattr(User, key):
                    raise ValueError(f"Invalid user attribute: {key}")
                setattr(user, key, value)

            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise ValueError(f"Failed to update user: {str(e)}")
