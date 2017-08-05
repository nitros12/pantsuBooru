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
    password = Column(Text, nullable=False)
    # posted_images = Relationship(id, "image.poster")
    # posted_comments = Relationship(id, "comment.poster")


class Image(Table):
    id = Column(Integer, primary_key=True, autoincrement=True)
    posted_at = Column(Timestamp)
    author = Column(Text)
    source = Column(Text)
    poster = Column(Integer, foreign_key=ForeignKey(User.id))
    # tags = Relationship(id, 'tag.image_id')
    # comments = Relationship(id, 'comment.image_id')

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


"""
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    joined_at TIMESTAMP,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE "image" (
    id SERIAL PRIMARY KEY,
    posted_at TIMESTAMP,
    author TEXT,
    source TEXT,
    poster INTEGER REFERENCES "user" (id) ON DELETE CASCADE
);

CREATE TABLE "tag" (
    id SERIAL PRIMARY KEY,
    image_id INTEGER REFERENCES "image" (id) ON DELETE CASCADE,
    tag TEXT NOT NULL UNIQUE
);

CREATE TABLE "comment" (
    id SERIAL PRIMARY KEY,
    image_id INTEGER REFERENCES "image" (id) ON DELETE CASCADE,
    poster INTEGER REFERENCES "user" (id) ON DELETE CASCADE,
    text TEXT
);
"""
