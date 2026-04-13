# Superset dashboard'ları

Bu klasör, Northwind veritabanı için oluşturulan Superset dashboard'larının JSON export'larını içerir. Aynı ortamı kuran arkadaşlar bu dosyaları import ederek aynı dashboard'lara ulaşabilir.

## Export edilen dashboard'lar

- **Satış Özet** – Sipariş sayısı (aylık), toplam sipariş, kategoriye göre satış
- **Kategori performansı** – Kategoriye göre satış (tablo + pie)
- **Ürün performansı** – En çok satan ürünler
- **Müşteri analizi** – En çok alışveriş yapan müşteriler
- **Sipariş özeti** – Nakliyeciye göre sipariş, sipariş durumu (Gönderildi/Beklemede)
- **Çalışan satışları** – Çalışan bazında satış

## Arkadaşlarım nasıl kullanır?

### 1. Northwind + Superset ortamını çalıştır

- **Northwind (Postgres + pgAdmin):** Proje kökünde `docker compose up -d`
- **Superset:** [Superset Apache Kurulum.txt](../Superset%20Apache%20Kurulum.txt) içindeki adımlara göre Superset’i ayağa kaldır ve Northwind veritabanı bağlantısını ekle (host: `host.docker.internal`, port: `55432`, database: `northwind`, user/pass: `postgres`).

### 2. Dashboard'ları import et

1. Superset’e giriş yap (örn. http://localhost:8088), admin / admin.
2. Üst menüden **Settings** (dişli) → **Import dashboards** (veya **Dashboard** → **Import**).
3. Bu klasördeki `.json` dosyalarını tek tek seçip import et.
4. Import sonrası **Dashboards** menüsünden dashboard’ları görebilirsin.

Not: Import öncesi Northwind veritabanı bağlantısının Superset’te tanımlı olması gerekir (Connect database → PostgreSQL, host: `host.docker.internal`, port: 55432, database: northwind, user: postgres, password: postgres).

## Dashboard'ları nasıl export ederim? (Güncelleme yapanlar için)

1. Superset’te ilgili dashboard’u aç.
2. Sağ üstte **⋮** (üç nokta) menüsüne tıkla.
3. **Export** → **Export dashboard** (veya **Download as JSON**) seç; dosyayı indir.
4. İndirilen JSON dosyasını bu klasöre koy (anlamlı bir isimle, örn. `satis-ozet.json`).
5. Değişiklikleri repo’ya commit + push et.
