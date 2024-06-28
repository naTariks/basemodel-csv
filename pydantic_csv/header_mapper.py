"""
This module contains the HeaderMapper which can be used to define different Headers than the standard with the Field
alias/name.
"""

from typing import Callable


class HeaderMapper:
    """
    The `HeaderMapper` class is used to explicitly map a field of the BaseModel to a Header. Useful when the header on
    the CSV file needs to be different from a BaseModel field name.
    """

    def __init__(self, callback: Callable[[str], None]):
        def to(name: str) -> None:
            """
            When writing:
                Specify the CSV Header that should be used instead of the BaseModel field name

            when reading:
                Specify the BaseModel field name that should listen to the CSV Header
                **Important:** If not specifically set
                `reader = BasemodelCSVReader(file_obj, BaseModel, *use_alias=false*)` you have to use the alias name of
                the field (Of course only if one is set)

            Args:
                name (str): The CSV Header name (writing) or the BaseModel field name (reading)
            """
            callback(name)

        self.to: Callable[[str], None] = to
