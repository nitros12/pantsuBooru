from asyncqlio.orm.schema.column import Column
from asyncqlio.orm.schema.relationship import ForeignKey, Relationship
from asyncqlio.orm.schema.table import table_base
from asyncqlio.orm.schema.types import Integer, Text, Timestamp

from .user_models import User

Table = table_base("pantsu_booru")


class Image(Table):
    id = Column(Integer, primary_key=True, autoincrement=True)
    posted_at = Column(Timestamp)
    author = Column(Text, nullable=False)
    poster = Column(Integer, foreign_key=ForeignKey(User.id))
    tags = Relationship(id, 'Tag.image_id')
    comments = Relationship(id, 'Comment.image_id')

    # All images will be stored on disk in the format {database-id}_(full|thumb).(png|jpeg)
    # full images are stored in PNG format and are converted on upload
    # thumbnail images are stored in JPEG and are converted on upload
    # all images from a user are deleted when the user account is destroyed


class Tag(Table):
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, foreign_key=ForeignKey(Image.id))
    tag = Column(Text)

    # Tags are stored in the format | id | image_id | tag_string |
    # this way we can enumerate tags for an image, etc


class Comment(Table):
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, foreign_key=ForeignKey(Image.id))
    poster = Column(Integer, foreign_key=ForeignKey(User.id))
    text = Column(Text)
