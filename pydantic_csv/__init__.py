"""
pydantic_csv
~~~~~~~~~~~~~

The pydantic_csv is a library that parses every row of a CSV file into
`pydantic.BaseModels`. It takes advantage of `BaseModel` features to perform
data validation and type conversion.

Basic Usage
~~~~~~~~~~~~~

Read data from a CSV file:

    >>> from pydantic import BaseModel
    >>> from pydantic_csv import BasemodelCSVReader

    >>> class User(BaseModel):
    >>>    firstname: str
    >>>    lastname: str
    >>>    age: int

    >>> with open('users.csv') as csv:
    >>>    reader = BasemodelCSVReader(csv, User)
    >>>    users = list(reader)
    >>>    print(users)
    [
        User(firstname='User1', lastname='Test', age=23),
        User(firstname='User2', lastname='Test', age=34)
    ]

Write BaseModels to a CSV file:

    >>> from pydantic import BaseModel
    >>> from pydantic_csv import BasemodelCSVWriter

    >>> class User(BaseModel):
    >>>    firstname: str
    >>>    lastname: str
    >>>    age: int

    >>> users = [
    >>>    User(firstname='User1', lastname='Test', age=23),
    >>>    User(firstname='User2', lastname='Test', age=34)
    >>> ]

    >>> with open('users.csv', 'w') as csv:
    >>>    writer = BasemodelCSVWriter(csv, users, User)
    >>>    writer.write()


:copyright: (c) 2024 by Nathan Richard.
:license: BSD, see LICENSE for more details.
"""

from .basemodel_csv_reader import BasemodelCSVReader
from .basemodel_csv_writer import BasemodelCSVWriter
from .exceptions import CSVValueError

__all__ = [
    "BasemodelCSVReader",
    "BasemodelCSVWriter",
    "CSVValueError",
]
