from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from notion_lib.nTypes.rich_text import NRichList, simple_rich_text_list, create_rich_list
from notion_lib.nTypes.primitives import NDate


# ──────────────────────────────────────────────
# Base
# ──────────────────────────────────────────────

class PropertyValue(ABC):
    prop_type: str = ""

    def __init__(self, name: str, prop_id: str, data: dict):
        self.name = name
        self.prop_id = prop_id
        self._data = data

    @classmethod
    @abstractmethod
    def from_data(cls, name: str, prop_id: str, data: dict) -> "PropertyValue":
        pass

    @abstractmethod
    def to_payload(self) -> dict:
        pass

    @property
    @abstractmethod
    def value(self):
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}': {self.value}>"


class ReadOnlyProperty(PropertyValue):
    """Base per proprietà non scrivibili via API."""

    def to_payload(self) -> dict:
        raise AttributeError(
            f"Property '{self.name}' ({self.prop_type}) is read-only."
        )

    @property
    def value(self):
        return None

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict) -> "PropertyValue":
        return cls(name, prop_id, data)


# ──────────────────────────────────────────────
# Writable
# ──────────────────────────────────────────────

class TitleProperty(PropertyValue):
    prop_type = "title"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._rich_list: NRichList = create_rich_list(data.get("title", []))

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> str:
        return self._rich_list.text

    @value.setter
    def value(self, text: str):
        self._rich_list = simple_rich_text_list(text)

    def to_payload(self) -> dict:
        return {self.name: {"title": self._rich_list.to_dict()}}


class RichTextProperty(PropertyValue):
    prop_type = "rich_text"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._rich_list: NRichList = create_rich_list(data.get("rich_text", []))

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> str:
        return self._rich_list.text

    @value.setter
    def value(self, text: str):
        self._rich_list = simple_rich_text_list(text)

    def to_payload(self) -> dict:
        return {self.name: {"rich_text": self._rich_list.to_dict()}}


class NumberProperty(PropertyValue):
    prop_type = "number"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._value: Optional[float] = data.get("number")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[float]:
        return self._value

    @value.setter
    def value(self, v: Optional[float]):
        self._value = v

    def to_payload(self) -> dict:
        return {self.name: {"number": self._value}}


class CheckboxProperty(PropertyValue):
    prop_type = "checkbox"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._value: bool = data.get("checkbox", False)

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, v: bool):
        self._value = bool(v)

    def to_payload(self) -> dict:
        return {self.name: {"checkbox": self._value}}


class SelectProperty(PropertyValue):
    prop_type = "select"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        sel = data.get("select") or {}
        self._value: Optional[str] = sel.get("name")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[str]:
        return self._value

    @value.setter
    def value(self, v: Optional[str]):
        self._value = v

    def to_payload(self) -> dict:
        return {self.name: {"select": {"name": self._value} if self._value else None}}


class MultiSelectProperty(PropertyValue):
    prop_type = "multi_select"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._value: list[str] = [
            item.get("name", "") for item in data.get("multi_select", [])
        ]

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> list[str]:
        return self._value

    @value.setter
    def value(self, names: list[str]):
        self._value = list(names)

    def to_payload(self) -> dict:
        return {self.name: {"multi_select": [{"name": n} for n in self._value]}}


class StatusProperty(PropertyValue):
    prop_type = "status"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        st = data.get("status") or {}
        self._value: Optional[str] = st.get("name")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[str]:
        return self._value

    @value.setter
    def value(self, v: Optional[str]):
        self._value = v

    def to_payload(self) -> dict:
        return {self.name: {"status": {"name": self._value} if self._value else None}}


class DateProperty(PropertyValue):
    prop_type = "date"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        d = data.get("date") or {}
        self._start: Optional[NDate] = NDate(d["start"]) if d.get("start") else None
        self._end: Optional[NDate] = NDate(d["end"]) if d.get("end") else None
        self._time_zone: Optional[str] = d.get("time_zone")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[NDate]:
        return self._start

    @property
    def start(self) -> Optional[NDate]:
        return self._start

    @start.setter
    def start(self, v: Optional[NDate]):
        self._start = v

    @property
    def end(self) -> Optional[NDate]:
        return self._end

    @end.setter
    def end(self, v: Optional[NDate]):
        self._end = v

    def to_payload(self) -> dict:
        if self._start is None:
            return {self.name: {"date": None}}
        d: dict = {"start": self._start.to_dict()}
        if self._end:
            d["end"] = self._end.to_dict()
        if self._time_zone:
            d["time_zone"] = self._time_zone
        return {self.name: {"date": d}}


class URLProperty(PropertyValue):
    prop_type = "url"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._value: Optional[str] = data.get("url")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[str]:
        return self._value

    @value.setter
    def value(self, v: Optional[str]):
        self._value = v

    def to_payload(self) -> dict:
        return {self.name: {"url": self._value}}


class EmailProperty(PropertyValue):
    prop_type = "email"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._value: Optional[str] = data.get("email")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[str]:
        return self._value

    @value.setter
    def value(self, v: Optional[str]):
        self._value = v

    def to_payload(self) -> dict:
        return {self.name: {"email": self._value}}


class PhoneNumberProperty(PropertyValue):
    prop_type = "phone_number"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._value: Optional[str] = data.get("phone_number")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[str]:
        return self._value

    @value.setter
    def value(self, v: Optional[str]):
        self._value = v

    def to_payload(self) -> dict:
        return {self.name: {"phone_number": self._value}}


class RelationProperty(PropertyValue):
    prop_type = "relation"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._ids: list[str] = [r.get("id", "") for r in data.get("relation", [])]

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> list[str]:
        return self._ids

    @value.setter
    def value(self, ids: list[str]):
        self._ids = list(ids)

    def to_payload(self) -> dict:
        return {self.name: {"relation": [{"id": i} for i in self._ids]}}


class PeopleProperty(PropertyValue):
    prop_type = "people"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._ids: list[str] = [p.get("id", "") for p in data.get("people", [])]

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> list[str]:
        return self._ids

    @value.setter
    def value(self, ids: list[str]):
        self._ids = list(ids)

    def to_payload(self) -> dict:
        return {self.name: {"people": [{"object": "user", "id": i} for i in self._ids]}}


# ──────────────────────────────────────────────
# Read-only
# ──────────────────────────────────────────────

class FilesProperty(ReadOnlyProperty):
    prop_type = "files"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._files: list = data.get("files", [])

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> list:
        return self._files


class FormulaProperty(ReadOnlyProperty):
    prop_type = "formula"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        f = data.get("formula", {})
        self._formula_type: Optional[str] = f.get("type")
        self._value = f.get(self._formula_type) if self._formula_type else None

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self):
        return self._value

    @property
    def formula_type(self) -> Optional[str]:
        return self._formula_type


class RollupProperty(ReadOnlyProperty):
    prop_type = "rollup"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        r = data.get("rollup", {})
        self._rollup_type: Optional[str] = r.get("type")
        self._value = r.get(self._rollup_type) if self._rollup_type else None

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self):
        return self._value


class UniqueIDProperty(ReadOnlyProperty):
    prop_type = "unique_id"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        uid = data.get("unique_id", {})
        self._number: Optional[int] = uid.get("number")
        self._prefix: Optional[str] = uid.get("prefix")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[int]:
        return self._number

    @property
    def prefix(self) -> Optional[str]:
        return self._prefix

    def __repr__(self):
        p = f"{self._prefix}-" if self._prefix else ""
        return f"<UniqueIDProperty '{self.name}': {p}{self._number}>"


class CreatedTimeProperty(ReadOnlyProperty):
    prop_type = "created_time"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        raw = data.get("created_time")
        self._value: Optional[NDate] = NDate(raw) if raw else None

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[NDate]:
        return self._value


class LastEditedTimeProperty(ReadOnlyProperty):
    prop_type = "last_edited_time"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        raw = data.get("last_edited_time")
        self._value: Optional[NDate] = NDate(raw) if raw else None

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[NDate]:
        return self._value


class CreatedByProperty(ReadOnlyProperty):
    prop_type = "created_by"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._user_id: Optional[str] = data.get("created_by", {}).get("id")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[str]:
        return self._user_id


class LastEditedByProperty(ReadOnlyProperty):
    prop_type = "last_edited_by"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        self._user_id: Optional[str] = data.get("last_edited_by", {}).get("id")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[str]:
        return self._user_id


# ──────────────────────────────────────────────
# Tipi mancanti (prima causavano ValueError nel registry)
# ──────────────────────────────────────────────

class VerificationProperty(ReadOnlyProperty):
    """
    Stato di verifica di una pagina.
    Valori possibili: "verified", "unverified".
    Non modificabile via API.
    """
    prop_type = "verification"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        v = data.get("verification") or {}
        self._state: Optional[str] = v.get("state")
        self._verified_by: Optional[str] = (v.get("verified_by") or {}).get("id")
        self._date: Optional[NDate] = NDate(v["date"]["start"]) if v.get("date") else None

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[str]:
        return self._state

    @property
    def verified_by(self) -> Optional[str]:
        return self._verified_by

    @property
    def date(self) -> Optional[NDate]:
        return self._date


class ButtonProperty(ReadOnlyProperty):
    """
    Proprietà di tipo button. Non ha valore leggibile né scrivibile via API.
    """
    prop_type = "button"

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self):
        return None


class LocationProperty(ReadOnlyProperty):
    """
    Proprietà di tipo location (latitudine/longitudine).
    Non scrivibile via API pubblica.
    """
    prop_type = "location"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        loc = data.get("location") or {}
        self._latitude: Optional[float] = loc.get("latitude")
        self._longitude: Optional[float] = loc.get("longitude")

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self):
        return {"latitude": self._latitude, "longitude": self._longitude}

    @property
    def latitude(self) -> Optional[float]:
        return self._latitude

    @property
    def longitude(self) -> Optional[float]:
        return self._longitude


class PlaceProperty(ReadOnlyProperty):
    """Proprietà di tipo place. Read-only."""
    prop_type = "place"

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self):
        return self._data.get("place")


class LastVisitedTimeProperty(ReadOnlyProperty):
    """Ultimo accesso alla pagina. Read-only."""
    prop_type = "last_visited_time"

    def __init__(self, name: str, prop_id: str, data: dict):
        super().__init__(name, prop_id, data)
        raw = data.get("last_visited_time")
        self._value: Optional[NDate] = NDate(raw) if raw else None

    @classmethod
    def from_data(cls, name: str, prop_id: str, data: dict):
        return cls(name, prop_id, data)

    @property
    def value(self) -> Optional[NDate]:
        return self._value


# ──────────────────────────────────────────────
# Registry & Factory
# ──────────────────────────────────────────────

_PROP_REGISTRY: dict[str, type[PropertyValue]] = {
    "title":              TitleProperty,
    "rich_text":          RichTextProperty,
    "number":             NumberProperty,
    "checkbox":           CheckboxProperty,
    "select":             SelectProperty,
    "multi_select":       MultiSelectProperty,
    "status":             StatusProperty,
    "date":               DateProperty,
    "url":                URLProperty,
    "email":              EmailProperty,
    "phone_number":       PhoneNumberProperty,
    "relation":           RelationProperty,
    "people":             PeopleProperty,
    "files":              FilesProperty,
    "formula":            FormulaProperty,
    "rollup":             RollupProperty,
    "unique_id":          UniqueIDProperty,
    "created_time":       CreatedTimeProperty,
    "last_edited_time":   LastEditedTimeProperty,
    "created_by":         CreatedByProperty,
    "last_edited_by":     LastEditedByProperty,
    # Tipi precedentemente mancanti → non più ValueError
    "verification":       VerificationProperty,
    "button":             ButtonProperty,
    "location":           LocationProperty,
    "place":              PlaceProperty,
    "last_visited_time":  LastVisitedTimeProperty,
}


class PropertyFactory:
    @staticmethod
    def from_data(name: str, data: dict) -> PropertyValue:
        prop_type = data.get("type", "")
        prop_id = data.get("id", "")
        cls = _PROP_REGISTRY.get(prop_type)
        if cls is None:
            raise ValueError(
                f"Tipo proprietà sconosciuto: '{prop_type}' per '{name}'. "
                f"Tipi supportati: {sorted(_PROP_REGISTRY)}"
            )
        return cls.from_data(name, prop_id, data)