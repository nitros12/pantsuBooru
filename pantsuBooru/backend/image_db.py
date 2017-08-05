from datetime import datetime
from typing import Iterable

from asyncqlio.orm.operators import And

from pantsuBooru.backend.exceptions import TagExists
from pantsuBooru.models import Image, Tag, User

from .utils import BaseDatabase, make_comp_search


class ImageDB(BaseDatabase):

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
            await q.run()

        return image

    async def delete_image(self, image_id: int):
        """Delete an image.

        :param image_id: ID of image to delete.
        """
        async with self.db.get_session() as s:
            q = s.delete(Image)
            q.add_condition(Image.id == image_id)
            await q.run()

    async def add_tags(self, image_id: int, *tags: str) -> [Tag]:
        """Insert multiple tags onto an image.

        Ignores tag if it already exists on an image.
        Note: This is expensive as it requires querying for existing tags and removing duplicates.

        :param image_id: ID of the image to add the tags to.
        :param tags: Iterable of strings to add.

        :returns int: Number of tags added.
        """
        # NOTE: I hope there is a better way to do this
        tags = map(str.lower, tags)
        already_has = (i.tag for i in (await self.get_tags(image_id)))

        no_dupes = set(tags) - set(already_has)

        tags = (Tag(image_id=image_id, tag=i) for i in no_dupes)

        async with self.db.get_session() as s:
            q = s.insert
            q.rows(*tags)
            return await q.run()

    async def get_tags(self, image_id: int) -> [Tag]:
        """Get the tags on an image.

        :param image_id: ID of image to get tags from.
        """
        async with self.db.get_session() as s:
            q = s.select(Tag)
            q.add_condition(Tag.image_id == image_id)
            res = await q.all()
            return await res.flatten()

    async def add_tag(self, image_id: int, tag: str):
        """Insert a tag onto an image.

        :param image_id: ID of the image to add the tag to.
        :param tag: The tag to add to the image.

        :raises TagExists: If the tag already exists.
        """
        tag = tag.lower()
        condition = make_comp_search(Tag, join_op=And, image_id=image_id, tag=tag)

        async with self.db.get_session() as s:
            q = s.select(Tag)
            q.add_condition(condition)
            if (await q.first()):
                raise TagExists

            q = s.insert.add_row(Tag(image_id=image_id, tag=tag))
            [tag] = await q.run()
            return tag

    async def delete_tag(self, image_id: int, tag: str):
        """Delete a tag from an image.

        :param image_id: ID of the image to delete the tag from.
        :param tag: The tag to delete from the image.
        """
        tag = tag.lower()
        condition = make_comp_search(Tag, join_op=And, image_id=image_id, tag=tag)

        async with self.db.get_session() as s:
            q = s.delete(Tag)
            q.add_condition(condition)
            await q.run()
