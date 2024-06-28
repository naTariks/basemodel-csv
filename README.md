# pydantic - CSV

Pydantic CSV makes working with CSV files easier and much better than working with Dicts. It uses pydantic BaseModels to store data of every row on the CSV file and also uses type annotations which enables proper type checking and validation.

## Table of Contents
- [Main features](#main-features)
- [Installation](#installation)
- [Getting started](#getting-started)
  * [Using the BasemodelCSVReader](#using-the-basemodelcsvreader)
    + [Error handling](#error-handling)
    + [Default values](#default-values)
    + [Mapping BaseModel fields to columns](#mapping-basemodel-fields-to-columns)
    + [Supported type annotation](#supported-type-annotation)
    + [User-defined types](#user-defined-types)
  * [Using the BasemodelCSVWriter](#using-the-basemodelcsvwriter)
    + [Modifying the CSV header](#modifying-the-csv-header)
- [Copyright and License](#copyright-and-license)
- [Credits](#credits)

## Main features

- Use `pydantic.BaseModel` instead of dictionaries to represent the rows in the CSV file.
- Take advantage of the `BaseModel` properties type annotation. `BasemodelCSVReader` uses the type annotation to perform validation on the data of the CSV file.
- Automatic type conversion. `BasemodelCSVReader` supports `str`, `int`, `float`, `complex`, `datetime` and `bool`, as well as any type whose constructor accepts a string as its single argument.
- Helps you troubleshoot issues with the data in the CSV file. `BasemodelCSVReader` will show exactly, which line of the CSV file contains errors.
- Extract only the data you need. It will only parse the properties defined in the `BaseModel`
- Familiar syntax. The `BasemodelCSVReader` is used almost the same way as the `DictReader` in the standard library.
- It uses `BaseModel` features that let you define Field properties or Config so the data can be parsed exactly the way you want.
- Make the code cleaner. No more extra loops to convert data to the correct type, perform validation, set default values, the `BasemodelCSVReader` will do all this for you.
- In addition to the `BasemodelCSVReader`, the library also provides a `BasemodelCSVWriter` which enables creating a CSV file using a list of instances of a BaseModel.
- Because [sqlmodel](https://github.com/tiangolo/sqlmodel) uses pydantic.BaseModels too, you can directly fill a database with data from a CSV


## Installation

```shell
pip install pydantic-csv
```

## Getting started

### Using the BasemodelCSVReader

First, add the necessary imports:

```python
from pydantic import BaseModel

from pydantic_csv import BasemodelCSVReader
```

Assuming that we have a CSV file with the contents below:
```text
firstname,email,age
Elsa,elsa@test.com,26
Astor,astor@test.com,44
Edit,edit@test.com,33
Ella,ella@test.com,22
```

Let's create a BaseModel that will represent a row in the CSV file above:
```python
class User(BaseModel):
    firstname: str
    email: str
    age: int
```

The BaseModel `User` has 3 properties, `firstname` and `email` is of type `str` and `age` is of type `int`.

To load and read the contents of the CSV file we do the same thing as if we would be using the `DictReader` from the `csv` module in the Python's standard library. After opening the file we create an instance of the `BasemodelCSVReader` passing two arguments. The first is the `file` and the second is the BaseModel that we wish to use to represent the data of every row of the CSV file. Like so:

```python
# using file on disk
with open("<filename>") as csv:
  reader = BasemodelCSVReader(csv, User)
  for row in reader:
    print(row)


# using buffer (has to be a string buffer -> convert beforehand)
buffer = io.StringIO()
buffer.seek(0)  # ensure that we read from the beginning

reader = BasemodelCSVReader(buffer, User)
for row in reader:
  print(row)
```

If you run this code you should see an output like this:

```python
User(firstname='Elsa', email='elsa@test.com', age=11)
User(firstname='Astor', email='astor@test.com', age=7)
User(firstname='Edit', email='edit@test.com', age=3)
User(firstname='Ella', email='ella@test.com', age=2)
```

The `BasemodelCSVReader` internally uses the `DictReader` from the `csv` module to read the CSV file which means that you can pass the same arguments that you would pass to the `DictReader`. The complete argument list is shown below:

```python
BasemodelCSVReader(
    file_obj: Any,
    model: Type[BaseModel],
    *,  # Note that you can't provide any value without specifying the parameter name
    use_alias: bool = True,
    validate_header: bool = True,
    fieldnames: Optional[Sequence[str]] = None,
    restkey: Optional[str] = None,
    restval: Optional[Any] = None,
    dialect: str = "excel",
    **kwargs: Any,
)
```

All keyword arguments supported by `DictReader` are supported by the `BasemodelCSVReader`, except `use_alias` and `validate_header`. Those are used to change the behaviour of the `BasemodelCSVReader` as follows:

`use_alias` - The `BasemodelCSVReader` will search for column names identical to the aliases of the BaseModel Fields (if set, otherwise its names).
To avoid this behaviour and use the field names in every case set `use_alias = False` when creating an instance of the `BasemodelCSVReader`, see an example below:
```python
reader = BasemodelCSVReader(csv, User, use_alias=False)
```

`validate_header` - The `BasemodelCSVReader` will raise a `ValueError` if the CSV file contains columns with the same name. This
validation is performed to avoid data being overwritten. To skip this validation set `validate_header=False` when creating an
instance of the `BasemodelCSVReader`, see an example below:

```python
reader = BasemodelCSVReader(csv, User, validate_header=False)
```
**Important:** If two or more columns with the same name exists it tries to instantiate the BaseModel with the data from the column most right.

#### Error handling

One of the advantages of using the `BasemodelCSVReader` is that it makes it easy to detect when the type of data in the CSV file is not what your application's model is expecting. And, the `BasemodelCSVReader` shows errors that will help to identify the rows with problems in your CSV file.

For example, say we change the contents of the CSV file shown in the **Getting started** section and, modify the `age` of the user Astor, let's change it to a string value:

```text
firstname,email,age
Elsa,elsa@test.com,26
Astor,astor@test.com,test
Edit,edit@test.com,33
Ella,ella@test.com,22
```

Remember that in the BaseModel `User` the `age` property is annotated with `int`. If we run the code again an exception from the pydantic validation will be raised with the message below:

```text
pydantic_csv.exceptions.CSVValueError: [Error on CSV Line number: 3]
E           1 validation error for UserOptional
E           age
E             Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='not a number', input_type=str]
E               For further information visit https://errors.pydantic.dev/2.7/v/int_parsing
```

Note that apart from telling what the error was, the `BasemodelCSVReader` will also show which line of the CSV file contain the data with errors.

#### Default values

The `BasemodelCSVReader` also handles properties with default values. Let's modify the BaseModel `User` and add a default value for the field `email`:

```python
from pydantic import BaseModel


class User(BaseModel):
    firstname: str
    email: str = 'Not specified'
    age: int
```

And we modify the CSV file and remove the email for the user Astor:

```text
firstname,email,age
Elsa,elsa@test.com,26
Astor,,44
Edit,edit@test.com,33
Ella,ella@test.com,22
```

If we run the code we should see the output below:

```text
User(firstname='Elsa', email='elsa@test.com', age=11)
User(firstname='Astor', email='Not specified', age=7)
User(firstname='Edit', email='edit@test.com', age=3)
User(firstname='Ella', email='ella@test.com', age=2)
```

Note that now the object for the user Astor has the default value `Not specified` assigned to the email property.

Default values can also be set using `pydantic.Field` like so:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    firstname: str
    email: str = Field(default='Not specified')
    age: int
```

#### Mapping BaseModel fields to columns

The mapping between a BaseModel field and a column in the CSV file will be done automatically if the names match. However, there are situations that the name of the header for a column is different. We can easily tell the `BasemodelCSVReader` how the mapping should be done using the method `map`.\
Assuming that we have a CSV file with the contents below:

```text
First Name,email,age
Elsa,elsa@test.com,26
Astor,astor@test.com,44
Edit,edit@test.com,33
Ella,ella@test.com,22
```

Note that now the column is called **First Name** and not **firstname**

And we can use the method `map`, like so:

```python
reader = BasemodelCSVReader(csv, User)
reader.map('First Name').to('firstname')
```

Now the BasemodelCSVReader will know how to extract the data from the column **First Name** and add it to the BaseModel property **firstname**

#### Supported type annotation

At the moment the `BasemodelCSVReader` supports `int`, `str`, `float`, `complex`, `datetime`, and `bool`. pydantic_csv doesn't parse the date(times) itself. Thus, it relies on the datetime parsing of pydantic. Now they support some common formats and unix timestamps, but if you have a more exotic format you can use a pydantic validator.

Assuming that the CSV file has the following contents:
```text
name,email,birthday
Edit,edit@test.com,Sunday, 6. January 2002
```

This would look like this:
```python
from pydantic import BaseModel, field_validator
from datetime import datetime


class User(BaseModel):
    name: str
    email: str
    birthday: datetime

    @field_validator("birthday", mode="before")
    def parse_birthday_date(cls, value):
        return datetime.strptime(value, "%A, %d. %B %Y").date()
```

#### User-defined types

You can use any type for a field as long as its constructor accepts a string:

```python
import re
from pydantic import BaseModel


class SSN:
    def __init__(self, val):
        if re.match(r"\d{9}", val):
            self.val = f"{val[0:3]}-{val[3:5]}-{val[5:9]}"
        elif re.match(r"\d{3}-\d{2}-\d{4}", val):
            self.val = val
        else:
            raise ValueError(f"Invalid SSN: {val!r}")


class User(BaseModel):
    name: str
    ssn: SSN
```


### Using the BasemodelCSVWriter

Reading a CSV file using the `BasemodelCSVReader` is great and gives us the type-safety of Pydantic's BaseModels and type annotation, however, there are situations where we would like to use BaseModels for creating CSV files, that's where the `BasemodelCSVWriter` comes in handy.

Using the `BasemodelCSVWriter` is quite simple. Given that we have a Basemodel `User`:

```python
from pydantic import BaseModel


class User(BaseModel):
    firstname: str
    lastname: str
    age: int
```

And in your program we have a list of users:

```python
users = [
    User(firstname="John", lastname="Smith", age=40),
    User(firstname="Daniel", lastname="Nilsson", age=23),
    User(firstname="Ella", lastname="Fralla", age=28)
]
```

In order to create a CSV using the `BasemodelCSVWriter` import it from `pydantic_csv`:

```python
from pydantic_csv import BasemodelCSVReader
```

Initialize it with the required arguments and call the method `write`:

```python
# using file on disk
with open("<filename>") as csv:
    writer = BasemodelCSVWriter(csv, users, User)
    writer.write()


# using buffer (has to be a StringBuffer)
writer = BasemodelCSVWriter(buffer, users, User)
writer.write()

buffer.seek(0)  # ensure that the next working steps start at the beginning of the "file"

# if you need a BytesBuffer just convert it:
bytes_buffer: io.BytesIO = io.BytesIO(buffer.read().encode("utf-8"))
bytes_buffer.name = buffer.name
bytes_buffer.seek(0)  # ensure that the next working steps start at the beginning of the "file"
```

That's it! Let's break down the snippet above.

First, we open a file called `user.csv` for writing. After that, an instance of the `BasemodelCSVWriter` is created. To create a `BasemodelCSVWriter` we need to pass the `file_obj`, the list of `User` instances, and lastly, the type, which in this case is `User`.

The type is required since the writer uses it when trying to figure out the CSV header. By default, it will use the alias of the field otherwise its name
defined in the BaseModel, in the case of the BaseModel `User` the title of each column will be `firstname`, `lastname` and `age`.

See below the CSV created out of a list of `User`:

```text
firstname,lastname,age
John,Smith,40
Daniel,Nilsson,23
Ella,Fralla,28
```

The `BasemodelCSVWriter` also takes `**fmtparams` which accepts the same parameters as the `csv.writer`. For more
information see: https://docs.python.org/3/library/csv.html#csv-fmt-params

Now, there are situations where we don't want to write the CSV header. In this case, the method `write` of
the `BasemodelCSVWriter` accepts an extra argument, called `skip_header`. The default value is `False` and when set to
`True` it will skip the header.

#### Modifying the CSV header

As previously mentioned the `BasemodelCSVWriter` uses the aliases or names of the fields defined in the BaseModel as the CSV header titles.
If you don't want the `BasemodelCSVWriter` to use the aliases and only the names you can set `use_alias` to `False`. This will look like this:
```python
writer = BasemodelCSVWriter(file_obj, users, User, use_alias=False)
```

However, depending on your use case it makes sense to set custom Headers and not use the aliases or names at all. The `BasemodelCSVWriter` has a `map` method just for this purpose.

 Using the `User` BaseModel with the properties `firstname`, `lastname` and `age`. The snippet below shows how to change `firstname` to `First name` and `lastname` to `Last name`:

 ```python
 with open("<filename>", "w") as file:
    writer = BasemodelCSVWriter(file, users, User)

    # Add mappings for firstname and lastname
    writer.map("firstname").to("First Name")
    writer.map("lastname").to("Last Name")

    writer.write()
 ```

 The CSV output of the snippet above will be:

```text
First Name,Last Name,age
John,Smith,40
Daniel,Nilsson,23
Ella,Fralla,28
```

## Copyright and License

Copyright (c) 2024 Nathan Richard. Code released under BSD 3-clause license

## Credits
A huge shoutout to Daniel Furtado ([github](https://github.com/dfurtado)) and his python package 'dataclass-csv' ([pypi](https://pypi.org/project/dataclass-csv/) | [github](https://github.com/dfurtado/dataclass-csv)). The most of the Codebase and Documentation is from him and just adjusted for using pydantic.BaseModel.
