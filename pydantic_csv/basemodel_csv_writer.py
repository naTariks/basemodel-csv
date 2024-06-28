"""
module containing the BasemodelCSVWriter Class to write from instances of a BaseModel to a CSV File
"""

import csv
from typing import Any

import pydantic
from pydantic import BaseModel

from .header_mapper import HeaderMapper


class BasemodelCSVWriter:
    """
    The Writer, which takes a file object and instances of BaseModels in order to write them to a CSV file
    """

    def __init__(
        self,
        file_obj: Any,
        data: list[Any],
        model: type[BaseModel],
        *,
        use_alias: bool = True,
        dialect: str = "excel",
        **kwargs: Any,
    ):
        if not file_obj:
            raise ValueError("The 'file_obj' argument is required")

        if not isinstance(data, list):
            raise ValueError("Invalid 'data' argument. It must be a list")

        if model is None or not issubclass(model, pydantic.BaseModel):
            raise ValueError("Invalid 'cls' argument. It must be a pydantic BaseModel")

        self._data = data
        self._model = model
        self._field_mapping: dict[str, str] = {}

        if use_alias:
            self._fieldnames = [field.alias or name for name, field in self._model.model_fields.items()]
        else:
            self._fieldnames = model.model_fields.keys()

        self._writer = csv.writer(file_obj, dialect=dialect, **kwargs)

    def _add_to_mapping(self, header: str, fieldname: str) -> None:
        self._field_mapping[fieldname] = header

    def _apply_mapping(self) -> list[str]:
        mapped_fields = []

        for field in self._fieldnames:
            mapped_item = self._field_mapping.get(field, field)
            mapped_fields.append(mapped_item)

        return mapped_fields

    def write(self, skip_header: bool = False) -> None:
        """
        Used to start the writing process. Afterward the provided data will be written to a CSV file.
        **Important:** Remember to do all the mappings beforehand. Afterward it's too late.

        Args:
            skip_header (bool):

        Returns:
            None: well, nothing
        """
        if not skip_header:
            if self._field_mapping:
                self._fieldnames = self._apply_mapping()

            self._writer.writerow(self._fieldnames)

        for item in self._data:
            if not isinstance(item, self._model):
                raise TypeError(
                    f"The item [{item}] is not an instance of "
                    f"{self._model.__name__}. All items on the list must be "
                    "instances of the same type"
                )
            row = item.model_dump().values()
            self._writer.writerow(row)

    def map(self, fieldname: str) -> HeaderMapper:
        """
        writer.map("firstname").to("First Name")
        Used to map a BaseModel field to Column name in the Header of the CSV file
        **Important:** If not specifically set `writer = BasemodelCSVWriter(file_obj, data, BaseModel,
        *use_alias=false*)` you have to use the alias name of the field. (Of course only if one is set)

        Args:
            fieldname (str): The name of the BaseModel field to be mapped

        Returns:
            HeaderMapper: HeaderMapper instance which then can be used to set the Header name (.to("First Name"))
        """
        return HeaderMapper(lambda header: self._add_to_mapping(header, fieldname))
