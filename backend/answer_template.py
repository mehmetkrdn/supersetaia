from app.security.user_context import UserContext


_ROLE_LABELS_TR = {
    "admin": "Admin",
    "manager": "Yönetici",
    "team_leader": "Takım Lideri",
    "employee": "Çalışan",
    "customer": "Müşteri",
    "hr": "İK",
    "guest": "Misafir",
}


def _role_labels_tr(role_codes: list[str]) -> list[str]:
    labels = []
    for code in role_codes or []:
        labels.append(_ROLE_LABELS_TR.get(code, code))
    return labels


def _primary_role_label(role_codes: list[str]) -> str:
    labels = _role_labels_tr(role_codes)
    if labels:
        return labels[0]
    return "Misafir"


def build_assistant_reply(
    user: UserContext,
    question: str,
    columns: list[str],
    row_count: int,
    truncated: bool,
    ui_locale: str = "tr",
) -> tuple[str, list[str]]:
    """
    Sadece gerçekten dönen sonuç kümesine dayanan, şablon tabanlı kısa asistan metni.
    Harici veri veya tahmin eklemez.
    """
    locale = (ui_locale or "tr").lower().split("-")[0]
    if locale not in {"tr", "en", "fr", "ar"}:
        locale = "tr"

    q = (question or "").strip()
    role_tr = _primary_role_label(user.role_codes)

    cols = [c for c in (columns or []) if c is not None]
    col_preview = ", ".join(str(c) for c in cols[:8])
    if len(cols) > 8:
        col_preview = f"{col_preview}, …"

    text = {
        "tr": {
            "role": "Rolünüz",
            "summary_scope": "Özet, yalnızca bu rol kapsamında size sunulan sonuç satırlarına göredir.",
            "ran": "Sorgu çalıştırıldı; {n} satır listelendi.",
            "cols": "Dönen kolonlar: {cols}.",
            "no_cols": "Tablo yapısı: sonuç kolonu yok (boş sonuç).",
            "trunc": "Sonuçlar uygulama limiti nedeniyle kısaltılmış olabilir; tam liste için limiti artırın veya 'Tümü' seçin.",
            "no_rows": "Sorunuz ({q}) için sorgu güvenli biçimde çalıştırıldı; filtre ve yetkilerinize uyan kayıt bulunamadı. Sol panelden görünüm türünü seçseniz de gösterilecek satır yok.",
            "rows": "Sorunuz doğrultusunda bir SELECT sorgusu üretilip veritabanında çalıştırıldı. {n} satırlık sonuç, rolünüzün ({role}) izin verdiği ölçüde size sunuldu. Grafik veya tablo olarak görmek için sol panelden istediğiniz görselleştirme türüne tıklayabilirsiniz.",
        },
        "en": {
            "role": "Your role",
            "summary_scope": "This summary is based only on the rows returned for your role.",
            "ran": "Query executed; {n} rows listed.",
            "cols": "Returned columns: {cols}.",
            "no_cols": "Table shape: no result columns (empty result).",
            "trunc": "Results may be truncated by the app limit; increase the limit or choose 'All' for the full list.",
            "no_rows": "Your question ({q}) was executed safely, but no records matched your filters/permissions. Even if you switch views, there are no rows to display.",
            "rows": "A SELECT query was generated and executed. {n} rows were returned within your role ({role}) permissions. Choose a visualization type on the left to view as a chart or table.",
        },
        "fr": {
            "role": "Votre rôle",
            "summary_scope": "Ce résumé est basé uniquement sur les lignes renvoyées pour votre rôle.",
            "ran": "Requête exécutée ; {n} lignes affichées.",
            "cols": "Colonnes renvoyées : {cols}.",
            "no_cols": "Structure : aucune colonne de résultat (résultat vide).",
            "trunc": "Les résultats peuvent être tronqués par la limite ; augmentez la limite ou choisissez « Tous ».",
            "no_rows": "Votre question ({q}) a été exécutée en toute sécurité, mais aucun enregistrement ne correspond à vos filtres/autorisations. Même en changeant de vue, il n'y a aucune ligne à afficher.",
            "rows": "Une requête SELECT a été générée et exécutée. {n} lignes ont été renvoyées selon les autorisations de votre rôle ({role}). Choisissez un type de visualisation à gauche.",
        },
        "ar": {
            "role": "دورك",
            "summary_scope": "هذا الملخص يعتمد فقط على الصفوف المعروضة ضمن صلاحيات دورك.",
            "ran": "تم تنفيذ الاستعلام؛ تم عرض {n} صفوف.",
            "cols": "الأعمدة المُعادة: {cols}.",
            "no_cols": "بنية الجدول: لا توجد أعمدة نتيجة (نتيجة فارغة).",
            "trunc": "قد تكون النتائج مقتطعة بسبب حد التطبيق؛ زد الحد أو اختر «الكل» لعرض القائمة كاملة.",
            "no_rows": "تم تنفيذ سؤالك ({q}) بأمان، لكن لم يتم العثور على سجلات مطابقة للفلاتر/الصلاحيات. حتى مع تغيير العرض لا توجد صفوف لعرضها.",
            "rows": "تم إنشاء استعلام SELECT وتنفيذه. تم إرجاع {n} صفوف ضمن صلاحيات دورك ({role}). اختر نوع العرض من اليسار لعرضها كجدول أو رسم.",
        },
    }[locale]

    bullets: list[str] = [
        f"{text['role']}: {role_tr}. {text['summary_scope']}",
        text["ran"].format(n=row_count),
    ]

    if cols:
        bullets.append(text["cols"].format(cols=col_preview))
    else:
        bullets.append(text["no_cols"])

    if truncated:
        bullets.append(text["trunc"])

    if row_count == 0:
        qq = q[:200] + ("…" if len(q) > 200 else "")
        body = text["no_rows"].format(q=qq)
        return body, bullets

    body = text["rows"].format(n=row_count, role=role_tr)
    return body, bullets