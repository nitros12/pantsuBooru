from datetime import datetime
from typing import Optional

from passlib.hash import bcrypt

from pantsuBooru.backend.exceptions import UserExists
from pantsuBooru.models import User, Comment, Image

from .utils import BaseDatabase, make_comp_search


class UserDB(BaseDatabase):
    def hash_password(self, password: str):
        """Hash a password with bcrypt.

        This function returns a coroutine.
        """
        return self.loop.run_in_executor(None, bcrypt.hash, password)

    async def create_user(self, username: str, email: str,
                          password: str) -> User:
        """Create a user.

        :param username: The username of the user.
        :param email: The email address of the user.
        :param password: The users password.

        :raises UserExists: If either username or email already exists in the database.

        :return: The :class:`pantsuBooru.models.User` object inserted.
        """
        condition = make_comp_search(User, username=username, email=email)

        if await self.get_user(username=username, email=email):
            raise UserExists

        user = User(
            joined_at=datetime.utcnow(),
            username=username,
            email=email,
            password=await self.hash_password(password))

        async with self.db.get_session() as s:
            q = s.insert
            q.add_row(user)
            [user] = await q.run()

        return user

    async def reset_password(self, *, user_id: int, password: str):
        """Reset the password of a user object.

        :param user_id: ID of the user to reset the password of.
        :param password: The password to reset to.
        """
        hash = await self.hash_password(password)
        user.password = hash

        async with self.db.get_session() as s:
            return await s.merge(user)

    async def get_user(self,
                       *,
                       username: str=None,
                       email: str=None,
                       id: int=None) -> Optional[User]:
        """Get a user object by username, email or id.

        Atleast one parameter must be passed.

        :param usename: Username of user to get.
        :param email: Email of user to get.
        :param id: Id of user to get.

        :return: The :class:`pantsuBooru.models.User` object found.
        """
        condition = make_comp_search(
            User, username=username, email=email, id=id)

        async with self.db.get_session() as s:
            q = s.select(User)
            q.add_condition(condition)
            return await q.first()

    async def delete_user(self, user_id: int) -> User:
        """Delete a user and also delete their corresponding images and comments.

        :param user_id: ID of the user object to delete.
        """
        async with self.db.get_session() as s:
            return await s.remove(User(id=user_id))
