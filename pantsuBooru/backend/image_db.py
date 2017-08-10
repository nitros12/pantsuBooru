from datetime import datetime
from typing import Iterable

from pantsuBooru.backend.exceptions import TagExists
from pantsuBooru.models import Image, Tag, ImageTag, User, Comment

from .utils import BaseDatabase

from asyncqlio.orm.operators import In


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
            [image] = await s.insert.add_row(image)

        await self.insert_tags(image.id, *tags)
        return image

    async def get_image(self, image_id: int) -> Image:
        """Retrieve an image from the database.

        :param image_id: ID of image to fetch.

        :return: The :class:`pantsuBooru.models.Image` fetched.
        """
        async with self.db.get_session() as s:
            return await s.select(Image).where(Image.id == image_id).first()

    async def get_many_images(self, *image_ids: int) -> [Image]:
        """Retrieve images given a list of image IDs.
        The order of images retrieved is preserved

        :param image_ids: List of image IDs to fetch.

        :return: A list of :class:`pantsuBooru.models.Image`.
        """
        async with self.db.get_session() as s:
            images = await s.select(Image).where(In(Image.id, image_ids)).all()
            images = await images.flatten()
            return sorted(images, key=lambda x: image_ids.index(x.id))

    async def delete_image(self, image_id: int) -> Image:
        """Delete an image.

        :param image_id: ID of image to delete.
        """
        async with self.db.get_session() as s:
            return await s.remove(Image(id=image_id))

    async def insert_tags(self, image_id, *tags: str):
        """Insert tags onto an image.

        Should only be done when the image has NO tags.

        :param image_id: ID of image to add tags to.
        :param tags: Tags to add to image.
        """
        tags = list(map(str.lower, tags))

        async with self.db.get_session() as s:
            q = s.select(Tag).where(In(Tag.tag, tags))
            print(q.generate_sql())
            existing_tags = await (await q.all()).flatten()
            # Tags that already exist in the db
            to_create = set(tags) - set(i.tag for i in existing_tags)
            # Tags that dont exist and need to be created

            created = await s.insert.rows(*(Tag(tag=i)
                                            for i in to_create)).run()

            tags = existing_tags + created

            await s.insert.rows(*(ImageTag(tag_id=i.id, image_id=image_id)
                                  for i in tags))

    async def replace_tags(self, image_id: int, *tags: str):
        """Replace the tags on an image.

        :param image_id: ID of image to add tags to.
        :param tags: Iterable of strings to add.
        """
        await self.delete_all_tags(image_id)
        await self.insert_tags(image_id, *tags)

    async def delete_all_tags(self, image_id: int) -> [Tag]:
        """Delete all the tags on an image.

        :param image_id: ID of the image to remove tags of.
        """
        async with self.db.get_session() as s:
            q = s.delete(ImageTag).where(ImageTag.image_id == image_id)
            deleted = await q.run()
            await s.execute("""
                DELETE FROM "tag"
                WHERE NOT EXISTS (SELECT 1 from "imagetag"
                                  WHERE "imagetag"."tag_id" = "tag"."id");""")
            # run cleanup on tags that dont have any matched images

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

    async def search_tags(self, *tags: str, limit=100) -> [Image]:
        """Search images by tags.

        :param tags: Tags to search for.
        :param limit: Limit of images to return.

        :return: List of :class:`pantsuBooru.models.Image` ordered by most matching tags.
        """
        tags = list(map(str.lower, tags))

        async with self.db.get_session() as s:
            tags_v = [f"${i}" for i, _ in enumerate(tags, 1)]
            tags_fmt = ", ".join(tags_v)

            query = f"""SELECT "image"."id"
            FROM "imagetag", "image", "tag"
            WHERE "imagetag"."tag_id" = "tag"."id"
                AND ("tag"."tag" IN ({tags_fmt}))
                AND "image"."id" = "imagetag"."image_id"
            GROUP BY "image"."id"
            ORDER BY COUNT(image.id) DESC
            LIMIT {limit}
            """

            async with await s.cursor(query, dict(zip(tags_v, tags))) as c:
                image_ids = [i.get("id") async for i in c]
                print(image_ids)
            return await self.get_many_images(*image_ids)
