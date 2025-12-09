class S:
    def __init__(self):
        self.sorts = []

    def get(self, *args):
        """
        Aggiunge più sort alla volta.
        Ogni argomento deve essere una tupla: (chiave, direzione)
        Esempio: ("Name", "ascending")
        """
        for key, direction in args:
            self.sorts.append({
                "property" if key not in ["created_time", "last_edited_time"] else "timestamp": key,
                "direction": "ascending" if direction else "descending"
            })
        return {"sorts": self.sorts}


class _PropertyFilter:
    def __init__(self, prop_name: str, prop_type: str):
        self.prop_name = prop_name
        self.prop_type = prop_type

    def _build(self, operator: str, value):
        return {
            "property": self.prop_name,
            self.prop_type: {operator: value}
        }


# ------------------ Filtri per tipo ------------------

class _CheckboxFilter(_PropertyFilter):
    def equals(self, value: bool):
        return self._build("equals", value)

    def does_not_equal(self, value: bool):
        return self._build("does_not_equal", value)


class _DateFilter(_PropertyFilter):
    def equals_date(self, date_str: str):
        return self._build("equals", date_str)

    def after(self, date_str: str):
        return self._build("after", date_str)

    def before(self, date_str: str):
        return self._build("before", date_str)

    def on_or_after(self, date_str: str):
        return self._build("on_or_after", date_str)

    def on_or_before(self, date_str: str):
        return self._build("on_or_before", date_str)

    def is_empty(self):
        return self._build("is_empty", True)

    def is_not_empty(self):
        return self._build("is_not_empty", True)

    def next_week(self):
        return self._build("next_week", {})

    def next_month(self):
        return self._build("next_month", {})

    def next_year(self):
        return self._build("next_year", {})

    def past_week(self):
        return self._build("past_week", {})

    def past_month(self):
        return self._build("past_month", {})

    def past_year(self):
        return self._build("past_year", {})

    def this_week(self):
        return self._build("this_week", {})


class _FilesFilter(_PropertyFilter):
    def is_empty(self):
        return self._build("is_empty", True)

    def is_not_empty(self):
        return self._build("is_not_empty", True)


class _IDFilter(_PropertyFilter):
    def equals(self, value: int):
        return self._build("equals", value)

    def does_not_equal(self, value: int):
        return self._build("does_not_equal", value)

    def greater_than(self, value: int):
        return self._build("greater_than", value)

    def greater_than_or_equal_to(self, value: int):
        return self._build("greater_than_or_equal_to", value)

    def less_than(self, value: int):
        return self._build("less_than", value)

    def less_than_or_equal_to(self, value: int):
        return self._build("less_than_or_equal_to", value)


class _NumberFilter(_PropertyFilter):
    def equals_number(self, value: float):
        return self._build("equals", value)

    def disequals_number(self, value: float):
        return self._build("does_not_equal", value)

    def greater_than(self, value: float):
        return self._build("greater_than", value)

    def greater_than_or_equal_to(self, value: float):
        return self._build("greater_than_or_equal_to", value)

    def less_than(self, value: float):
        return self._build("less_than", value)

    def less_than_or_equal_to(self, value: float):
        return self._build("less_than_or_equal_to", value)

    def is_empty(self):
        return self._build("is_empty", True)

    def is_not_empty(self):
        return self._build("is_not_empty", True)


class _PeopleFilter(_PropertyFilter):
    def contains(self, value: str):
        return self._build("contains", value)

    def does_not_contain(self, value: str):
        return self._build("does_not_contain", value)

    def is_empty(self):
        return self._build("is_empty", True)

    def is_not_empty(self):
        return self._build("is_not_empty", True)


class _RelationFilter(_PropertyFilter):
    def contains(self, value: str):
        return self._build("contains", value)

    def does_not_contain(self, value: str):
        return self._build("does_not_contain", value)

    def is_empty(self):
        return self._build("is_empty", True)

    def is_not_empty(self):
        return self._build("is_not_empty", True)


class _RollupFilter(_PropertyFilter):
    basic_structure = {
        "rich_text": {
            "contains": ""
        }
    }

    def any(self, text: str):
        self.basic_structure['rich_text']['contains'] = text
        return self._build("any", self.basic_structure)

    def every(self, text: str):
        self.basic_structure['rich_text']['contains'] = text
        return self._build("every", self.basic_structure)

    def none(self, text: str):
        self.basic_structure['rich_text']['contains'] = text
        return self._build("none", self.basic_structure)


class _SelectFilter(_PropertyFilter):
    def equals(self, value: str):
        return self._build("equals", value)

    def does_not_equal(self, value: str):
        return self._build("does_not_equal", value)

    def is_empty(self):
        return self._build("is_empty", True)

    def is_not_empty(self):
        return self._build("is_not_empty", True)


class _StatusFilter(_PropertyFilter):
    def equals(self, value: str):
        return self._build("equals", value)

    def does_not_equal(self, value: str):
        return self._build("does_not_equal", value)

    def is_empty(self):
        return self._build("is_empty", True)

    def is_not_empty(self):
        return self._build("is_not_empty", True)


class _TextFilter(_PropertyFilter):
    def contains(self, value: str):
        return self._build("contains", value)

    def does_not_contain(self, value: str):
        return self._build("does_not_contain", value)

    def equals_text(self, value: str):
        return self._build("equals", value)

    def does_not_equal(self, value: str):
        return self._build("does_not_equal", value)

    def starts_with(self, value: str):
        return self._build("starts_with", value)

    def ends_with(self, value: str):
        return self._build("ends_with", value)

    def is_empty(self):
        return self._build("is_empty", True)

    def is_not_empty(self):
        return self._build("is_not_empty", True)


class _TimestampFilter:
    def __init__(self, timestamp_type: str):
        self.timestamp_type = timestamp_type

    def _build(self, operator: str, value):
        return {
            "timestamp": self.timestamp_type,
            self.timestamp_type: {operator: value}
        }

    # date operators
    def equals(self, date_str: str):
        return self._build("equals", date_str)

    def before(self, date_str: str):
        return self._build("before", date_str)

    def after(self, date_str: str):
        return self._build("after", date_str)

    def on_or_before(self, date_str: str):
        return self._build("on_or_before", date_str)

    def on_or_after(self, date_str: str):
        return self._build("on_or_after", date_str)

    def is_empty(self):
        return self._build("is_empty", True)

    def is_not_empty(self):
        return self._build("is_not_empty", True)


class _VerificationFilter(_PropertyFilter):
    def status(self, value: str):  # "verified", "expired", "none"
        return self._build("status", value)


# ------------------ Factory ------------------
class F:
    """Factory semplificata per creare filtri Notion senza scrivere JSON."""

    @staticmethod
    def checkbox(name: str):
        return _CheckboxFilter(name, "checkbox")

    @staticmethod
    def notion_id(name: str):
        return _IDFilter(name, "ID")

    @staticmethod
    def number(name: str):
        return _NumberFilter(name, "number")

    @staticmethod
    def date(name: str):
        return _DateFilter(name, "date")

    @staticmethod
    def files(name: str):
        return _FilesFilter(name, "files")

    @staticmethod
    def rich_text(name: str):
        return _TextFilter(name, "rich_text")

    @staticmethod
    def multi_select(name: str):
        return _TextFilter(name, "multi_select")

    @staticmethod
    def people(name: str):
        return _PeopleFilter(name, "people")

    @staticmethod
    def relation(name: str):
        return _RelationFilter(name, "relation")

    @staticmethod
    def rollup(name: str):
        return _RollupFilter(name, "rollup")

    @staticmethod
    def select(name: str):
        return _SelectFilter(name, "select")

    @staticmethod
    def status(name: str):
        return _StatusFilter(name, "status")

    @staticmethod
    def timestamp(timestamp_type: str):  # "created_time" o "last_edited_time"
        return _TimestampFilter(timestamp_type)

    @staticmethod
    def verification(name: str):
        return _VerificationFilter(name, "verification")

    # compound
    @staticmethod
    def and_(*filters):
        return {"and": list(filters)}

    @staticmethod
    def or_(*filters):
        return {"or": list(filters)}


if __name__ == "__main__":
    # Checkbox
    checkbox_f = {
        "filter": F.checkbox("Done").equals(True)
    }
    print(checkbox_f)

    # ID
    id_f = {
        "filter": F.notion_id("unique_id").greater_than(42)
    }
    print(id_f)

    # Number
    number_f = {
        "filter": F.number("Score").less_than_or_equal_to(100)
    }
    print(number_f)

    # Date
    date_f = {
        "filter": F.date("Deadline").on_or_after("2025-12-01")
    }
    print(date_f)

    # Files
    files_f = {
        "filter": F.files("Attachments").is_not_empty()
    }
    print(files_f)

    # Rich Text
    text_f = {
        "filter": F.rich_text("Description").contains("urgent")
    }
    print(text_f)

    # Multi-select
    multi_f = {
        "filter": F.multi_select("Tags").contains("Important")
    }
    print(multi_f)

    # People
    people_f = {
        "filter": F.people("Assignee").is_not_empty()
    }
    print(people_f)

    # Relation
    relation_f = {
        "filter": F.relation("Project").contains("Alpha")
    }
    print(relation_f)

    # Rollup
    rollup_f = {
        "filter": F.rollup("Tasks").any("Complete")
    }
    print(rollup_f)

    # Select
    select_f = {
        "filter": F.select("Priority").equals("High")
    }
    print(select_f)

    # Status
    status_f = {
        "filter": F.status("Progress").does_not_equal("Done")
    }
    print(status_f)

    # Timestamp
    timestamp_f = {
        "filter": F.timestamp("created_time").on_or_before("2025-12-01")
    }
    print(timestamp_f)

    # Verification
    verification_f = {
        "filter": F.verification("verification").status("verified")
    }
    print(verification_f)

    # Compound AND
    and_f = {
        "filter": F.and_(
            F.checkbox("Done").equals(True),
            F.multi_select("Tags").contains("Urgent")
        )
    }
    print(and_f)

    # Compound OR
    or_f = {
        "filter": F.or_(
            F.select("Status").equals("Open"),
            F.select("Status").equals("Pending")
        )
    }
    print(or_f)

    # Compound AND + OR
    and_or_f = {
        "filter": F.and_(
            F.checkbox("Done").equals(True),
            F.or_(
                F.multi_select("Tags").contains("A"),
                F.multi_select("Tags").contains("B")
            )
        )
    }
    print(and_or_f)

    s = S().get(
                ("Name", "ascending"),
                ("created_time", "descending"),
                ("Food group", "descending")
            )

    print(s)
