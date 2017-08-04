class BooruException(Exception):
    """Base class for booru exceptions."""
    # I'm not sure this is the best way to manage this.
    # An isinstance check will always be done on BooruException

    def __init__(self, *args):
        super().__init__(self.reason, *args)


class UserExists(BooruException):
    """Raised when an attempt to create a user that already exists is made."""

    reason = "An account with the same username and/or email already exists."


class NoUser(BooruException):
    """Raised when an attempt is made to login to a non existent account."""

    reason = "No account with such details exists."


class NoImage(BooruException):
    """Raised when an attempt is made to get, delete or edit tags to an image that does not exist."""

    reason = "No image with such details exists"


class TagExists(BooruException):
    """Raised when a tag already existed for an image it was added to."""

    reason = "A tag of the same value already existed for that image."
