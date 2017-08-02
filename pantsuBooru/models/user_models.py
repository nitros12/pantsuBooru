from asyncqlio.orm.schema.column import Column
from asyncqlio.orm.schema.relationship import ForeignKey, Relationship
from asyncqlio.orm.schema.table import table_base
from asyncqlio.orm.schema.types import Integer, Text, Timestamp

Table = table_base("pantsu_booru")


class User(Table):
    id = Column(Integer, primary_key=True, autoincrement=True)
    joined_at = Column(Timestamp)
    username = Column(Text, nullable=False, unique=True)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    posted_images = Relationship(id, "Image.poster")
    posted_comments = Relationship(id, "Comment.poster")
