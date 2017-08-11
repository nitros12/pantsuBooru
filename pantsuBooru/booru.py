import asyncio
import logging
import sys

from asyncqlio.db import DatabaseInterface

from pantsuBooru import backend

from pantsuBooru.models import Tag

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

db = DatabaseInterface(
    "postgresql://postgres:postgres@127.0.0.1:5432/pantsuBooru")

images = backend.ImageDB(db)
users = backend.UserDB(db)


async def main():
    await db.connect()
    user = await users.create_user("test_user", "test@test.com", "test")
    try:
        image = await images.add_image("me", "www.source.com/source", user.id,
                                       ("wew", "more_tags", "kek"))
        image2 = await images.add_image("me", "no", user.id, ("wew", "kek"))
        wew = await images.search_tags("wew")
        print(wew)
        image_get = await images.get_image(image.id)
        print(image_get.tags)
        print(image_get.comments)
    except Exception as e:
        raise e
    finally:
        await users.delete_user(user.id)
        pass


# testing file so I can get used to this and see what can be done/ what cannot

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
