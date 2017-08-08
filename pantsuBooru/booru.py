import asyncio

from asyncqlio.db import DatabaseInterface

from pantsuBooru import backend

from pantsuBooru.models import Tag

db = DatabaseInterface("postgresql://postgres:postgres@127.0.0.1:5432/pantsuBooru")

images = backend.ImageDB(db)
users = backend.UserDB(db)


async def main():
    await db.connect()
    user = await users.create_user("test_user", "test@test.com", "test")
    image = await images.add_image("me", "www.source.com/source", user, ("wew", "more_tags", "kek"))
    try:
        await images.add_tag(Tag(image_id=image.id, tag="wew"))
    except Exception as e:
        print(f"Got exception correctly: {e}")
    await images.add_tag(Tag(image_id=image.id, tag="moretags"))
    tag = await images.add_tag(Tag(image_id=image.id, tag="added_with_id"))
    print(tag)
    await images.delete_tag(tag)
    print(await images.add_tags(image, "wew", "unique_tag", "kek"))
    print(await images.get_tags(image))
    comment = await images.add_comment(image, user, "Wew lad this is a comment")
    print(comment)
    got_user = await users.get_user(id=user.id)
    print(f"retrieved user = {got_user}")

    print(await images.get_comments(image))
    print(await users.get_comments(user))
    print(await users.get_images(user))

    await images.delete_comment(comment)
    await images.delete_image(image)
    await users.delete_user(user)


# testing file so I can get used to this and see what can be done/ what cannot

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
