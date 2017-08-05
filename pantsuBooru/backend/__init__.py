from .image_db import ImageDB
from .user_db import UserDB
from .exceptions import *


class BooruDatabase(UserDB, ImageDB):
    # Merge db classes here
    # UserDB is the first since it requires the loop attr
    pass
