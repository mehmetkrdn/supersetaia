# table_guides.md

## Amaç

Bu belge, Northwind tabanlı analitik sisteminde kullanılan tüm temel analitik tabloları açıklar.

Her tablo tanımı şunları içerir:
- iş anlamı (business meaning)
- teknik rol
- temel sütunlar (key columns)
- birleştirme (join) davranışı
- takma ad (alias) kuralları
- doğal dil eşlemeleri (takma ad / eşanlamlı katmanı)

Bu dosya şunlar için kullanılır:
- tablo seçimine rehberlik etmek
- halüsinasyonu önlemek
- NL (Doğal Dil) → SQL doğruluğunu artırmak
- kullanıcı sorgularının anlamsal olarak anlaşılmasını desteklemek

---

# 1. categories

## İş Anlamı
Ürün kategorilerini temsil eder (örn. İçecekler, Deniz Ürünleri).

## Teknik Rol
Ürünleri gruplandırmak için boyut (dimension) tablosu.

## Birincil Anahtar
- category_id

## Önemli Sütunlar
- category_name → kategori etiketi
- description → kategori açıklaması

## Yaygın Kullanım Senaryoları
- kategori bazlı satışlar
- ürünleri gruplandırma
- kategori karşılaştırmaları

## Birleştirmeler (Joins)
- products.category_id → categories.category_id

## Takma Ad (Alias)
- cat (tercih edilen)
- c (kabul edilebilir)

## Doğal Dil Takma Adları
- kategori
- ürün kategorisi
- product category
- category
- ürün grubu

---

# 2. products

## İş Anlamı
Satılan bireysel ürünleri temsil eder.

## Teknik Rol
Ürün düzeyinde analiz için merkezi boyut (dimension) tablosu.

## Birincil Anahtar
- product_id

## Önemli Sütunlar
- product_name
- category_id
- supplier_id
- unit_price
- units_in_stock
- units_on_order
- discontinued

## Genişletilmiş Kapsam Sütunları (özel)
- company_id

## Yaygın Kullanım Senaryoları
- ürün satış analizi
- stok takibi
- kategori/ürün kırılımı

## Birleştirmeler (Joins)
- products.category_id → categories.category_id
- products.product_id → order_details.product_id
- products.supplier_id → suppliers.supplier_id

## Takma Ad (Alias)
- p (tercih edilen)

## Doğal Dil Takma Adları
- ürün
- ürünler
- product
- item
- mal

---

# 3. customers

## İş Anlamı
Sipariş veren müşterileri temsil eder.

## Teknik Rol
Müşteri boyut tablosu.

## Birincil Anahtar
- customer_id

## Önemli Sütunlar
- company_name
- contact_name
- city
- country

## Genişletilmiş Kapsam Sütunları (özel)
- company_id
- region_id

## Yaygın Kullanım Senaryoları
- müşteri satış analizi
- coğrafi dağılım
- müşteri sıralaması

## Birleştirmeler (Joins)
- customers.customer_id → orders.customer_id

## Takma Ad (Alias)
- c (tercih edilen)
- cust (alternatif)

## Doğal Dil Takma Adları
- müşteri
- firma
- alıcı
- customer
- client

---

# 4. employees

## İş Anlamı
Siparişleri işleyen çalışanları temsil eder.

## Teknik Rol
Satış performansı ve hiyerarşi için boyut tablosu.

## Birincil Anahtar
- employee_id

## Önemli Sütunlar
- first_name
- last_name
- title
- reports_to

## Genişletilmiş Kapsam Sütunları (özel)
- company_id
- branch_id
- department_id
- team_id

## Yaygın Kullanım Senaryoları
- çalışan performansı
- çalışan bazında satışlar
- organizasyonel hiyerarşi

## Birleştirmeler (Joins)
- employees.employee_id → orders.employee_id
- employees.reports_to → employees.employee_id (kendi kendine birleştirme / self join)

## Takma Ad (Alias)
- e (tercih edilen)

## Doğal Dil Takma Adları
- çalışan
- personel
- satış temsilcisi
- employee
- staff

---

# 5. orders

## İş Anlamı
Müşteri siparişlerini (işlemlerini) temsil eder.

## Teknik Rol
Temel fact (olay/gerçeklik) tablosu (başlık düzeyi).

## Birincil Anahtar
- order_id

## Önemli Sütunlar
- customer_id
- employee_id
- order_date
- required_date
- shipped_date
- ship_via
- freight

## Genişletilmiş Kapsam Sütunları (özel)
- company_id
- branch_id
- department_id

## Yaygın Kullanım Senaryoları
- sipariş analizi
- tarih bazlı analiz
- müşteri davranışı
- sevkiyat takibi

## Birleştirmeler (Joins)
- orders.order_id → order_details.order_id
- orders.customer_id → customers.customer_id
- orders.employee_id → employees.employee_id
- orders.ship_via → shippers.shipper_id

## Takma Ad (Alias)
- o (tercih edilen)

## Doğal Dil Takma Adları
- sipariş
- satış
- işlem
- order
- satış kaydı

---

# 6. order_details

## İş Anlamı
Her siparişin içindeki kalemleri (satırları) temsil eder.

## Teknik Rol
Fact tablosu (satır düzeyi, gelir hesaplaması).

## Birincil Anahtar
- (order_id, product_id)

## Önemli Sütunlar
- unit_price
- quantity
- discount

## Yaygın Kullanım Senaryoları
- gelir hesaplaması
- ürün satışları
- miktar analizi

## Birleştirmeler (Joins)
- order_details.order_id → orders.order_id
- order_details.product_id → products.product_id

## Takma Ad (Alias)
- od (tercih edilen)

## Doğal Dil Takma Adları
- sipariş detayı
- satış detayı
- order detail
- line item

---

# 7. suppliers

## İş Anlamı
Ürün tedarikçilerini temsil eder.

## Teknik Rol
Tedarikçi boyutu.

## Birincil Anahtar
- supplier_id

## Önemli Sütunlar
- company_name
- country

## Genişletilmiş Kapsam Sütunları (özel)
- company_id

## Yaygın Kullanım Senaryoları
- tedarikçi analizi
- ürün tedariği

## Birleştirmeler (Joins)
- suppliers.supplier_id → products.supplier_id

## Takma Ad (Alias)
- s (tercih edilen)

## Doğal Dil Takma Adları
- tedarikçi
- supplier
- üretici firma

---

# 8. shippers

## İş Anlamı
Nakliye (kargo) şirketlerini temsil eder.

## Teknik Rol
Nakliye boyutu.

## Birincil Anahtar
- shipper_id

## Önemli Sütunlar
- company_name

## Yaygın Kullanım Senaryoları
- nakliye analizi
- teslimat takibi

## Birleştirmeler (Joins)
- shippers.shipper_id → orders.ship_via

## Takma Ad (Alias)
- sh (tercih edilen)

## Doğal Dil Takma Adları
- kargo
- taşıyıcı
- nakliyeci
- shipper

---

# 9. geography (ileri düzey)

## Tablolar
- region
- territories
- employee_territories

## İş Anlamı
Çalışanların ve satışların coğrafi gruplamasını temsil eder.

## Kullanım
- gelişmiş bölgesel analiz
- bölge (territory) bazlı raporlama

## Not
Sadece açıkça gerektiğinde kullanın.

---

# 10. Veritabanları Arası Kapsam Eşlemesi (Mantıksal)

Bu eşlemeler varsayılan olarak fiziksel join'ler DEĞİLDİR.

Şunlar arasındaki mantıksal ilişkileri temsil ederler:
- northwind (analitik)
- ai_security (yetkilendirme & kapsam)

## Mantıksal Eşleme Örnekleri

- orders.company_id → companies.id
- orders.branch_id → branches.id
- orders.department_id → departments.id

- employees.company_id → companies.id
- employees.branch_id → branches.id
- employees.department_id → departments.id
- employees.team_id → teams.id

- customers.company_id → companies.id
- customers.region_id → regions.id

- products.company_id → companies.id

## Önemli Kural

Bu eşlemeler:
- meta verileri anlamak için kullanılır
- SQL üretiminde otomatik olarak UYGULANMAZ
- sadece sistem açıkça veritabanları arası join'ler gerektiriyorsa kullanılmalıdır

---

# 11. Tablo Seçim Stratejisi

Bir sorguyu yanıtlarken:

### Satış soruları
→ orders + order_details (zorunlu)

### Ürün soruları
→ products (+ categories isteğe bağlı)

### Müşteri soruları
→ customers (+ orders isteğe bağlı)

### Çalışan soruları
→ employees (+ orders + order_details)

### Nakliye soruları
→ shippers + orders

### Tedarikçi soruları
→ suppliers + products

---

# 12. Anti-Kalıplar (Kesinlikle Kaçının)

Şunları YAPMAYIN:
- satış analitiği için order_details'ı orders olmadan kullanmak
- gereksiz tabloları birleştirmek (join)
- sahte ilişkiler yaratmak
- ilgili olmayan boyutları karıştırmak
- join'lerde birincil anahtarları görmezden gelmek
- eksik yabancı anahtarları (foreign keys) tahmin etmek

---

# 13. Tasarım Felsefesi

- Her zaman minimal ama doğru join'leri tercih edin
- Her zaman iş anlamını koruyun
- Her zaman gerçek şema ilişkilerine saygı duyun
- Her zaman kullanıcı niyetini → doğru tablo setine eşleyin