from typing import Union


class BooruException(Exception):
    """Base class for booru exceptions."""
    reason = "Base"  # I'm not sure this is the best way to manage this.
    # An isinstance check will always be done on BooruException


class UserExists(BooruException):
    """Raised when an attempt to create a user that already exists is made."""
    reason = "An account with the same username and/or email already exists."


class NoUser(BooruException):
    """Raised when an attempt is made to login to a non existent account."""
    reason = "No account with such details exists."


class NoImage(BooruException):
    """Raised when an attempt is made to get, delete or edit tags to an image that does not exist."""
    reason = "No image with such details exists"
