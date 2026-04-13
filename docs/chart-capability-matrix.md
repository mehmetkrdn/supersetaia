# Chart Capability Matrix (Manuel Yaklaşım)

Bu doküman, hedeflediğimiz chart setini teknik uygulanabilirlik, veri gereksinimi ve faz planı açısından özetler.

## 1) Hedef Chart Listesi

- Table
- Pivot Table
- Progress
- Funnel
- Detail
- Map
- Bar
- Line
- Pie
- Number (KPI)
- Row
- Area
- Combo
- Trend
- Gauge
- Scatter
- Waterfall
- Box Plot
- Sankey

---

## 2) Chart Gereksinim Matrisi

| Chart | Minimum veri gereksinimi | Zorluk | Not |
|---|---|---|---|
| Table | herhangi bir kolon/satır | Kolay | Mevcut |
| Bar | 1 kategori (text/date) + 1 numeric | Kolay | Mevcut |
| Line | 1 zaman/kategori + 1 numeric | Kolay | Mevcut |
| Pie | 1 kategori + 1 numeric | Kolay | Kısa sürede eklenir |
| Number (KPI) | tek numeric değer | Kolay | Mevcut |
| Area | 1 zaman/kategori + 1 numeric | Kolay-Orta | Line altyapısından türetilir |
| Scatter | 2 numeric (+ opsiyonel label) | Orta | Nokta yoğunluğu önemli |
| Combo | 1 kategori + 2+ numeric (line+bar) | Orta | Ortak eksen ihtiyacı |
| Trend | tarih + metric + opsiyonel önceki dönem | Orta | Delta/percent hesap gerekir |
| Funnel | aşama adı + değer | Orta | Custom transform gerekebilir |
| Waterfall | adım + artış/azalış değerleri | Orta-Zor | Hesaplama katmanı şart |
| Box Plot | her kategori için dağılım (çoklu numeric) | Zor | Kuartil hesapları gerekir |
| Gauge | tek metric + hedef/aralık | Orta | KPI türevi, threshold gerekir |
| Sankey | source, target, value | Zor | Graph veri modeli gerekir |
| Pivot Table | row dims + col dims + aggregate | Zor | Pivot engine gerekir |
| Map | geo key (ülke/şehir/lat-lon) + metric | Zor | Coğrafi eşleme gerekir |
| Progress | target/current veya yüzde | Orta | KPI + threshold |
| Detail | satır bazlı detay kartları | Orta | Drill-down kurgusu |
| Row | yatay bar/row list görünümü | Kolay-Orta | Table/Bar varyantı |

---

## 3) Önerilen Faz Planı

## Faz A (Hızlı değer, düşük risk)
- Table, Bar, Line, Pie, Number(KPI), Area, Scatter
- Hedef: Sol panelde temel chartların aktif ve stabil çalışması

## Faz B (Orta seviye analitik)
- Combo, Trend, Funnel, Progress, Row, Detail
- Hedef: İş kullanıcılarının en sık kullandığı ara analiz tipleri

## Faz C (İleri seviye)
- Waterfall, Box Plot, Gauge, Sankey, Pivot Table, Map
- Hedef: Gelişmiş analitik ve yönetim raporlama ihtiyaçları

---

## 4) Teknik Tercih Önerisi

- Uzun vadede chart seti geniş olacağı için tek motor yaklaşımı önerilir.
- Bu hedef listesi için `ECharts` ekosistemi daha kapsayıcıdır.
- Recharts mevcut tiplerde kalabilir, ancak Faz B-C için ek kütüphane maliyeti büyür.

---

## 5) Uygulama Notu (Karar Kriteri)

Bir chart'ın aktif olması için:
- veri gereksinimi karşılanmalı,
- dönüşüm (aggregation/reshape) yapılabilmeli,
- hata durumunda kullanıcıya “neden uygun değil” mesajı gösterilmeli.

Bu kurallar sayesinde sol panelde tüm chartlar görünür kalır; uygun olanlar çalışır, uygun olmayanlar anlaşılır geri bildirim verir.

