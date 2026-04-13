"""
Northwind schema metadata okuyucu.

Desteklenen kaynak yapılar:
1) tables = dict
2) tables = list
3) columns = dict
4) columns = list
5) foreign_keys = dict / list
6) top-level relationships = list

Amaç:
Kişi 1'in ürettiği metadata formatını,
Kişi 2'nin context_builder.py dosyasının beklediği yapıya
tek bir uyumluluk katmanında normalize etmek.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _default_metadata_path() -> Path:
    d = Path(__file__).resolve().parent
    prod = d / "metadata/schema_metadata.json"
    gecici = d / "schema_metadata_gecici.json"
    if prod.exists():
        return prod
    if gecici.exists():
        return gecici
    return prod


def _normalize_table_name(name: str) -> str:
    n = (name or "").strip().lower()
    if n.startswith("public."):
        n = n[7:]
    return n


def _normalize_alias(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _normalize_column_name(name: Any) -> str:
    s = str(name or "").strip()
    if not s:
        return ""
    parts = [p.strip() for p in s.split(".") if p.strip()]
    return parts[-1] if parts else ""


def _normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        candidates = [value]
    elif isinstance(value, (list, tuple, set)):
        candidates = list(value)
    else:
        return []

    out: list[str] = []
    seen: set[str] = set()

    for item in candidates:
        s = str(item or "").strip()
        key = _normalize_alias(s)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(s)

    return out


def _normalize_primary_keys(value: Any) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()

    for item in _normalize_string_list(value):
        col = _normalize_column_name(item)
        key = col.lower()
        if not col or key in seen:
            continue
        seen.add(key)
        out.append(col)

    return out


def _split_table_column_ref(value: Any) -> tuple[str | None, str | None]:
    s = str(value or "").strip()
    if not s:
        return None, None

    parts = [p.strip() for p in s.split(".") if p.strip()]
    if len(parts) < 2:
        return None, None

    table = _normalize_table_name(".".join(parts[:-1]))
    column = _normalize_column_name(parts[-1])

    if not table or not column:
        return None, None

    return table, column


def _normalize_ref_string(value: Any) -> str:
    table, col = _split_table_column_ref(value)
    if not table or not col:
        return ""
    return f"{table}.{col}"


def _column_text_from_meta(meta: Any) -> str:
    if isinstance(meta, dict):
        return str(meta.get("description") or meta.get("type") or "").strip()
    return str(meta or "").strip()


def _normalize_column_map(columns: Any) -> dict[str, str]:
    out: dict[str, str] = {}

    if isinstance(columns, dict):
        for raw_name, raw_meta in columns.items():
            name = _normalize_column_name(raw_name)
            if not name:
                continue
            out[name] = _column_text_from_meta(raw_meta)
        return out

    if isinstance(columns, list):
        for item in columns:
            if isinstance(item, dict):
                name = _normalize_column_name(item.get("name") or item.get("column"))
                if not name:
                    continue
                out[name] = _column_text_from_meta(item)
            else:
                name = _normalize_column_name(item)
                if not name:
                    continue
                out[name] = ""
        return out

    return out


def _normalize_foreign_keys(foreign_keys: Any) -> dict[str, str]:
    out: dict[str, str] = {}

    if isinstance(foreign_keys, dict):
        for raw_col, raw_ref in foreign_keys.items():
            col = _normalize_column_name(raw_col)
            ref = _normalize_ref_string(raw_ref)
            if not col or not ref:
                continue
            out[col] = ref
        return out

    if isinstance(foreign_keys, list):
        for item in foreign_keys:
            if not isinstance(item, dict):
                continue
            col = _normalize_column_name(
                item.get("column") or item.get("name") or item.get("from_column")
            )
            ref = _normalize_ref_string(
                item.get("references")
                or item.get("reference")
                or item.get("ref")
                or item.get("to")
            )
            if not col or not ref:
                continue
            out[col] = ref
        return out

    return out


def _normalize_single_table_meta(table_name: str, meta: Any) -> dict[str, Any]:
    src = meta if isinstance(meta, dict) else {}
    normalized_name = _normalize_table_name(src.get("name") or table_name)

    normalized = dict(src)
    normalized["name"] = normalized_name
    normalized["description"] = str(src.get("description") or "").strip()
    normalized["aliases"] = _normalize_string_list(src.get("aliases"))
    normalized["primary_key"] = _normalize_primary_keys(src.get("primary_key"))
    normalized["columns"] = _normalize_column_map(src.get("columns"))
    normalized["foreign_keys"] = _normalize_foreign_keys(src.get("foreign_keys"))

    return normalized


def _normalize_tables(raw_tables: Any) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}

    if isinstance(raw_tables, dict):
        items = raw_tables.items()
    elif isinstance(raw_tables, list):
        items = []
        for entry in raw_tables:
            if not isinstance(entry, dict):
                continue
            name = entry.get("name")
            if not name:
                continue
            items.append((name, entry))
    else:
        return normalized

    for raw_name, raw_meta in items:
        if isinstance(raw_meta, dict):
            table_name = _normalize_table_name(raw_meta.get("name") or raw_name)
        else:
            table_name = _normalize_table_name(str(raw_name))

        if not table_name:
            continue

        normalized[table_name] = _normalize_single_table_meta(table_name, raw_meta)

    return normalized


def _apply_relationships_to_tables(
    tables: dict[str, dict[str, Any]],
    relationships: Any,
) -> None:
    if not isinstance(relationships, list):
        return

    for rel in relationships:
        if not isinstance(rel, dict):
            continue

        from_table, from_col = _split_table_column_ref(rel.get("from"))
        to_table, to_col = _split_table_column_ref(rel.get("to"))

        if not from_table or not from_col or not to_table or not to_col:
            continue

        table_meta = tables.get(from_table)
        if not isinstance(table_meta, dict):
            continue

        fks = table_meta.get("foreign_keys")
        if not isinstance(fks, dict):
            fks = {}
            table_meta["foreign_keys"] = fks

        # Mevcut foreign_keys varsa ezmeyelim; top-level relationship sadece eksikse tamamlansın.
        fks.setdefault(from_col, f"{to_table}.{to_col}")


class MetadataService:
    def __init__(self, json_path: Path | None = None) -> None:
        self._path = json_path or _default_metadata_path()
        self._data: dict[str, Any] | None = None
        self._alias_to_tables: dict[str, list[str]] = {}

    def _load(self) -> dict[str, Any]:
        if self._data is not None:
            return self._data

        if not self._path.exists():
            raise FileNotFoundError(
                "Metadata dosyası yok. ai/metadata/schema_metadata.json (Kişi 1) veya "
                "ai/schema_metadata_gecici.json (geçici test) gerekli."
            )

        raw = json.loads(self._path.read_text(encoding="utf-8"))

        tables = _normalize_tables(raw.get("tables"))
        if not tables:
            raise ValueError("schema_metadata.json içinde geçerli 'tables' objesi yok.")

        _apply_relationships_to_tables(tables, raw.get("relationships"))
        raw["tables"] = tables

        self._data = raw
        self._rebuild_alias_index()
        return self._data

    def _rebuild_alias_index(self) -> None:
        self._alias_to_tables = {}
        data = self._data or {}
        tables = data.get("tables", {})

        for table_name in tables:
            t = tables.get(table_name) or {}
            aliases = t.get("aliases") or []
            if isinstance(aliases, str):
                aliases = [aliases]

            for a in aliases:
                key = _normalize_alias(str(a))
                if not key:
                    continue
                self._alias_to_tables.setdefault(key, []).append(table_name)

    def reload(self) -> None:
        self._data = None
        self._alias_to_tables = {}
        self._load()

    def tables(self) -> dict[str, Any]:
        """Ham 'tables' sözlüğü (tablo adı -> normalize metadata)."""
        self._load()
        t = self._data.get("tables", {})
        return t if isinstance(t, dict) else {}

    def list_tables(self) -> list[str]:
        return sorted(self.tables().keys())

    def get_table(self, name: str) -> dict[str, Any] | None:
        key = _normalize_table_name(name)
        t = self.tables().get(key)
        if t is None:
            return None
        return t if isinstance(t, dict) else None

    def find_table_by_alias(self, term: str) -> str | None:
        """Tek tablo adı döner; aynı alias birden fazla tabloda varsa deterministik ilk eşleşme."""
        self._load()
        key = _normalize_alias(term)
        if not key:
            return None

        if key in self._alias_to_tables:
            return sorted(self._alias_to_tables[key])[0]

        for alias, tables in sorted(self._alias_to_tables.items(), key=lambda x: -len(x[0])):
            if key in alias or alias in key:
                return sorted(tables)[0]

        return None

    def all_alias_index(self) -> dict[str, list[str]]:
        """Test / debug: normalize alias -> tablo adları."""
        self._load()
        return {k: list(v) for k, v in self._alias_to_tables.items()}