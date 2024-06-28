"""
model containing custom Exceptions
"""

from typing import Any


class CSVValueError(Exception):
    """
    Raised Exception if a problem with the value in the CSV file occurs. Also prints out the line where the problem
    happened.
    """

    def __init__(self, error: Any, line_number: int):
        self.error: Any = error
        self.line_number: int = line_number

    def __str__(self):
        return f"[Error on CSV Line number: {self.line_number}]\n{self.error}"
