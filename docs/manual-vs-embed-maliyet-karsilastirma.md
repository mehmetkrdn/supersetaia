# Manuel vs Embed — Kısa Karar Notu

## Karar
- **Ana ürün için manuel chart geliştirme** seçildi.
- **Neden:** Chat + RBAC + görselleştirme tek akışta daha kontrollü, daha özelleştirilebilir ve uzun vadede daha sürdürülebilir.

## Hızlı Karşılaştırma

| Başlık | Manuel | Embed (Superset/Metabase) |
|---|---|---|
| İlk geliştirme hızı | Orta | Hızlı |
| UI/UX kontrolü | Çok yüksek | Sınırlı |
| RBAC/chat entegrasyonu | Doğal | Daha karmaşık |
| Performans (ilk yük) | Genelde daha hafif | Genelde daha ağır |
| Uzun vadeli bağımlılık | Düşük | Daha yüksek |

## Maliyet Özeti
- **Kısa vade (MVP):** Embed daha ucuz/hızlı olabilir.
- **Orta-uzun vade:** Manuel yaklaşımın toplam sahip olma maliyeti genelde daha dengeli olur (özellikle ürünleşmede).

## Ne zaman Embed düşünülür?
- Çok kısa sürede çok sayıda dashboard çıkarılması gerekiyorsa.
- Self-service BI ayrı bir hedefse.

## Final Not
Bu projede ana deneyim manuel tutulacak; gerekirse ileride “Advanced Analytics” için hibrit model (ayrı BI ekranı) değerlendirilecek.

