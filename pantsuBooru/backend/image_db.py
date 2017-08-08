from datetime import datetime
from typing import Iterable

from pantsuBooru.backend.exceptions import TagExists
from pantsuBooru.models import Image, Tag, User, Comment

from .utils import BaseDatabase


class ImageDB(BaseDatabase):
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

    async def delete_image(self, image: Image) -> Image:
        """Delete an image.

        :param image: image to delete.
        """
        async with self.db.get_session() as s:
            return await s.remove(image)

    async def add_tags(self, image: Image, *tags: str) -> [Tag]:
        """Insert multiple tags onto an image.

        Ignores tag if it already exists on an image.
        Note: This is expensive as it requires querying for existing tags and removing duplicates.

        :param image: Image to add the tags to.
        :param tags: Iterable of strings to add.

        :return: List of added tags.
        """
        # NOTE: I hope there is a better way to do this
        tags = map(str.lower, tags)
        already_has = (i.tag for i in (await self.get_tags(image)))

        no_dupes = set(tags) - set(already_has)

        tags = (Tag(image_id=image.id, tag=i) for i in no_dupes)

        async with self.db.get_session() as s:
            q = s.insert
            q.rows(*tags)
            return await q.run()

    async def get_tags(self, image: Image) -> [Tag]:
        """Get the tags on an image.

        :param image: Image to get tags from.

        :return: List of tags on the image.
        """
        async with self.db.get_session() as s:
            q = s.select(Tag)
            q.add_condition(Tag.image_id == image.id)
            # TODO: eventually replace this with a relationship
            res = await q.all()
            return await res.flatten()

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

    async def delete_tag(self, tag: Tag) -> Tag:
        """Delete a tag from an image.

        :param tag: The :class:`pantsuBooru.models.Tag` to delete.

        :return: The deleted Tag.
        """

        async with self.db.get_session() as s:
            return await s.remove(tag)

    async def add_comment(self, image: Image, user: User, comment: str) -> Comment:
        """Add a comment to an image.

        :param image: The :class:`pantsuBooru.models.Image` object to add the tag to.
        :param user: The :class:`pantsuBooru.models.User` that added the comment.
        :param comment: The comment string.

        :return: The comment that was added.
        """

        async with self.db.get_session() as s:
            comment = Comment(image_id=image.id, poster=user.id, text=comment)
            q = s.insert.add_row(comment)
            [comment] = await q.run()
            return comment

    async def get_comments(self, image: Image) -> [Comment]:
        """Get a the comments on an image.

        :param image: Image object to get comments of.

        :return: List of comment objects."""
        async with self.db.get_session() as s:
            q = s.select(Comment)
            q.add_condition(Comment.image_id == image.id)
            # TODO: eventually replace this with a relationship
            res = await q.all()
            return await res.flatten()

    async def delete_comment(self, comment: Comment) -> Comment:
        """Delete a comment.

        :param comment: The :class:`pantsuBooru.models.Comment` to delete.

        :return: The deleted comment.
        """
        async with self.db.get_session() as s:
            return await s.remove(comment)
