"""
Doğal dil sorusundan dar schema context üretir.
metadata_service; schema dosyası Kişi 1 (schema_metadata.json) veya geçici (schema_metadata_gecici.json).
"""

from __future__ import annotations

import re
from .metadata_service import MetadataService


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _tokenize(text: str) -> set[str]:
    text = (text or "").lower()
    parts = re.split(r"[^\w]+", text, flags=re.UNICODE)
    return {p for p in parts if len(p) >= 2}


def _has_any_phrase(question_text: str, phrases: tuple[str, ...]) -> bool:
    return any(p in question_text for p in phrases)


def _detect_intents(question: str, tokens: set[str]) -> set[str]:
    q = _normalize_text(question)
    intents: set[str] = set()

    sales_phrases = (
        "en çok satan",
        "top selling",
        "best selling",
        "satış",
        "satis",
        "ciro",
        "revenue",
        "gelir",
    )
    if _has_any_phrase(q, sales_phrases) or {"satış", "satis", "satan", "ciro", "revenue", "gelir"} & tokens:
        intents.add("sales")

    if _has_any_phrase(q, ("ürün", "urun", "product", "mal")) or {"ürün", "urun", "product", "mal"} & tokens:
        intents.add("product")

    if _has_any_phrase(q, ("kategori", "category")) or {"kategori", "category"} & tokens:
        intents.add("category")

    if _has_any_phrase(q, ("müşteri", "musteri", "customer", "client", "firma")) or {
        "müşteri", "musteri", "customer", "client", "firma"
    } & tokens:
        intents.add("customer")

    if _has_any_phrase(q, ("çalışan", "calisan", "personel", "employee")) or {
        "çalışan", "calisan", "personel", "employee"
    } & tokens:
        intents.add("employee")

    if _has_any_phrase(q, ("sipariş", "siparis", "order", "işlem", "islem")) or {
        "sipariş", "siparis", "order", "işlem", "islem"
    } & tokens:
        intents.add("order")

    if _has_any_phrase(q, ("sayısı", "sayisi", "count", "toplam", "adet", "bazında", "bazinda")) or {
        "sayısı", "sayisi", "count", "toplam", "adet", "bazında", "bazinda"
    } & tokens:
        intents.add("aggregate")

    if _has_any_phrase(q, ("en çok", "en cok", "top", "highest", "largest")):
        intents.add("ranking")

    if "sipariş veren" in q or "siparis veren" in q:
        intents.add("customer")
        intents.add("order")

    return intents


def _priority_boost(meta: dict) -> float:
    priority = str(meta.get("priority") or "").strip().lower()
    if priority == "critical":
        return 1.5
    if priority == "high":
        return 0.75
    if priority == "medium":
        return 0.25
    return 0.0


def _score_table(table_name: str, meta: dict, tokens: set[str], question_text: str) -> float:
    score = 0.0

    desc = (meta.get("description") or "").lower()
    aliases = meta.get("aliases") or []
    if isinstance(aliases, str):
        aliases = [aliases]

    for a in aliases:
        al = str(a).strip().lower()
        if not al:
            continue

        # tam alias cümle içinde
        if al in question_text:
            score += 4.0
        else:
            atoks = _tokenize(al)
            inter = atoks & tokens
            score += 2.0 * len(inter)

    desc_tokens = _tokenize(desc)
    score += 0.5 * len(desc_tokens & tokens)

    cols = meta.get("columns") or {}
    if isinstance(cols, dict):
        for cname, cdesc in cols.items():
            cn = str(cname).lower()
            if cn in tokens:
                score += 1.0
            score += 0.25 * len(_tokenize(str(cdesc)) & tokens)

    table_phrase = table_name.lower().replace("_", " ")
    if table_phrase in question_text:
        score += 3.0

    table_tokens = _tokenize(table_phrase)
    score += 1.5 * len(table_tokens & tokens)

    return score


def _intent_table_boost(table_name: str, intents: set[str]) -> float:
    name = table_name.lower()
    boost = 0.0

    if "sales" in intents:
        if name == "order_details":
            boost += 6.0
        elif name == "orders":
            boost += 3.5

        if "product" in intents and name == "products":
            boost += 4.0
        if "customer" in intents and name == "customers":
            boost += 4.0
        if "employee" in intents and name == "employees":
            boost += 4.0
        if "category" in intents and name == "categories":
            boost += 2.0

    if "product" in intents:
        if name == "products":
            boost += 4.0
        if "sales" in intents and name == "order_details":
            boost += 2.5

    if "category" in intents:
        if name == "categories":
            boost += 4.0
        if name == "products":
            boost += 2.5

    if "customer" in intents:
        if name == "customers":
            boost += 4.0
        if name == "orders":
            boost += 2.5

    if "employee" in intents:
        if name == "employees":
            boost += 4.0
        if name == "orders":
            boost += 2.5

    if "order" in intents:
        if name == "orders":
            boost += 4.0
        if name == "order_details":
            boost += 1.5

    if "ranking" in intents and name == "order_details":
        boost += 0.5

    return boost


def _expand_selection(
    picked: list[str],
    score_by_table: dict[str, float],
    intents: set[str],
    available_tables: set[str],
    max_tables: int,
) -> list[str]:
    extras: list[str] = []

    def add_if_needed(table_name: str) -> None:
        if table_name in available_tables and table_name not in picked and table_name not in extras:
            extras.append(table_name)

    if "sales" in intents:
        if "products" in picked:
            add_if_needed("order_details")
            add_if_needed("orders")
        if "customers" in picked or "employees" in picked:
            add_if_needed("orders")
        if "orders" in picked:
            add_if_needed("order_details")
        if "categories" in picked:
            add_if_needed("products")

    if "category" in intents:
        add_if_needed("products")

    if "customer" in intents and ("order" in intents or "sales" in intents):
        add_if_needed("orders")

    if "employee" in intents and ("order" in intents or "sales" in intents):
        add_if_needed("orders")

    combined: list[str] = []
    for name in picked + extras:
        if name not in combined:
            combined.append(name)

    if len(combined) <= max_tables:
        return combined

    mandatory = set(extras)
    ranked = sorted(
        combined,
        key=lambda name: (
            1 if name in mandatory else 0,
            score_by_table.get(name, 0.0),
            -combined.index(name),
        ),
        reverse=True,
    )
    keep = set(ranked[:max_tables])

    return [name for name in combined if name in keep]


def _join_hints(selected: list[str], service: MetadataService) -> list[str]:
    hints: list[str] = []
    sel_set = {s.lower() for s in selected}
    seen: set[tuple[str, str]] = set()

    for t in selected:
        meta = service.get_table(t) or {}
        fks = meta.get("foreign_keys") or {}
        if not isinstance(fks, dict):
            continue

        for col, ref in fks.items():
            ref_s = str(ref)
            if "." in ref_s:
                rt, rcol = ref_s.split(".", 1)
            else:
                rt, rcol = ref_s, "?"

            rt_l = rt.strip().lower()
            if rt_l not in sel_set:
                continue

            pair = tuple(sorted((t.lower(), rt_l)))
            if pair in seen:
                continue

            seen.add(pair)
            hints.append(f"{t}.{col} -> {rt}.{rcol.strip()}")

    return hints


def build_context(
    question: str,
    service: MetadataService | None = None,
    max_tables: int = 4,
    min_tables: int = 1,
) -> str:
    """
    Soruya göre en ilgili tabloları seçer (varsayılan en fazla 4),
    FK tabanlı join ipucu ve kısa context metni üretir.
    """
    svc = service or MetadataService()
    question_text = _normalize_text(question)
    tokens = _tokenize(question)
    intents = _detect_intents(question, tokens)

    tables_raw = svc.tables()
    scored: list[tuple[float, str]] = []
    score_by_table: dict[str, float] = {}

    for name, meta in tables_raw.items():
        if not isinstance(meta, dict):
            continue

        sc = _score_table(name, meta, tokens, question_text)
        sc += _priority_boost(meta)
        sc += _intent_table_boost(name, intents)

        score_by_table[name] = sc
        scored.append((sc, name))

    scored.sort(key=lambda x: (-x[0], x[1]))

    picked: list[str] = []
    for sc, name in scored:
        if sc <= 0:
            break
        picked.append(name)
        if len(picked) >= max_tables:
            break

    if len(picked) < min_tables and scored:
        # zayıf eşleşme: en yüksek skorlu tabloları yine de doldur
        for sc, name in scored:
            if name not in picked:
                picked.append(name)
            if len(picked) >= min_tables:
                break

    if not picked:
        return ""

    picked = _expand_selection(
        picked=picked,
        score_by_table=score_by_table,
        intents=intents,
        available_tables=set(tables_raw.keys()),
        max_tables=max_tables,
    )

    lines: list[str] = ["[Seçilen tablolar]"]
    for t in picked:
        m = svc.get_table(t) or {}
        desc = (m.get("description") or "").strip()
        if desc:
            lines.append(f"- {t}: {desc}")
        else:
            lines.append(f"- {t}")

        cols = m.get("columns") or {}
        if isinstance(cols, dict) and cols:
            brief = ", ".join(f"{k}" for k in list(cols.keys())[:12])
            if len(cols) > 12:
                brief += ", …"
            lines.append(f"  Kolonlar: {brief}")

    jh = _join_hints(picked, svc)
    if jh:
        lines.append("[Join ipuçları]")
        lines.extend(f"- {h}" for h in jh)

    return "\n".join(lines)