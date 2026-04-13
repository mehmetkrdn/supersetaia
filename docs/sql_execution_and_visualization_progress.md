# Northwind Sorgu Asistanı — SQL Execution ve Görselleştirme Geliştirmeleri

Bu branch kapsamında, proje gerçek veritabanı sorgulama ve sonuç görselleştirme desteği olan çalışan bir PoC haline getirildi.

---

## Faz 1 — SQL’i gerçekten çalıştırmak

Bu fazda yapılanlar:

- backend’e PostgreSQL bağlantısı eklendi
- AI tarafından üretilen SQL’in Northwind veritabanında gerçekten çalıştırılması sağlandı
- yalnızca `SELECT` / `WITH` sorgularına izin veren validation katmanı eklendi
- yasak SQL ifadeleri engellendi
- query timeout desteği eklendi
- row limit desteği eklendi
- sorgu sonucu `columns`, `rows`, `row_count`, `truncated` alanları ile JSON olarak frontend’e döndürülür hale getirildi
- frontend tarafında sonuç tablosu oluşturuldu

Bu faz sonunda sistem:

- “soru sor → SQL üret → veriyi getir” seviyesine yükseldi

---

## Faz 2 — Görselleştirme

Bu fazda yapılanlar:

- sorgu sonucundaki kolon tipleri analiz edilmeye başlandı
- veri yapısına göre uygun görünüm seçenekleri çıkarıldı
- varsayılan görünüm otomatik seçilir hale getirildi
- aşağıdaki görünüm tipleri desteklendi:
  - Table
  - Bar
  - Line
  - KPI
- kullanıcıya görünüm değiştirme butonları eklendi
- `recharts` ile gerçek bar chart ve line chart render edildi
- tek sayısal sonuçlar için KPI görünümü eklendi
- grafik eksenleri, tooltip ve sayı formatları okunabilir hale getirildi

Varsayılan görünüm kuralları:

- tek sayısal değer → KPI
- text + numeric → Bar
- date + numeric → Line
- diğer durumlar → Table

---

## Limit desteği

Kullanıcı için satır limiti seçimi eklendi.

Desteklenen seçenekler:

- 10
- 25
- 50
- 100
- Tümü

Not:

- frontend tarafında `Tümü` seçildiğinde backend’e `limit = 0` gönderilir
- backend tarafında `limit = 0` değeri “tüm sonuçları getir” olarak yorumlanır

---

## Güncellenen / eklenen önemli dosyalar

### Backend
- `backend/main.py`
- `backend/db.py`
- `backend/schemas.py`
- `backend/requirements.txt`

### Frontend
- `frontend/src/App.jsx`
- `frontend/src/App.css`
- `frontend/src/utils/visualization.js`
- `frontend/package.json`

### Konfigürasyon
- `.env.example`

---

## Kullanılan ek bağımlılıklar

### Backend
- `psycopg[binary]`

### Frontend
- `recharts`

---

## Sistem şu an neleri destekliyor?

- doğal dilde soru alma
- SQL üretme
- SQL’i gerçek Northwind veritabanında çalıştırma
- sorgu sonucunu tablo olarak gösterme
- veri tipine göre uygun varsayılan görünüm seçme
- bar chart gösterme
- line chart gösterme
- KPI gösterme
- kullanıcıya görünüm seçme imkanı sunma
- limit seçme
- tüm sonuçları getirme

---

## Örnek kullanım

### Bar görünümü
Soru:
- “En çok satan 5 ürün hangileri?”

Beklenen:
- varsayılan görünüm: Bar

### Line görünümü
Soru:
- “Aylara göre toplam satışları getir”

Beklenen:
- varsayılan görünüm: Line

### KPI görünümü
Soru:
- “Toplam sipariş sayısı kaç?”

Beklenen:
- varsayılan görünüm: KPI

---

## Sonraki olası geliştirmeler

- SQL kopyalama butonu
- CSV export
- gerçek pagination
- rol / RBAC tarafı ile entegrasyon
- daha gelişmiş grafik seçenekleri