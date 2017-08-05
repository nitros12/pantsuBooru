import asyncio
from typing import Union

from asyncqlio.db import DatabaseInterface
from asyncqlio.orm.operators import And, ComparisonOp, Eq, Or
from asyncqlio.orm.schema.table import Table


def make_comp_search(table: Table, comp_op: ComparisonOp=Eq, join_op: Union[Or, And]=Or, **matches) -> Union[Or, And]:
    """Build a condition from a dictionary of matched conditions.

    :param table: The table to build on.
    :param comp_op: The comparison op to use.
    :param join_op: The joining operator to use.
    :param matches: Dict of {column:value} to build with.

    :retuns: The built condition.
    """
    searches = [comp_op(getattr(table, k), v) for k, v in matches.items()]
    if not searches:
        raise Exception("At least one attribute is required to search by")
    return join_op(*searches)


class BaseDatabase:
    def __init__(self, db: DatabaseInterface, loop=None):
        self.db = db
        self.loop = asyncio.get_event_loop()
