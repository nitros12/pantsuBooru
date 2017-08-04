import asyncio
from datetime import datetime
from typing import Optional

from asyncqlio.db import DatabaseInterface
from asyncqlio.orm.operators import Or
from passlib.hash import bcrypt

from pantsuBooru.backend.exceptions import UserExists
from pantsuBooru.models import User


class UserDB:
    def __init__(self, db: DatabaseInterface, loop=None):
        self.db = db
        self.loop = asyncio.get_event_loop()

    def hash_password(self, password: str):
        """Hash a password with bcrypt.

        This function is a coroutine.
        """
        return self.loop.run_in_executor(None, bcrypt.hash, password)

    async def create_user(self, username: str, email: str, password: str) -> User:
        """Create a user.

        :param username: The username of the user.
        :param email: The email address of the user.
        :param password: The users password.

        :raises UserExists: If either username or email already exists in the database.

        :return: The :class:`pantsuBooru.models.User` object inserted.
        """
        async with self.db.get_session() as s:
            q = s.select(User).where((User.email == email) |
                                     (User.username == username))
            print(q.generate_sql())
            if (await q.first()):
                print("fuck")  # this breaks on getting a foreign key somehow
                raise UserExists

        user = User(
            joined_at=datetime.utcnow(),
            username=username,
            email=email,
            password=await self.hash_password(password)
        )

        async with self.db.get_session() as s:
            q = s.insert
            q.add_row(user)
            [user] = await q.run()

        return user

    def reset_password_user(self, user: User, password: str):
        """Reset the password of a user object.

        :param user: The :class:`pantsuBooru.models.User` object to update.
        :param password: The password to reset to
        """
        return self.reset_password(user.username, user.email, password)

    async def reset_password(self, username: str, email: str, password: str):
        """Reset the password of a user object."""
        async with self.db.get_session() as s:
            q = s.update.table(User)
            q.add_condition((User.username == username) &
                            (User.email == email))
            q.set(User.password, await self.hash_password(password))
            await q.run()

    async def get_user(self, *, username: str=None, email: str=None, id: int=None) -> Optional[User]:
        """Get a user object by username, email or id.

        :param usename: username to request by.
        :param email: email to request by.
        :param id: id to request by.

        :return: The :class:`pantsuBooru.models.User` object found.
        """
        searches = [
            (getattr(User, k) == v) for k, v in dict(
                username=username,
                email=email,
                id=id,
            )
        ]
        if not searches:
            raise Exception("At least one attribute is required to search by")

        async with self.db.get_session() as s:
            q = s.select(User)
            q.add_condition(Or(*searches))
            return await q.first()
