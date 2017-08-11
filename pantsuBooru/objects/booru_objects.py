from pantsuBooru.backend import BooruDatabase
from pantsuBooru.models import Image, Tag, User, Comment, ImageTag
import inspect


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
        self.poster = await self._get_poster()
        self.tags = list(row.tags)
        self.comments = list(row.comments)

    async def replace_tags(self, *tags: str) -> [Tag]:
        """Replace tags on the image.

        :param tags: The tags to replace on the image.
        """
        return await self.db.replace_tags(self.id, *tags)

    async def _get_poster(self) -> 'BooruUser':
        """Get the poster of the image."""
        return await self.db.get_user(id=self.poster)

    async def add_comment(self, text: str, poster: 'BooruUser'):
        comment = Comment(text=text, poster=poster)
        async with self.db.get_session() as s:
            self.comments.append(await self.comments.add(comment))

    def to_json(self):
        return {
            "id": self.id,
            "posted_at": self.posted_at.timestamp(),
            "author": self.author,
            "source": self.source,
            "poster": self.poster.to_json(),
            "tags": [i.to_json() for i in self.tags],
            "comments": [i.to_json() for i in self.comments]
        }


class BooruUser(BooruBase):
    # TODO: Fill in BooruUser methods
