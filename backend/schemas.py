from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Kullanıcının doğal dilde sorduğu soru")

    user_id: int = Field(..., description="Kullanıcı ID")
    username: str | None = Field(default=None, description="Kullanıcı adı")
    active_company_id: int | None = Field(default=None, description="Aktif şirket ID")

    role_codes: list[str] = Field(default_factory=list, description="Kullanıcının rol kodları")
    permission_codes: list[str] = Field(default_factory=list, description="Opsiyonel, backend tarafından yeniden yüklenecek")

    company_ids: list[int] = Field(default_factory=list)
    country_ids: list[int] = Field(default_factory=list)
    region_ids: list[int] = Field(default_factory=list)
    branch_ids: list[int] = Field(default_factory=list)
    department_ids: list[int] = Field(default_factory=list)
    team_ids: list[int] = Field(default_factory=list)
    customer_ids: list[int] = Field(default_factory=list)

    is_superadmin: bool = Field(default=False)

    limit: int | None = Field(
        default=None,
        ge=0,
        description="İstenen maksimum satır sayısı. 0 ise tüm sonuçlar getirilir."
    )


class AskResponse(BaseModel):
    sql: str = Field(..., description="AI tarafından üretilen veya güvenlik filtresi uygulanmış SQL sorgusu")
    columns: list[str] = Field(default_factory=list, description="Sonuç tablosunun kolon adları")
    rows: list[list] = Field(default_factory=list, description="Sonuç satırları")
    row_count: int = Field(default=0, ge=0, description="Frontend'e dönen satır sayısı")
    total_row_count: int | None = Field(default=None, ge=0, description="Toplam bulunan satır sayısı")
    truncated: bool = Field(default=False, description="Sonuçlar kısaltıldı mı?")
    error: str | None = Field(default=None, description="Hata mesajı varsa burada döner")
    answer_text: str = Field(
        default="",
        description="Sadece dönen sonuçlara dayanan şablon asistan özeti (chat paneli)",
    )
    answer_bullets: list[str] = Field(
        default_factory=list,
        description="Kısa madde madde özet (chat paneli)",
    )