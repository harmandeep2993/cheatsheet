# 12 - Pydantic

Quick reference for Pydantic v2: data validation with Python type hints, used by FastAPI, LLM structured outputs, agent frameworks and settings management.

## Introduction

### What is Pydantic?

Pydantic is a Python library that **checks and converts data** using type hints. You describe the shape of your data as a class (a **model**), and Pydantic makes sure any incoming data (JSON from an API, output from an LLM, values from a config file) matches that shape. If it does, you get a clean Python object with the right types. If not, you get a clear error saying exactly which field is wrong and why.

### Mental model

Think of a Pydantic model as a **customs checkpoint** at the border of your program:

```text
Outside world (untrusted)            Border (Pydantic model)                Inside your code (trusted)
-------------------------            -----------------------                --------------------------
'{"age": "42", "email": "a@b.c"}' -> check types, convert "42" -> 42,  ->  user.age == 42 (int)
LLM output, API request body,         check rules (age >= 0),               user.email is a valid email
.env values, CSV rows                 reject with a clear error if bad      safe to use, autocomplete works
```

Validate **once at the boundary**, then trust the object everywhere inside. The same model can also **export** a JSON Schema, which is exactly what LLM APIs and FastAPI use to describe inputs and outputs.

### Why use it?

- **Catch bad data early** with precise error messages instead of crashes deep in your code.
- **Automatic conversion**: `"42"` -> `42`, ISO strings -> `datetime`, dicts -> nested models.
- **One definition, many uses**: validation, JSON export, JSON Schema, editor autocomplete, docs.
- **Core of the AI stack**: FastAPI bodies, Claude / OpenAI structured outputs, tool definitions, LangChain, agent SDKs and `pydantic-settings` all use it.
- **Fast**: the core is written in Rust.

### Key terms

| Term | Meaning |
|---|---|
| Model | A class inheriting `BaseModel` that defines fields and types |
| Field | One attribute with a type (and optional rules / default) |
| Validation | Checking and converting input data |
| Serialization | Turning a model back into a dict / JSON |
| Validator | Your own function that checks or transforms a field |
| JSON Schema | Machine-readable description of the model, generated automatically |
| Coercion | Converting compatible values (`"1"` -> `1`) |
| Strict mode | No coercion: types must match exactly |

**Where it fits:** used in [39 - FastAPI](39_fastapi.md), [26 - LLM APIs](26_llm-apis.md) (structured outputs), [28 - Tool Use](28_tool-use.md), [32 - Agent Frameworks](32_agent-frameworks.md); builds on [09 - Python Basics](09_python-basics.md) type hints and [07 - JSON](07_yaml-json.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Pydantic documentation | https://docs.pydantic.dev/latest/ |
| pydantic-settings | https://docs.pydantic.dev/latest/concepts/pydantic_settings/ |
| Migration guide (v1 to v2) | https://docs.pydantic.dev/latest/migration/ |

---

## Contents

1. [Install and First Model](#1-install-and-first-model)
2. [Field Types](#2-field-types)
3. [Optional Fields and Defaults](#3-optional-fields-and-defaults)
4. [Field Constraints](#4-field-constraints)
5. [Nested Models and Lists](#5-nested-models-and-lists)
6. [Validation Errors](#6-validation-errors)
7. [Custom Validators](#7-custom-validators)
8. [Serialization (dump)](#8-serialization-dump)
9. [Parsing JSON and Dicts](#9-parsing-json-and-dicts)
10. [JSON Schema](#10-json-schema)
11. [Model Configuration](#11-model-configuration)
12. [Enums and Literals](#12-enums-and-literals)
13. [Aliases (Different Names in JSON)](#13-aliases-different-names-in-json)
14. [Computed Fields](#14-computed-fields)
15. [TypeAdapter (Validate Without a Model)](#15-typeadapter-validate-without-a-model)
16. [Settings from Environment (pydantic-settings)](#16-settings-from-environment-pydantic-settings)
17. [Pydantic for LLM Structured Output](#17-pydantic-for-llm-structured-output)
18. [Pydantic vs dataclass vs TypedDict](#18-pydantic-vs-dataclass-vs-typeddict)
19. [v1 to v2 Cheat Sheet](#19-v1-to-v2-cheat-sheet)
20. [Troubleshooting](#20-troubleshooting)

---

## 1. Install and First Model

> - **What:** Defining a model and creating validated objects.
> - **How:** Subclass `BaseModel`, declare fields with type hints, create instances with keyword arguments.
> - **When to use:** Any time data enters your program from outside.

```powershell
pip install pydantic
pip install "pydantic[email]"          # extra: EmailStr validation
```

```python
from pydantic import BaseModel


class User(BaseModel):
    """A registered user."""

    id: int
    name: str
    active: bool = True


u = User(id="42", name="Ana")          # "42" is converted to 42
u.id                                   # 42
u                                      # User(id=42, name='Ana', active=True)
u.name = "Bo"                          # models are mutable by default
```

## 2. Field Types

> - **What:** The types Pydantic understands and validates.
> - **How:** Standard Python types plus special ones for common formats.
> - **When to use:** Choosing the most precise type gives the best validation for free.

| Type | Accepts / validates |
|---|---|
| `int`, `float`, `str`, `bool` | Basic types (with sensible coercion) |
| `list[str]`, `dict[str, int]`, `set[int]`, `tuple[int, int]` | Collections with element types |
| `datetime`, `date`, `time`, `timedelta` | ISO strings like `"2026-09-27T10:00:00"` |
| `UUID` | UUID strings |
| `Decimal` | Exact decimals (money) |
| `EmailStr` | Valid email address (needs `pydantic[email]`) |
| `HttpUrl`, `AnyUrl` | Valid URLs |
| `SecretStr` | Hidden when printed (`**********`) |
| `Path` | File system paths |
| `Literal["a", "b"]` | Only these exact values |
| `X \| None` | X or None |
| `Any` | Anything (no validation) |

## 3. Optional Fields and Defaults

> - **What:** Fields that may be missing or empty.
> - **How:** A default value makes a field optional; `X | None = None` allows missing and null.
> - **When to use:** Partial updates, optional metadata, LLM outputs where a value may not exist.

```python
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str                              # required
    description: str | None = None         # optional, may be null
    tags: list[str] = []                   # safe in Pydantic (copied per instance)
    quantity: int = 1
    created: datetime = Field(default_factory=datetime.now)   # computed at creation
```

Required vs optional is decided by the **default**, not by `| None`: `x: int | None` without a default is still required (but may be `null`).

## 4. Field Constraints

> - **What:** Extra rules on values: ranges, lengths, patterns.
> - **How:** `Field(...)` with keyword arguments, or `Annotated[type, Field(...)]` for reusable types.
> - **When to use:** Prices >= 0, names not empty, codes matching a pattern.

```python
from typing import Annotated

from pydantic import BaseModel, Field

Percent = Annotated[float, Field(ge=0, le=100)]      # reusable constrained type


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Product name")
    price: float = Field(gt=0)
    discount: Percent = 0
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$")
    tags: list[str] = Field(default_factory=list, max_length=10)
```

| Keyword | Meaning |
|---|---|
| `gt`, `ge`, `lt`, `le` | `>`, `>=`, `<`, `<=` |
| `min_length`, `max_length` | Length of strings / lists |
| `pattern` | Regex the string must match |
| `multiple_of` | Number must be a multiple |
| `default`, `default_factory` | Default value / function producing it |
| `description`, `examples`, `title` | Documentation (shown in JSON Schema, FastAPI docs, LLM tool schemas) |

## 5. Nested Models and Lists

> - **What:** Models inside models, for tree-shaped data.
> - **How:** Use a model as a field type; dicts are converted into model instances automatically.
> - **When to use:** Orders with line items, API responses with nested objects, complex LLM outputs.

```python
class Address(BaseModel):
    street: str
    city: str


class LineItem(BaseModel):
    sku: str
    qty: int = Field(ge=1)


class Order(BaseModel):
    id: int
    shipping: Address
    items: list[LineItem]


order = Order.model_validate({
    "id": 1,
    "shipping": {"street": "Main 1", "city": "Berlin"},
    "items": [{"sku": "ABC-0001", "qty": 2}],
})
order.items[0].qty          # 2
```

## 6. Validation Errors

> - **What:** What happens when data does not match.
> - **How:** Pydantic raises `ValidationError` listing every problem with its location and message.
> - **When to use:** Returning helpful errors to users, re-asking an LLM to fix its output.

```python
from pydantic import ValidationError

try:
    Product(name="", price=-5, sku="bad")
except ValidationError as e:
    print(e.error_count())       # 3
    for err in e.errors():
        print(err["loc"], err["msg"])
    # ('name',) String should have at least 1 character
    # ('price',) Input should be greater than 0
    # ('sku',) String should match pattern '^[A-Z]{3}-\d{4}$'
```

FastAPI turns this automatically into a 422 response.

## 7. Custom Validators

> - **What:** Your own checking / cleaning logic.
> - **How:** `@field_validator` for one field; `@model_validator` for rules that involve several fields.
> - **When to use:** Normalising text, cross-field rules (end date after start date).

```python
from pydantic import BaseModel, field_validator, model_validator


class Booking(BaseModel):
    guest: str
    start: date
    end: date

    @field_validator("guest")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("guest must not be empty")
        return v.title()

    @model_validator(mode="after")
    def check_dates(self) -> "Booking":
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self
```

`mode="before"` runs on raw input before type conversion (for example to split a comma-separated string into a list).

## 8. Serialization (dump)

> - **What:** Turning a model back into a dict or JSON string.
> - **How:** `model_dump()` -> dict, `model_dump_json()` -> str; options to include / exclude fields.
> - **When to use:** Returning API responses, saving to files / databases, sending to LLMs.

```python
order.model_dump()                          # dict (nested models become dicts)
order.model_dump_json(indent=2)             # JSON string
order.model_dump(exclude={"id"})            # leave out fields
order.model_dump(include={"items"})         # only some fields
order.model_dump(exclude_none=True)         # drop None values
order.model_dump(exclude_unset=True)        # only fields that were explicitly set (PATCH)
order.model_dump(by_alias=True)             # use JSON aliases
order.model_dump(mode="json")               # dict with JSON-safe values (datetime -> str)
order.model_copy(update={"id": 2})          # copy with changes
```

## 9. Parsing JSON and Dicts

> - **What:** Creating models from dicts or raw JSON text.
> - **How:** `model_validate(dict)` or `model_validate_json(str)` (faster than `json.loads` + validate).
> - **When to use:** API responses, LLM JSON, files.

```python
user = User.model_validate({"id": 1, "name": "Ana"})
user = User.model_validate_json('{"id": 1, "name": "Ana"}')

users = [User.model_validate(row) for row in rows]

with open("user.json", encoding="utf-8") as f:
    user = User.model_validate_json(f.read())
```

## 10. JSON Schema

> - **What:** An automatically generated description of the model.
> - **How:** `model_json_schema()` returns a dict following the JSON Schema standard, including descriptions and constraints.
> - **When to use:** LLM tool definitions, structured output schemas, API documentation.

```python
class WeatherQuery(BaseModel):
    """Get the weather for a city."""

    city: str = Field(description="City name, e.g. Berlin")
    days: int = Field(1, ge=1, le=7, description="Forecast length")

WeatherQuery.model_json_schema()
# {'description': 'Get the weather for a city.',
#  'properties': {'city': {'description': 'City name, e.g. Berlin', 'title': 'City', 'type': 'string'},
#                 'days': {'default': 1, 'maximum': 7, 'minimum': 1, ...}},
#  'required': ['city'], 'title': 'WeatherQuery', 'type': 'object'}
```

Good `description`s matter: the LLM reads them to decide how to fill the fields.

## 11. Model Configuration

> - **What:** Settings that change how a model behaves.
> - **How:** `model_config = ConfigDict(...)` inside the class.
> - **When to use:** Rejecting unknown fields, immutability, reading from ORM objects.

```python
from pydantic import BaseModel, ConfigDict


class Strict(BaseModel):
    model_config = ConfigDict(
        extra="forbid",               # unknown fields -> error ("ignore" is default, "allow" keeps them)
        frozen=True,                  # immutable (and hashable)
        str_strip_whitespace=True,    # trim strings
        strict=False,                 # True = no coercion ("42" stays invalid for int)
        from_attributes=True,         # build from objects (SQLAlchemy rows): Model.model_validate(row)
        populate_by_name=True,        # accept field name as well as alias
    )
```

## 12. Enums and Literals

> - **What:** Restricting a field to a fixed set of values.
> - **How:** `Literal[...]` for simple cases; `Enum` when you want a named, reusable type.
> - **When to use:** Status fields, categories, LLM classification labels.

```python
from enum import Enum
from typing import Literal


class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class Review(BaseModel):
    sentiment: Sentiment
    priority: Literal["low", "medium", "high"]


Review(sentiment="positive", priority="high").sentiment    # <Sentiment.positive: 'positive'>
```

## 13. Aliases (Different Names in JSON)

> - **What:** Using one name in Python and another in JSON.
> - **How:** `Field(alias=...)`, or an `alias_generator` for all fields (e.g. camelCase).
> - **When to use:** External APIs that use `camelCase` or names that are Python keywords.

```python
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class ApiUser(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_id: int
    first_name: str


u = ApiUser.model_validate({"userId": 1, "firstName": "Ana"})
u.model_dump(by_alias=True)              # {'userId': 1, 'firstName': 'Ana'}
```

## 14. Computed Fields

> - **What:** Read-only values derived from other fields, included in output.
> - **How:** `@computed_field` on a `@property`.
> - **When to use:** Totals, full names, derived flags you want in the JSON output.

```python
from pydantic import computed_field


class Cart(BaseModel):
    prices: list[float]

    @computed_field
    @property
    def total(self) -> float:
        return round(sum(self.prices), 2)


Cart(prices=[1.5, 2.25]).model_dump()     # {'prices': [1.5, 2.25], 'total': 3.75}
```

## 15. TypeAdapter (Validate Without a Model)

> - **What:** Validating plain types like `list[int]` or `dict[str, User]` without writing a model class.
> - **How:** Wrap the type in `TypeAdapter`, then call `validate_python` / `validate_json`.
> - **When to use:** Validating a list of models from an API, quick checks.

```python
from pydantic import TypeAdapter

users = TypeAdapter(list[User]).validate_json('[{"id": 1, "name": "Ana"}]')
TypeAdapter(list[User]).json_schema()
```

## 16. Settings from Environment (pydantic-settings)

> - **What:** A typed config object loaded from environment variables and `.env`.
> - **How:** Subclass `BaseSettings`; field names map to env var names (case-insensitive).
> - **When to use:** Every app with API keys, URLs or feature flags.

```powershell
pip install pydantic-settings
```

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    anthropic_api_key: SecretStr          # reads APP_ANTHROPIC_API_KEY
    llm_model: str = "claude-opus-5"
    max_tokens: int = 4096
    debug: bool = False                   # "true", "1", "yes" -> True


settings = Settings()                     # fails fast at startup if a required value is missing
settings.anthropic_api_key.get_secret_value()
```

## 17. Pydantic for LLM Structured Output

> - **What:** Getting LLM answers as validated Python objects instead of free text.
> - **How:** Define a model; the SDK sends its JSON Schema and parses the reply into the model.
> - **When to use:** Extraction, classification, any time code (not a human) reads the LLM output.

```python
import anthropic
from pydantic import BaseModel, Field


class Invoice(BaseModel):
    vendor: str
    total: float = Field(description="Total amount in EUR")
    due_date: date | None = None
    line_items: list[str]


client = anthropic.Anthropic()
response = client.messages.parse(
    model="claude-opus-5",
    max_tokens=16000,
    messages=[{"role": "user", "content": f"Extract the invoice data:\n\n{invoice_text}"}],
    output_format=Invoice,
)
invoice = response.parsed_output          # validated Invoice instance
```

More in [26 - LLM APIs](26_llm-apis.md) and [27 - Prompt Engineering](27_prompt-engineering.md).

## 18. Pydantic vs dataclass vs TypedDict

> - **What:** Three ways to describe structured data in Python.
> - **How:** They differ in whether data is validated at runtime.
> - **When to use:** Pydantic at boundaries (untrusted input); dataclasses for internal data; TypedDict to type plain dicts.

| | `BaseModel` | `@dataclass` | `TypedDict` |
|---|---|---|---|
| Runtime validation | Yes | No | No |
| Type conversion | Yes | No | No |
| JSON / Schema export | Built in | Manual | Manual |
| Speed / overhead | Small cost | Fastest | Plain dict |
| Best for | API input, LLM output, config | Internal objects | Typing existing dicts |

## 19. v1 to v2 Cheat Sheet

> - **What:** Renamed methods between Pydantic v1 and v2.
> - **How:** Old tutorials use v1 names; v2 (current) uses the `model_` prefix.
> - **When to use:** Reading older code or Stack Overflow answers.

| v1 | v2 |
|---|---|
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `.parse_obj(d)` | `.model_validate(d)` |
| `.parse_raw(s)` | `.model_validate_json(s)` |
| `.schema()` | `.model_json_schema()` |
| `.copy()` | `.model_copy()` |
| `@validator` | `@field_validator` |
| `@root_validator` | `@model_validator` |
| `class Config:` | `model_config = ConfigDict(...)` |
| `orm_mode = True` | `from_attributes=True` |
| `BaseSettings` in pydantic | `pip install pydantic-settings` |

## 20. Troubleshooting

| Error | Fix |
|---|---|
| `ValidationError: Field required` | Missing key in input, or give the field a default |
| `Input should be a valid integer` | Wrong type; check the data or use a looser type |
| `Extra inputs are not permitted` | `extra="forbid"` and an unknown key was sent |
| `AttributeError: 'X' object has no attribute 'dict'` | Pydantic v2: use `model_dump()` |
| `PydanticImportError: BaseSettings has been moved` | `pip install pydantic-settings`; import from `pydantic_settings` |
| `email-validator is not installed` | `pip install "pydantic[email]"` |
| Validator not running | Check the field name string in `@field_validator("...")` and `@classmethod` |
| `datetime` not JSON serializable | Use `model_dump_json()` or `model_dump(mode="json")` |
| Secret printed in logs | Use `SecretStr` and `.get_secret_value()` only where needed |
| Mutable default shared between instances (dataclass) | Pydantic copies defaults; for dataclasses use `field(default_factory=list)` |
