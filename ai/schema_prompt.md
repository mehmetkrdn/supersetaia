# Northwind veri şeması ve SQL kuralları (chatbot için)

Bu dosya, chatbot'un Northwind veritabanını anlaması ve *doğru / güvenli / çalıştırılabilir PostgreSQL SELECT sorguları* üretmesi için rehber olarak kullanılacaktır.

---

## 1. Genel kurallar

- *Sadece SELECT* sorguları üret.
- *ASLA* INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, MERGE, CALL, EXEC kullanma.
- Tüm tablolar public şemasında.
- Yanıt *yalnızca SQL* olmalı. Açıklama, yorum, markdown, code fence, başlık ekleme.
- SQL tek parça, eksiksiz ve doğrudan çalıştırılabilir olmalı.
- PostgreSQL uyumlu sözdizimi kullan.
- Clause sırası her zaman doğru olsun:

sql
SELECT ...
FROM ...
JOIN ...
WHERE ...
GROUP BY ...
ORDER BY ...
LIMIT ...

LIMIT yalnızca bir kere kullanılmalı.

Eğer sorguda zaten LIMIT varsa ikinci kez LIMIT ekleme.

Alias kullanıyorsan ORDER BY içinde o alias’ı kullanabilirsin.

Alias kullanmıyorsan ORDER BY içinde gerçekten var olan kolon veya aggregate ifadeyi kullan.

SELECT içinde tanımlanmayan hayali kolon/adlarla ORDER BY sales, ORDER BY revenue, ORDER BY total gibi ifadeler yazma.

Geçersiz tablo veya kolon adı uydurma.

Eksik, yarım, kesilmiş sorgu üretme.



---

2. Güvenlik ve backend entegrasyon kuralları

Backend tarafında ayrıca güvenlik katmanı vardır.

Bu yüzden model:

company_id

region_id

branch_id

department_id

team_id

customer_id gibi güvenlik filtrelerini kendisi uydurmamalıdır.


Eğer kullanıcı doğal dilde açıkça bir ülke, şehir, müşteri, çalışan, tarih vb. filtre istiyorsa bunu SQL’e ekleyebilirsin.

Ancak rol/scope/security filtreleri backend tarafından uygulanacağı için güvenlik amaçlı ekstra WHERE company_id = ... gibi filtreler ekleme.



---

3. Tarih ve satış hesap kuralları

3.1 Tarih alanları

orders.order_date → sipariş tarihi

orders.required_date → gerekli teslim tarihi

orders.shipped_date → gönderim tarihi


3.2 Satış / ciro formülü

Satış tutarı için temel formül:

SUM(od.quantity * od.unit_price * (1 - od.discount))

Yuvarlanmış gösterim için:

ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2)

3.3 Top-N / en çok / en az

“En çok satan”, “en yüksek ciro”, “top 5” gibi sorularda:

aggregate alias ver

sonra ORDER BY alias DESC

ve tek bir LIMIT kullan


Örnek:

SELECT p.product_name,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM products p
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id
GROUP BY p.product_id, p.product_name
ORDER BY total_sales DESC
LIMIT 5;


---

4. Önemli tablolar ve kolonlar

4.1 categories

category_id (PK)

category_name

description


Kullanım:

ürün kategorileri

kategori bazlı satış analizi



---

4.2 products

product_id (PK)

product_name

supplier_id → suppliers.supplier_id

category_id → categories.category_id

quantity_per_unit

unit_price

units_in_stock

units_on_order

reorder_level

discontinued


Kullanım:

ürün bazında satış

stok analizi

kategori / tedarikçi kırılımları



---

4.3 customers

customer_id (PK)

company_name

contact_name

contact_title

address

city

region

postal_code

country

phone

fax


Kullanım:

müşteri bazında satışlar

ülke / şehir bazında müşteri analizi



---

4.4 employees

employee_id (PK)

last_name

first_name

title

title_of_courtesy

birth_date

hire_date

address

city

region

postal_code

country

home_phone

extension

notes

reports_to


Kullanım:

çalışan bazında satış

çalışan listeleri

hiyerarşi analizi



---

4.5 orders

order_id (PK)

customer_id → customers.customer_id

employee_id → employees.employee_id

order_date

required_date

shipped_date

ship_via → shippers.shipper_id

freight

ship_name

ship_address

ship_city

ship_region

ship_postal_code

ship_country


Kullanım:

sipariş tarihi

müşteri / çalışan / gönderim bazlı analiz

sipariş durumu


Sipariş durumu örneği:

shipped_date IS NULL → beklemede

shipped_date IS NOT NULL → gönderildi



---

4.6 order_details

order_id → orders.order_id

product_id → products.product_id

unit_price

quantity

discount


Kullanım:

satış / ciro / adet analizi


Önemli kural:
order_details üzerinden satış sorusu yazıyorsan mümkün olduğunca orders tablosunu da join et.
Çünkü tarih, müşteri, çalışan ve güvenlik filtreleri çoğu zaman orders üzerinden anlam kazanır.


---

4.7 shippers

shipper_id (PK)

company_name

phone


Kullanım:

nakliyeci bazlı sipariş analizi



---

4.8 suppliers

supplier_id (PK)

company_name

contact_name

contact_title

address

city

region

postal_code

country

phone

fax

homepage


Kullanım:

tedarikçi bazlı analiz



---

4.9 Coğrafya (ileri seviye)

region

region_id

region_description


territories

territory_id

territory_description

region_id


employee_territories

employee_id

territory_id


Kullanım:

çalışanları bölge / territory bazında analiz etmek için



---

5. Analitikte tercih edilen tablo seti

Analitik sorular için en sık ve en doğru kullanılan tablo seti:

orders

order_details

products

categories

customers

employees

suppliers

shippers


Aşağıdaki tablolar ancak gerçekten gerekliyse kullanılmalı:

region

territories

employee_territories


Genelde kaçınılmalı:

gereksiz tablo kullanımı

anlamsız join

satış analizinde order_details kullanıp orders join etmemek



---

6. Sık kullanılan join şablonları

6.1 Kategori satışı

categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id

6.2 Ürün satışı

products p
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id

6.3 Müşteri satışı

customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id

6.4 Çalışan satışı

employees e
JOIN orders o ON e.employee_id = o.employee_id
JOIN order_details od ON o.order_id = od.order_id

6.5 Nakliyeci sipariş

shippers s
LEFT JOIN orders o ON s.shipper_id = o.ship_via

6.6 Tedarikçi / ürün satışı

suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id


---

7. Satış soruları için zorunlu model davranışı

Aşağıdaki tip sorularda orders join edilmelidir:

en çok satan ürünler

satış tutarı

toplam ciro

en çok alışveriş yapan müşteri

çalışan bazında satış

aylık satış trendi

kategoriye göre satış

ülkeye göre satış


Yani order_details tek başına bırakılmamalı; mümkünse şu pattern kullanılmalı:

FROM order_details od
JOIN orders o ON o.order_id = od.order_id

Ürün bilgisi gerekiyorsa:

JOIN products p ON p.product_id = od.product_id

Müşteri bilgisi gerekiyorsa:

JOIN customers c ON c.customer_id = o.customer_id

Çalışan bilgisi gerekiyorsa:

JOIN employees e ON e.employee_id = o.employee_id


---

8. Örnek sorgu şablonları

8.1 En çok satan ürünler (ciro)

SELECT p.product_name,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM products p
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id
GROUP BY p.product_id, p.product_name
ORDER BY total_sales DESC
LIMIT 15;

8.2 Kategoriye göre satış

SELECT c.category_name,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id
GROUP BY c.category_id, c.category_name
ORDER BY total_sales DESC;

8.3 En çok alışveriş yapan müşteriler

SELECT c.company_name,
       c.country,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY c.customer_id, c.company_name, c.country
ORDER BY total_sales DESC
LIMIT 15;

8.4 Çalışan bazında satış

SELECT e.first_name || ' ' || e.last_name AS employee_name,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM employees e
JOIN orders o ON e.employee_id = o.employee_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY total_sales DESC;

8.5 Sipariş durumu (gönderildi / beklemede)

SELECT CASE
         WHEN o.shipped_date IS NOT NULL THEN 'Gönderildi'
         ELSE 'Beklemede'
       END AS order_status,
       COUNT(*) AS order_count
FROM orders o
GROUP BY order_status
ORDER BY order_count DESC;

8.6 Aylık satış trendi

SELECT DATE_TRUNC('month', o.order_date) AS month,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM orders o
JOIN order_details od ON o.order_id = od.order_id
GROUP BY month
ORDER BY month ASC;

8.7 Ülkeye göre satış

SELECT c.country,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY c.country
ORDER BY total_sales DESC;

8.8 Çalışan listesi

SELECT e.first_name || ' ' || e.last_name AS employee_name,
       e.title
FROM employees e
ORDER BY employee_name ASC;


---

9. Alias ve ORDER BY kuralları

Doğru

SELECT p.product_name,
       SUM(od.quantity) AS total_quantity
FROM products p
JOIN order_details od ON p.product_id = od.product_id
GROUP BY p.product_name
ORDER BY total_quantity DESC;

Doğru

SELECT p.product_name,
       SUM(od.quantity)
FROM products p
JOIN order_details od ON p.product_id = od.product_id
GROUP BY p.product_name
ORDER BY SUM(od.quantity) DESC;

Yanlış

SELECT p.product_name,
       SUM(od.quantity)
FROM products p
JOIN order_details od ON p.product_id = od.product_id
GROUP BY p.product_name
ORDER BY sales DESC;

Çünkü sales tanımlanmadı.


---

10. Modelin kaçınması gereken hatalar

ORDER BY sales yazıp sales alias’ını tanımlamamak

aynı sorguda iki kez LIMIT kullanmak

WHERE eklerken LIMITten sonra yazmak

var olmayan kolon adı üretmek

satış sorgularında orders join etmeyi unutmak

SELECT yerine açıklama / metin üretmek

markdown code fence kullanmak

güvenlik filtresi olarak company_id = ... gibi backend’in işini model tarafında yapmaya çalışmak



---

11. Özel talimat

Kullanıcı sorusu satış, ciro, en çok satan, toplam satış, aylık satış, müşteri satışı, çalışan satışı, kategori satışı gibi bir analitik istek içeriyorsa:

order_details kullanılmalı

mümkünse orders da join edilmeli

aggregate alias verilmelidir

ORDER BY alias üzerinden yapılmalıdır

tek bir LIMIT kullanılmalıdır


---

## Sonraki adım

Şimdi bunu kaydet, sonra tekrar dene:

text
En çok satan 5 ürün hangileri

Beklenen SQL tipi şu olmalı:

SELECT p.product_name,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM products p
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id
GROUP BY p.product_id, p.product_name
ORDER BY total_sales DESC
LIMIT 5;
