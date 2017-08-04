import asyncio

from asyncqlio.db import DatabaseInterface

from pantsuBooru import backend

db = DatabaseInterface("postgresql://postgres:postgres@127.0.0.1:5432/pantsuBooru")

images = backend.ImageDB(db)
users = backend.UserDB(db)


async def main():
    await db.connect()
    user = await users.create_user("test_user", "test@test.com", "test")
    image = await images.add_image("me", "www.source.com/source", user, ("wew", "more_tags", "kek"))
    try:
        await images.add_tag(image, "wew")
    except Exception as e:
        print(f"Got exception correctly: {e}")
    await images.add_tag(image, "another_tag")
    await images.add_tag(image.id, "added_with_id")

# testing file so I can get used to this and see what can be done/ what cannot

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
