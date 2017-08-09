from datetime import datetime
from typing import Iterable

from pantsuBooru.backend.exceptions import TagExists
from pantsuBooru.models import Image, Tag, User, Comment

from .utils import BaseDatabase


class ImageDB(BaseDatabase):
    async def add_image(self,
                        author: str,
                        source: str,
                        user_id: int,
                        tags: Iterable[str]) -> Image:
        """Add an image.

        :param author: The author of the image.
        :param source: The source url of the image.
        :param user_id: ID of user that posted the image.
        :param tags: List of tags to insert with the image.

        :return: The :class:`pantsuBooru.models.Image` object inserted into the database.
        """
        image = Image(
            posted_at=datetime.utcnow(),
            author=author,
            source=source,
            poster=user_id)

        async with self.db.get_session() as s:
            q = s.insert.add_row(image)
            [image] = await q  # unsure
            tags = (Tag(image_id=image.id, tag=i.lower()) for i in tags)
            q = s.insert.rows(*tags)
            await q.run()

        return image

    async def get_image(self, image_id: int) -> Image:
        """Retrieve an image from the database.

        :param image_id: ID of image to fetch.

        :return: The :class:`pantsuBooru.models.Image` fetched.
        """
        async with self.db.get_session() as s:
            return await s.select(Image).where(Image.id == image_id).first()

    async def delete_image(self, image_id: int) -> Image:
        """Delete an image.

        :param image_id: ID of image to delete.
        """
        async with self.db.get_session() as s:
            return await s.remove(Image(id=image_id))

    async def add_tags(self, image_id: int, *tags: str) -> [Tag]:
        """Insert multiple tags onto an image.

        Ignores tag if it already exists on an image.
        Note: This is expensive as it requires querying for existing tags and removing duplicates.

        :param image_id: ID of image to add tags to.
        :param tags: Iterable of strings to add.

        :return: List of added tags.
        """
        # NOTE: I hope there is a better way to do this
        tags = map(str.lower, tags)
        already_has = (i.tag for i in (await self.get_image(image_id)).tags)

        no_dupes = set(tags) - set(already_has)

        tags = (Tag(image_id=image_id, tag=i) for i in no_dupes)

        async with self.db.get_session() as s:
            q = s.insert
            q.rows(*tags)
            return await q.run()

    async def add_tag(self, tag: Tag):
        """Insert a tag onto an image.

        :param tag: The tag to add to the image.

        :raises TagExists: If the tag already exists.
        """
        async with self.db.get_session() as s:
            q = s.select(Tag)
            q.add_condition(Tag.image_id == tag.image_id)
            q.add_condition(Tag.tag == tag.tag)
            if (await q.first()):
                raise TagExists

            q = s.insert.add_row(tag)
            [tag] = await q.run()
            return tag

    async def delete_tag(self, tag_id: int) -> Tag:
        """Delete a tag from an image.

        :param tag_id: ID of the tag to delete.
        :return: The :class:`pantsuBooru.models.Tag` that was deleted.
        """
        async with self.db.get_session() as s:
            return await s.remove(Tag(id=tag_id))

    async def add_comment(self, image_id: int, user_id: int,
                          comment: str) -> Comment:
        """Add a comment to an image.

        :param image: ID of the image to add the tag to.
        :param user: ID of the user that added the comment.
        :param comment: The comment string.

        :return: The comment that was added.
        """
        async with self.db.get_session() as s:
            comment = Comment(image_id=image_id, poster=user_id, text=comment)
            q = s.insert.add_row(comment)
            [comment] = await q.run()
            return comment

    async def delete_comment(self, comment_id: int) -> Comment:
        """Delete a comment.

        :param comment_id: ID of the comment to delete.

        :return: The :class:`pantsuBooru.models.Comment` that was deleted.
        """
        async with self.db.get_session() as s:
            return await s.remove(Comment(id=comment_id))
