from datetime import datetime

from asyncqlio.db import DatabaseInterface

from pantsuBooru.models.image_models import Image, Tag
from pantsuBooru.models.user_models import User


class BooruDB:
    def __init__(self, db: DatabaseInterface):
        self.db = db

    async def add_image(self, author: str, poster: User, tags: str):
        image = Image(
            posted_at=datetime.utcnow(),
            author=author,
            poster=poster.id)

        tags = (Tag(image_id=image.id, tag=i) for i in tags.split())
        async with self.db.get_session() as s:
            q = s.insert
            q.rows(image, *tags)
            await q
