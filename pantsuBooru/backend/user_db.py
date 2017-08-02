from datetime import datetime

from asyncqlio.db import DatabaseInterface
from passlib.hash import bcrypt

from pantsuBooru.backend.exceptions import UserExists
from pantsuBooru.models.user_models import User


class UserDB:
    def __init__(self, db: DatabaseInterface):
        self.db = db

    async def create_user(self, username: str, email: str, password: str):
        async with self.db.get_session() as s:
            q = s.select(User).where((User.email == email) |
                                     (User.username == username))
            if (await q.first()):
                raise UserExists

        pass_hash = bcrypt.hash(password)  # use defaults idk

        user = User(
            joined_at=datetime.utcnow(),
            username=username,
            email=email,
            password_hash=pass_hash
        )

        async with self.db.get_session() as s:
            q = s.insert
            q.add_row(user)
            await q
