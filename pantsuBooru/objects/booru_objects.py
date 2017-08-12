import inspect
from typing import Iterable

from pantsuBooru.backend import BooruDatabase
from pantsuBooru.models import Comment, Image, ImageTag, Tag, User


class AsyncMeta(type):
    async def __call__(self, *args, **kwargs):
        obb = object.__new__(self)
        fn = obb.__init__(*args, **kwargs)
        if inspect.isawaitable(fn):
            await fn
        return obb


class BooruBase(metaclass=AsyncMeta):
    async def __init__(self, db: BooruDatabase, row: 'Table'):
        self.db = db
        self.row = row

    def __getattr__(self, attr):
        try:
            return super().__getattr__(attr)
        except AttributeError as e:
            pass

        return getattr(self.row, attr)

    def to_json():
        raise NotImplemented


class BooruImage(BooruBase):
    async def __init__(self, db: BooruDatabase, row: Image):
        await super().__init__(db, row)
        self.poster = await self.db.get_user(id=self.row.poster)
        self.tags = [i.tag.tag
                     for i in row.tags]  # row.tags is list of ImageTag
        self.comments = list(row.comments)

    async def replace_tags(self, *tags: str):
        """Replace tags on the image.

        :param tags: The tags to replace on the image.
        """
        self.tags.clear()
        self.tags.extend(await self.db.replace_tags(self.id, *tags))

    async def add_comment(self, text: str, poster: 'BooruUser'):
        self.comments.append(
            await self.db.add_comment(self.id, poster.id, text))

    async def delete(self):
        await self.db.delete_all_tags(self.id)
        await self.db.delete_image(self.id)
        # TODO: Evict ourself from cache here

    def to_json(self, meta_only=True):
        """convert to json.

        :param meta_only: If True, dont include comments.
        """
        d = {
            "id": self.id,
            "posted_at": self.posted_at.timestamp(),
            "author": self.author,
            "source": self.source,
            "poster": self.poster.to_json(),
            "tags": self.tags,
        }

        if not meta_only:
            d["comments"] = [i.to_json() for i in self.comments]
        return d


class BooruUser(BooruBase):
    async def __init__(self, db: BooruDatabase, row: User):
        await super().__init__(db, row)
        self.posted_images = list(row.posted_images)
        self.posted_comments = list(row.posted_comments)

    async def add_image(self, author: str, source: str, tags: Iterable[str]):
        """Add an image posted by this user.

        :param author: The author of the image.
        :param source: The source of the image.
        :param tags: Iterable of tags to add to the image.
        """
        self.posted_images.append(
            await self.db.add_image(author, source, self.id, tags))
        self.add_image()

    async def add_comment(self, image: BooruImage, comment: str):
        """Add a comment to an image.

        :param image: The :class:`pantsuBooru.objects.BooruImage` to add the comment to.
        :param comment: The comment to add.
        """
        self.posted_comments.append(
            await self.db.add_comment(image.id, self.id, comment))

    async def delete(self):
        await self.db.delete_all_tags(*(i.id for i in self.posted_images))
        await self.db.delete_user(self.id)
        # TODO: Evict ourself from cache here

    async def reset_password(self, password: str):
        self.password = self.db.reset_password(self.id, password)

    def to_json(self):
        return {
            "id": self.id,
            "joined_at": self.joined_at,
            "username": self.username,
            "posted_images": [i.to_json() for i in self.posted_images]
        }


class BooruComment(BooruBase):
    async def __init__(self, db: BooruDatabase, row: Comment):
        pass
