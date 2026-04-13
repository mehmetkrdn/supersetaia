# global_rules.md

## Amaç

Bu belge, Northwind analitik veritabanı ve AI Security meta veri veritabanı ile kullanılan NL2SQL katmanı için küresel oluşturma kurallarını tanımlar.

Model, analitik kullanım senaryoları için geçerli, çalıştırılabilir, PostgreSQL uyumlu SQL üretirken aşağıdaki sorumlulukların ayrılığına dikkat etmelidir:

- `northwind` → iş / analitik verileri
- `ai_security` → yetkilendirme, kapsam (scope), veri seti ve politika meta verileri

Hedef; güvenli, doğru, deterministik ve çalıştırılmaya hazır SQL çıktısı üretmektir.

---

## 1. Temel Çıktı Kuralları

### 1.1 İzin verilen sorgu türü
- Sadece `SELECT` ifadeleri üretin.
- Asla şunları üretmeyin:
  - `INSERT`
  - `UPDATE`
  - `DELETE`
  - `DROP`
  - `CREATE`
  - `ALTER`
  - `TRUNCATE`
  - `MERGE`
  - `CALL`
  - `EXEC`
  - `GRANT`
  - `REVOKE`

### 1.2 Çıktı formatı
- Çıktı **sadece SQL** içermelidir.
- Şunları eklemeyin:
  - açıklamalar
  - yorumlar
  - markdown biçimlendirmesi
  - başlıklar
  - kod blokları
  - sorgudan önce veya sonra notlar
- Sistem açıkça çoklu sorgu çalıştırmayı desteklemediği sürece, SQL tek bir tam sorgu olmalıdır.

### 1.3 SQL kalite standardı
Üretilen SQL şu şekilde olmalıdır:
- sözdizimsel olarak geçerli
- anlamsal olarak mantıklı
- doğrudan çalıştırılabilir
- eksiksiz
- parçalanmamış
- PostgreSQL uyumlu

Asla şunları çıktı olarak vermeyin:
- eksik SQL
- yer tutucu (placeholder) metin
- sözde SQL (pseudo-SQL)
- tahmin edilmiş sütun adları
- tahmin edilmiş tablo adları
- geçersiz takma adlar (aliases)

---

## 2. Veritabanı Bağlamı

### 2.1 Birincil analitik kaynağı
Birincil analitik kaynağı `northwind` veritabanıdır.

Temel analitik tablolar şunları içerir:
- `orders`
- `order_details`
- `products`
- `customers`
- `employees`
- `categories`
- `suppliers`
- `shippers`

### 2.2 Güvenlik ve meta veri kaynağı
`ai_security` veritabanı şunları depolar:
- kullanıcılar
- roller
- izinler
- kapsam tanımları
- veri seti kayıtları
- veri seti sütun meta verileri
- sütun güvenlik kuralları
- şirket / ülke / bölge / şube / departman / takım hiyerarşisi

### 2.3 Veritabanları arası prensip
Model şunları anlamalıdır:
- iş analitiği sorguları temel olarak `northwind` üzerinde üretilir
- yetkilendirme ve politika uygulaması `ai_security` üzerinden yönetilir
- iki veritabanı arasında mantıksal kapsam eşlemeleri bulunabilir
- bu mantıksal eşlemeler, yürütme katmanı tarafından açıkça yapılandırılmadığı sürece modelin serbestçe geçici (ad hoc) veritabanları arası birleştirmeler (joins) üretmesi gerektiği anlamına **gelmez**

---

## 3. Güvenlik Sınırı Kuralları

### 3.1 Yetkilendirme backend'e aittir
Yetkilendirme, backend / ara katman (middleware) tarafından uygulanır.

Bu nedenle model, kullanıcı bu boyutlardan birine karşılık gelen bir iş filtresini açıkça talep etmediği sürece, aşağıdaki gibi güvenlik filtreleri **uydurmamalı** veya dayatmamalıdır:

- `company_id = ...`
- `region_id = ...`
- `branch_id = ...`
- `department_id = ...`
- `team_id = ...`
- `customer_id = ...`

### 3.2 Politika mantığını taklit etmeyin
Model, sistem tarafından açıkça talimat verilmedikçe SQL'de RBAC, ABAC, satır düzeyi güvenlik veya sütun düzeyi güvenliği simüle etmemelidir.

Bunun anlamı:
- kullanıcı kapsamını tahmin etmeyin
- gizli yetkilendirme koşulları (predicates) eklemeyin
- mevcut kullanıcının şirketini, şubesini, bölgesini veya departmanını çıkarmaya çalışmayın
- kendi inisiyatifinizle sütunları gizlemeyin veya dönüştürmeyin

### 3.3 Açık iş filtrelerine izin verilir
Kullanıcı tarafından açıkça talep edildiğinde şunlara izin verilir:
- ülke filtreleri
- şehir filtreleri
- müşteri filtreleri
- çalışan filtreleri
- tarih filtreleri
- kategori filtreleri
- ürün filtreleri
- nakliyeci filtreleri
- tedarikçi filtreleri

Örnek:
- İzin verilen: `WHERE o.order_date >= DATE '1997-01-01'`
- İzin verilen: `WHERE c.country = 'Germany'`
- İzin verilmeyen: Kullanıcı açıkça şirket düzeyinde filtreleme talep etmedikçe `WHERE o.company_id = 4`

---

## 4. Sorgu Oluşturma Kuralları

### 4.1 İfade (Clause) sıralaması
Her zaman doğru SQL ifade sıralamasını koruyun:

sql
SELECT ...
FROM ...
JOIN ...
WHERE ...
GROUP BY ...
HAVING ...
ORDER BY ...
LIMIT ...


### 4.2 LIMIT kullanımı
 * LIMIT ifadesini sadece gerektiğinde kullanın.
 * Bir sorguda LIMIT ifadesini yalnızca bir kez kullanın.
 * Zaten bir LIMIT varsa, ikincisini eklemeyin.
### 4.3 ORDER BY kuralları
 * Eğer SELECT içinde bir toplama (aggregate) takma adı tanımlanmışsa, bu ORDER BY içinde kullanılabilir.
 * Eğer bir takma ad tanımlanmamışsa, gerçek bir sütun veya açık bir toplama ifadesi kullanın.
 * Açıkça SELECT ifadesinde oluşturulmadıkça asla aşağıdaki gibi hayali isimler kullanmayın:
   * sales
   * revenue
   * total
   * amount
### 4.4 Takma ad (Alias) disiplini
 * Açık ve geleneksel takma adlar kullanın.
 * Takma adları kısa ve okunabilir tutun.
Önerilen takma ad stili:
 * o → orders
 * od → order_details
 * p → products
 * c → customers
 * e → employees
 * cat → categories
 * s → suppliers
 * sh → shippers
Şunları yapmayın:
 * aynı takma adı birden fazla tablo için yeniden kullanmak
 * yanıltıcı takma adlar kullanmak
 * takma adlı ve takma adsız referansları tutarsız bir şekilde karıştırmak
## 5. Join (Birleştirme) Kuralları
### 5.1 Sadece anlamlı join'ler kullanın
Sadece şunlara katkıda bulunan tabloları birleştirin:
 * talep edilen boyutlar
 * talep edilen metrikler
 * talep edilen filtreler
 * gerekli arama (lookup) bilgileri
Şunlardan kaçının:
 * gereksiz join'ler
 * dekoratif join'ler
 * spekülatif join'ler
### 5.2 Satış analitiği kuralı
Satışla ilgili sorular için, order_details genellikle orders ile birleştirilmelidir.
Tercih edilen kalıp:
sql
FROM order_details od
JOIN orders o ON o.order_id = od.order_id


Nedeni:
 * orders tarih bağlamı sağlar
 * orders müşteri bağlamı sağlar
 * orders çalışan bağlamı sağlar
 * orders sevkiyat bağlamı sağlar
 * orders, çoğu analitik filtreleme için doğal bir çapadır
### 5.3 Boyut genişletme
Sadece gerektiğinde ek tabloları birleştirin:
 * ürün bağlamı → products
 * kategori bağlamı → categories
 * müşteri bağlamı → customers
 * çalışan bağlamı → employees
 * tedarikçi bağlamı → suppliers
 * nakliyeci bağlamı → shippers
## 6. Metrik Kuralları
### 6.1 Gelir / satış tutarı
Varsayılan satış tutarı formülü:
sql
SUM(od.quantity * od.unit_price * (1 - od.discount))


Yuvarlatılmış versiyon:
sql
ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2)


### 6.2 Miktar tabanlı metrikler
Birim tabanlı sorular için şunu tercih edin:
sql
SUM(od.quantity)


### 6.3 Sipariş sayısı
Sipariş sayısı soruları için şunu tercih edin:
sql
COUNT(DISTINCT o.order_id)


### 6.4 Ürün sayısı / müşteri sayısı
Tekilleştirme mantıksal olarak gerektiğinde COUNT(DISTINCT ...) kullanın.
## 7. Tarih İşleme Kuralları
### 7.1 Kurallı (Canonical) sipariş tarihi sütunları
Amaca göre doğru tarih sütununu kullanın:
 * orders.order_date → sipariş oluşturma / sipariş tarihi
 * orders.required_date → istenen teslimat tarihi
 * orders.shipped_date → sevk edilen / yerine getirilen tarih
### 7.2 Durum yorumlama
Eğer sevkiyat durumu gerekliyse:
 * beklemede / sevk edilmedi:
sql
o.shipped_date IS NULL


 * sevk edildi:
sql
o.shipped_date IS NOT NULL


### 7.3 Tarih filtreleme
PostgreSQL uyumlu sözdizimi ile açık tarih karşılaştırmaları kullanın.
Tercih edilen stil:
sql
o.order_date >= DATE '1997-01-01'


Deterministik SQL beklendiğinde belirsiz veya taşınabilir olmayan ifadelerden kaçının.
## 8. Gruplama ve Toplama Kuralları
### 8.1 GROUP BY doğruluğu
Toplama fonksiyonları kullanıldığında, seçilen ancak toplanmayan tüm sütunlar uygun şekilde gruplandırılmalıdır.
### 8.2 İlk-N (Top-N) soruları
Şu tarz sorular için:
 * en iyi 5 ürün
 * en yüksek gelirli kategoriler
 * en iyi müşteriler
 * en iyi çalışanlar
Şu kalıbı kullanın:
 1. metriği hesaplayın
 2. takma ad atayın
 3. takma ada göre azalan sıralayın
 4. tek bir LIMIT uygulayın
### 8.3 En düşük / en az soruları
“En az”, “en düşük”, “en alt” tarzı sorular için:
 * metriği hesaplayın
 * artan sıralayın
 * uygunsa LIMIT kullanın
## 9. Null ve Veri Kalitesi İşleme
### 9.1 Null farkındalığı
Aşağıdaki gibi null olabilen (nullable) alanlara dikkat edin:
 * shipped_date
 * customer_id
 * employee_id
 * supplier_id
 * category_id
 * adres ile ilgili alanlar
 * bölge ile ilgili alanlar
### 9.2 Hatalı matematikten kaçının
Gerektiğinde COALESCE(...) ile açık null işleme kullanın, ancak sadece doğruluğu önemli ölçüde artırıyorsa.
Her yere gereksiz yere COALESCE eklemeyin.
## 10. İsimlendirme ve Anlamsal Disiplin
### 10.1 Asla şema halüsinasyonu görmeyin
Şunları uydurmayın:
 * tablolar
 * sütunlar
 * ilişkiler
 * fiziksel şema olarak iş terimleri
### 10.2 Gerçek iş anlamına saygı duyun
Örnekler:
 * freight sevkiyat maliyetidir, gelir değildir
 * discount, kalem formülündeki bir indirim oranıdır
 * ship_via nakliyeci bağlantısını ifade eder
 * reports_to çalışan hiyerarşisidir
### 10.3 Emin olmadığınızda tutucu olun
Eğer kullanıcı talebi güvenilir bir şekilde eşlenemiyorsa, bilinen şemaya dayalı en yakın geçerli yorumu tercih edin.
Desteklenmeyen şema öğeleri uydurmayın.
## 11. Veritabanları Arası Modelleme Kuralları
### 11.1 Mantıksal eşleme farkındalığı
Bazı Northwind tabloları şu tarz mantıksal kapsam sütunları içerebilir:
 * company_id
 * region_id
 * branch_id
 * department_id
 * team_id
Bunlar ai_security içinde yönetilen varlıklara karşılık gelebilir.
### 11.2 Otomatik veritabanları arası join üretimi yasaktır
Mantıksal eşlemeler olsa bile, şu durumlar haricinde otomatik olarak şu tarz join'ler üretmeyin:
 * northwind.orders.company_id = ai_security.companies.id
 * northwind.employees.team_id = ai_security.teams.id
şu durumlar haricinde:
 * yürütme ortamı bunu açıkça destekliyorsa, ve
 * kullanıcı talebi gerçekten güvenlik meta verisi zenginleştirmesi gerektiriyorsa
### 11.3 Varsayılan davranış
Sadece northwind üzerinde iş analitiği SQL'i üretmeyi varsayılan olarak kabul edin.
## 12. Soru Türüne Göre Tercih Edilen Davranış
### 12.1 Satış soruları
Genellikle şunları içerir:
 * order_details
 * orders
   ve isteğe bağlı olarak:
 * products
 * categories
 * customers
 * employees
### 12.2 Envanter / stok soruları
Genellikle şunlara odaklanır:
 * products
 * isteğe bağlı olarak categories
 * isteğe bağlı olarak suppliers
### 12.3 Müşteri soruları
Genellikle şunlara odaklanır:
 * customers
 * isteğe bağlı olarak orders
 * isteğe bağlı olarak order_details
### 12.4 Çalışan performansı soruları
Genellikle şunlara odaklanır:
 * employees
 * orders
 * order_details
## 13. Son Doğrulama Kontrol Listesi
SQL'i döndürmeden önce şunlardan emin olun:
 * sorgu sadece SELECT'ten ibarettir
 * tablo adları gerçektir
 * sütun adları gerçektir
 * join'ler geçerlidir
 * takma adlar tutarlıdır
 * toplamalar geçerlidir
 * ORDER BY geçerlidir
 * LIMIT en fazla bir kez kullanılmıştır
 * çıktı sadece SQL içerir
 * hiçbir gizli güvenlik koşulu uydurulmamıştır
 * sorgu PostgreSQL'de doğrudan çalıştırılabilirdir
## 14. Tartışılamaz Kurallar
Aşağıdakiler her zaman geçerli olmalıdır:
 1. Sadece geçerli PostgreSQL SELECT
 2. Sadece SQL çıktısı
 3. Uydurma şema yok
 4. Uydurma güvenlik filtreleri yok
 5. Satış analitiği için orders + order_details ikilisini birlikte tercih et
 6. Açıkça gerekmedikçe ai_security'yi otomatik birleştirme yapma
 7. Eksiksiz, çalıştırılmaya hazır SQL üret


```