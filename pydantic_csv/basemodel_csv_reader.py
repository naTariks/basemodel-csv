"""
module containing the BasemodelCSVReader Class to read from a CSV file and the parse it into a pydantic.BaseModel
"""

import csv
import typing
from collections import Counter
from collections.abc import Sequence
from typing import Any, Optional, Union

import pydantic
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from .exceptions import CSVValueError
from .header_mapper import HeaderMapper


def _verify_duplicate_header_items(header: Sequence[str]) -> Optional[list[str]]:
    if header is not None and len(header) == 0:
        return

    header_counter = Counter(header)
    duplicated = [k for k, v in header_counter.items() if v > 1]

    if len(duplicated) > 0:
        raise ValueError(
            f"It seems like the CSV file contain duplicated header values: {duplicated}. This may cause "
            "inconsistent data. Use the kwarg validate_header=False when initializing the DataclassReader to skip "
            "the header validation."
        )


def _is_union_type(t) -> bool:
    return hasattr(t, "__origin__") and t.__origin__ is Union


def _get_args(t):
    return getattr(t, "__args__", tuple())


class BasemodelCSVReader:
    """
    The Reader, which takes a file object and the BaseModel in which each row of the CSV should be parsed and returned
    """

    def __init__(
        self,
        file_obj: Any,
        model: type[BaseModel],
        *,
        use_alias: bool = True,
        validate_header: bool = True,
        fieldnames: Optional[Sequence[str]] = None,
        restkey: Optional[str] = None,
        restval: Optional[Any] = None,
        dialect: str = "excel",
        **kwargs: Any,
    ):

        if not file_obj:
            raise ValueError("The 'file_obj' argument is required")

        if model is None or not issubclass(model, pydantic.BaseModel):
            raise ValueError("cls argument needs to be a pydantic BaseModel.")

        self._model = model
        self._use_alias = use_alias
        self._optional_fields = self._get_optional_fields()
        self._field_mapping: dict[str, str] = {}

        self._reader = csv.DictReader(file_obj, fieldnames, restkey, restval, dialect, **kwargs)

        if validate_header:
            _verify_duplicate_header_items(self._reader.fieldnames)

        self.type_hints = typing.get_type_hints(model)

    def _get_optional_fields(self) -> list[str]:
        if self._use_alias:
            return [field.alias or name for name, field in self._model.model_fields.items() if not field.is_required()]
        return [name for name, field in self._model.model_fields.items() if not field.is_required()]

    def _add_to_mapping(self, fieldname: str, csv_fieldname: str) -> None:
        self._field_mapping[fieldname] = csv_fieldname

    @staticmethod
    def _get_default_value(field: FieldInfo) -> Any:
        if field.default_factory:
            return field.default_factory()
        return field.default

    @staticmethod
    def _get_possible_keys(fieldname: str, row: dict) -> Optional[str]:
        possible_keys = filter(lambda x: x.strip() == fieldname, row)
        return next(possible_keys, None)

    def _get_value(self, row: dict, fieldname: str, field: FieldInfo) -> Any:
        is_field_mapped = False

        if fieldname in self._field_mapping:
            is_field_mapped = True
            key = self._field_mapping.get(fieldname)
        else:
            key = fieldname

        try:
            if key in row:
                value = row[key]
            else:
                possible_key = self._get_possible_keys(fieldname, row)
                key = possible_key if possible_key else key
                value = row[key]

        except KeyError as e:
            if fieldname in self._optional_fields:
                return self._get_default_value(field)

            keyerror_message = f"The value for the column `{fieldname}`"
            if is_field_mapped:
                keyerror_message = f"The value for the mapped column `{key}`"
            raise KeyError(f"{keyerror_message} is missing in the CSV file") from e

        if not value and fieldname in self._optional_fields:
            return self._get_default_value(field)

        if not value and fieldname not in self._optional_fields:
            raise ValueError(f"The field `{fieldname}` is required.")

        return value

    def _process_row(self, row: dict) -> BaseModel:
        values = {}

        for name, field in self._model.model_fields.items():

            if self._use_alias:
                fieldname = field.alias or name
            else:
                fieldname = name

            try:
                value = self._get_value(row, fieldname, field)
                if not value and field.default is None:
                    values[fieldname] = None
                else:
                    values[fieldname] = value
            except ValueError as e:
                raise CSVValueError(e, line_number=self._reader.line_num) from None

        try:
            return self._model(**values)
        except pydantic.ValidationError as e:
            raise CSVValueError(
                str(e),
                line_number=self._reader.line_num,
            ) from e

    def __next__(self):
        row: dict = next(self._reader)
        return self._process_row(row)

    def __iter__(self):
        return self

    def map(self, header: str) -> HeaderMapper:
        """
        reader.map("First Name").to("firstname")
        Used to map Column name in the Header of the CSV file to a BaseModel field.

        Args:
            header (str): The Column Name of the Header in the CSV file

        Returns:
            HeaderMapper: HeaderMapper instance which then can be used to set the BaseModel field name
            (.to("firstname"))
        """
        return HeaderMapper(lambda fieldname: self._add_to_mapping(fieldname, header))
