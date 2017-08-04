from datetime import datetime
from typing import Iterable, Union

from asyncqlio.db import DatabaseInterface

from pantsuBooru.backend.exceptions import TagExists
from pantsuBooru.models import Image, Tag, User


class ImageDB:
    def __init__(self, db: DatabaseInterface):
        self.db = db

    # TODO: Create objects for images that implement add_tag, etc and have methods
    #       that would return the model objects instead return these with the db instace loaded

    async def add_image(self, author: str, source: str, poster: User, tags: Iterable[str]) -> Image:
        """Add an image.

        :param author: The author of the image.
        :param source: The source url of the image.
        :param poster: User object that posted the image.
        :param tags: List of tags to insert with the image.

        :return: The :class:`pantsuBooru.models.Image` object inserted into the database.
        """
        image = Image(
            posted_at=datetime.utcnow(),
            author=author,
            source=source,
            poster=poster.id)

        async with self.db.get_session() as s:
            q = s.insert.add_row(image)
            [image] = await q  # unsure
            tags = (Tag(image_id=image.id, tag=i.lower()) for i in tags)
            q = s.insert.rows(*tags)
            print(q.generate_sql())
            await q.run()

        return image

    async def add_tag(self, image: Union[Image, int], tag: str):
        """Insert a tag onto an image.

        :param image: Either a :class:`pantsuBooru.models.Image` object to add the tag to, or the id of the image.
        :param tag: The tag to add to the image.
        """
        tag = tag.lower()

        if isinstance(image, Image):
            id = image.id
        else:
            id = image

        async with self.db.get_session() as s:
            q = s.select(Tag).where((Tag.tag == tag) &
                                    (Tag.image_id == id))
            print(q.generate_sql())
            if (await q.first()):
                raise TagExists

            q = s.insert.add_row(Tag(image_id=id, tag=tag))
            print(q.generate_sql())
            await q.run()
