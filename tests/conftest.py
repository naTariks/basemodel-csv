import datetime
import io
import pathlib

import pytest

from pydantic_csv import BasemodelCSVReader, BasemodelCSVWriter

from .models import LotsOfDates, User, UserOptional


@pytest.fixture
def files_path() -> pathlib.Path:
    tests_folder: pathlib.Path = pathlib.Path(__file__).resolve().parent
    return tests_folder / "mocks"


@pytest.fixture
def user_list():
    return [
        User(
            id=13,
            firstname="Emily",
            lastname="Johnson",
            birthday=datetime.date(year=1991, month=10, day=12),
            signed_up=True,
        ),
        User(id=14, firstname="Benjamin", lastname="Adams", birthday=datetime.date(year=1986, month=3, day=29)),
        User(
            id=15,
            firstname="Olivia",
            lastname="Anderson",
            birthday=datetime.date(year=2000, month=8, day=3),
            signed_up=True,
        ),
    ]


@pytest.fixture
def users_as_csv_buffer(user_list):
    buffer: io.StringIO = io.StringIO()

    writer = BasemodelCSVWriter(buffer, user_list, User)
    writer.write()

    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def users_mapped_as_csv_buffer(user_list):
    buffer: io.StringIO = io.StringIO()

    writer = BasemodelCSVWriter(buffer, user_list, User)
    writer.map("firstname").to("First Name")
    writer.map("lastname").to("Last Name")
    writer.map("birthday").to("Birthday")
    writer.write()

    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def users_from_csv(files_path):
    with open(files_path / "users.csv", newline="") as csv:
        value = csv.read()

    return value


@pytest.fixture
def users_mapped_from_csv(files_path):
    with open(files_path / "users_mapped.csv", newline="") as csv:
        value = csv.read()

    return value


@pytest.fixture
def users_read_from_csv(files_path) -> list[BasemodelCSVReader]:
    with open(files_path / "users.csv", newline="") as csv:
        reader = BasemodelCSVReader(csv, User)
        return list(reader)


@pytest.fixture
def users_read_from_csv_with_spaces(files_path) -> list[BasemodelCSVReader]:
    with open(files_path / "users_space_in_header.csv", newline="") as csv:
        reader = BasemodelCSVReader(csv, User)
        return list(reader)


@pytest.fixture
def users_read_from_csv_optional(files_path):
    with open(files_path / "users_optional.csv", newline="") as csv:
        reader = BasemodelCSVReader(csv, UserOptional)
        return list(reader)


@pytest.fixture
def model_from_csv_default_factory(files_path):
    with open(files_path / "default_factory.csv", newline="") as csv:
        reader = BasemodelCSVReader(csv, UserOptional)
        return list(reader)


@pytest.fixture
def dates_from_csv(files_path):
    with open(files_path / "dates.csv", newline="") as csv:
        reader = BasemodelCSVReader(csv, LotsOfDates, delimiter=";")
        return list(reader)
