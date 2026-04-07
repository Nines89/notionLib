"""
gui/state.py
Stato globale dell'applicazione.
Un singleton AppState condiviso da tutti i componenti via get_state().
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class FilterRow:
    """Rappresenta una riga di filtro (colonna + operatore + valore)."""
    col: str = ""
    op:  str = "contains"
    val: Any = None


@dataclass
class SortRow:
    """Rappresenta un criterio di ordinamento (colonna + direzione)."""
    col: str = ""
    asc: bool = True


@dataclass
class AppState:
    # ── Connessione ──────────────────────────────────────────────
    api:         Any            = None
    bot_name:    str            = ""
    databases:   list           = field(default_factory=list)   # oggetti DB grezzi
    datasources: list           = field(default_factory=list)   # list[dict] id/name/pid/ptitle
    pages:       dict           = field(default_factory=dict)   # page_id -> {id, title}
    ds_schemas:  dict           = field(default_factory=dict)   # ds_id -> schema dict

    # ── Configurazione automazione ────────────────────────────────
    auto_name:   str            = "Nuova automazione"
    auto_src_id: Optional[str]  = None
    auto_tgt_id: Optional[str]  = None
    filter_rows: list           = field(default_factory=list)   # list[FilterRow]
    sort_rows:   list           = field(default_factory=list)   # list[SortRow]
    col_map:     dict           = field(default_factory=dict)   # tgt_col -> src_col

    # ── Output ───────────────────────────────────────────────────
    generated_code: str         = ""
    run_log:        list        = field(default_factory=list)


_state = AppState()


def get_state() -> AppState:
    return _state


def reset_state() -> None:
    """Resetta tutto lo stato (usato alla disconnessione)."""
    global _state
    _state = AppState()
