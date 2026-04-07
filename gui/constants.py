"""
gui/constants.py
Costanti condivise da tutta l'applicazione.
"""

FILTER_OPS = {
    "title": [
        ("Contiene", "contains"),
        ("Inizia con", "starts_with"),
        ("È uguale a", "equals_text"),
        ("È vuoto", "is_empty"),
        ("Non è vuoto", "is_not_empty"),
    ],
    "rich_text": [
        ("Contiene", "contains"),
        ("Inizia con", "starts_with"),
        ("Finisce con", "ends_with"),
        ("È uguale a", "equals_text"),
        ("È vuoto", "is_empty"),
        ("Non è vuoto", "is_not_empty"),
    ],
    "number": [
        ("=", "equals_number"),
        (">", "greater_than"),
        ("<", "less_than"),
        ("≥", "greater_than_or_equal_to"),
        ("≤", "less_than_or_equal_to"),
        ("È vuoto", "is_empty"),
        ("Non è vuoto", "is_not_empty"),
    ],
    "checkbox": [
        ("È vero", "equals_true"),
        ("È falso", "equals_false"),
    ],
    "select": [
        ("È uguale a", "equals"),
        ("È diverso da", "does_not_equal"),
        ("È vuoto", "is_empty"),
        ("Non è vuoto", "is_not_empty"),
    ],
    "multi_select": [
        ("Contiene", "contains"),
        ("Non contiene", "does_not_contain"),
        ("È vuoto", "is_empty"),
        ("Non è vuoto", "is_not_empty"),
    ],
    "status": [
        ("È uguale a", "equals"),
        ("È diverso da", "does_not_equal"),
    ],
    "date": [
        ("Dopo il", "after"),
        ("Prima del", "before"),
        ("Il o dopo il", "on_or_after"),
        ("Il o prima del", "on_or_before"),
        ("Settimana corrente", "this_week"),
        ("Settimana prossima", "next_week"),
        ("Mese scorso", "past_month"),
        ("È vuoto", "is_empty"),
    ],
    "url": [
        ("Contiene", "contains"),
        ("È uguale a", "equals_text"),
        ("È vuoto", "is_empty"),
    ],
    "email": [
        ("Contiene", "contains"),
        ("È uguale a", "equals_text"),
    ],
    "phone_number": [
        ("Contiene", "contains"),
    ],
}

FILTER_OPS_DEFAULT = [
    ("Contiene", "contains"),
    ("È uguale a", "equals_text"),
    ("È vuoto", "is_empty"),
    ("Non è vuoto", "is_not_empty"),
]

# Operatori che non richiedono un valore (es. "is_empty")
NO_VALUE_OPS = {
    "is_empty", "is_not_empty", "next_week", "this_week",
    "past_week", "past_month", "past_year", "next_month",
    "next_year", "equals_true", "equals_false",
}

# Tipi di colonna Notion scrivibili via API
WRITABLE_TYPES = {
    "title", "rich_text", "number", "checkbox", "select",
    "multi_select", "status", "date", "url", "email", "phone_number",
}
