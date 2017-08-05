from pantsuBooru.backend import BooruDatabase
from pantsuBooru.models import Image, Tag, User
from pantsuBooru.objects.user import BooruUser


class BooruImage:
    def __init__(self, db: BooruDatabase, row: Image):
        self.db = db
        self.row = row

    async def add_tags(self, *tags: str) -> [Tag]:
        """Add tags to the image.

        :param tags: The tags to add to this image.
        """
        return await self.db.add_tags(*tags)

    async def get_poster(self) -> 'BooruUser':
        """Get the poster of the image."""
        return await self.db.get_user(id=self.row.poster)


class BooruUser:
    # TODO: Fill in BooruUser methods
