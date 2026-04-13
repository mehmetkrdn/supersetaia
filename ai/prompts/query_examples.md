
Bu dosya LLM’in **nasıl düşünmesi gerektiğini öğretir (few-shot layer)**

---

````md
# query_examples.md

## Amaç

Bu doküman, doğal dil → SQL dönüşümünde modelin davranışını yönlendirmek için örnek soru-cevap (NL → SQL) çiftleri içerir.

Amaç:
- doğru pattern seçimini öğretmek
- metrik hesaplamalarını standartlaştırmak
- alias kullanımını oturtmak
- LLM’in hatasız SQL üretmesini sağlamak

---

# 1. Satış (Ciro) Soruları

---

## Örnek 1: En çok satan ürünler

### Soru
En çok satan 10 ürünü getir

### SQL
```sql
SELECT p.product_name,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM products p
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id
GROUP BY p.product_id, p.product_name
ORDER BY total_sales DESC
LIMIT 10;
````

---

## Örnek 2: Kategoriye göre satış

### Soru

Kategori bazında toplam satışları getir

### SQL

```sql
SELECT cat.category_name,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM categories cat
JOIN products p ON cat.category_id = p.category_id
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id
GROUP BY cat.category_id, cat.category_name
ORDER BY total_sales DESC;
```

---

## Örnek 3: Aylık satış trendi

### Soru

Aylara göre toplam satışları getir

### SQL

```sql
SELECT DATE_TRUNC('month', o.order_date) AS month,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM order_details od
JOIN orders o ON o.order_id = od.order_id
GROUP BY month
ORDER BY month;
```

---

# 2. Müşteri Analizi

---

## Örnek 4: En çok alışveriş yapan müşteriler

### Soru

En çok alışveriş yapan 10 müşteriyi getir

### SQL

```sql
SELECT c.company_name,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY c.customer_id, c.company_name
ORDER BY total_sales DESC
LIMIT 10;
```

---

## Örnek 5: Ülkeye göre müşteri sayısı

### Soru

Ülkelere göre müşteri sayısını getir

### SQL

```sql
SELECT c.country,
       COUNT(*) AS customer_count
FROM customers c
GROUP BY c.country
ORDER BY customer_count DESC;
```

---

# 3. Çalışan Analizi

---

## Örnek 6: Çalışan bazlı satış

### Soru

Çalışanlara göre toplam satışları getir

### SQL

```sql
SELECT e.first_name || ' ' || e.last_name AS employee_name,
       ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM employees e
JOIN orders o ON e.employee_id = o.employee_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY total_sales DESC;
```

---

# 4. Sipariş Analizi

---

## Örnek 7: Bekleyen siparişler

### Soru

Bekleyen siparişleri getir

### SQL

```sql
SELECT o.order_id,
       o.order_date,
       o.shipped_date
FROM orders o
WHERE o.shipped_date IS NULL;
```

---

## Örnek 8: Gönderilen sipariş sayısı

### Soru

Gönderilen sipariş sayısını getir

### SQL

```sql
SELECT COUNT(*) AS shipped_orders
FROM orders o
WHERE o.shipped_date IS NOT NULL;
```

---

# 5. Ürün / Stok Analizi

---

## Örnek 9: Stokta az kalan ürünler

### Soru

Stokta 10'dan az kalan ürünleri getir

### SQL

```sql
SELECT p.product_name,
       p.units_in_stock
FROM products p
WHERE p.units_in_stock < 10
ORDER BY p.units_in_stock ASC;
```

---

## Örnek 10: Ürün bazlı satış adedi

### Soru

Ürünlere göre toplam satış adetlerini getir

### SQL

```sql
SELECT p.product_name,
       SUM(od.quantity) AS total_quantity
FROM products p
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id
GROUP BY p.product_id, p.product_name
ORDER BY total_quantity DESC;
```

---

# 6. Kargo / Nakliye Analizi

---

## Örnek 11: Kargo firmasına göre sipariş sayısı

### Soru

Kargo firmalarına göre sipariş sayılarını getir

### SQL

```sql
SELECT sh.company_name,
       COUNT(o.order_id) AS order_count
FROM shippers sh
LEFT JOIN orders o ON sh.shipper_id = o.ship_via
GROUP BY sh.shipper_id, sh.company_name
ORDER BY order_count DESC;
```

---

# 7. Tedarikçi Analizi

---

## Örnek 12: Tedarikçiye göre ürün sayısı

### Soru

Tedarikçilere göre ürün sayısını getir

### SQL

```sql
SELECT s.company_name,
       COUNT(p.product_id) AS product_count
FROM suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
GROUP BY s.supplier_id, s.company_name
ORDER BY product_count DESC;
```

---

# 8. Tarih Filtreli Sorgular

---

## Örnek 13: Belirli tarihten sonraki satışlar

### Soru

1997 yılından sonraki satışları getir

### SQL

```sql
SELECT ROUND(SUM(od.quantity * od.unit_price * (1 - od.discount))::numeric, 2) AS total_sales
FROM order_details od
JOIN orders o ON o.order_id = od.order_id
WHERE o.order_date >= DATE '1997-01-01';
```

---

# 9. Önemli Öğrenme Kuralları

## Model davranışı

* satış sorularında:
  → order_details + orders kullan

* ciro sorularında:
  → doğru formül kullan

* top N sorularında:
  → ORDER BY + LIMIT

* tarih sorularında:
  → order_date kullan

* müşteri sorularında:
  → customers + orders

---

# 10. Anti-Pattern Örnekleri

---

## Yanlış 1

```sql
SELECT SUM(unit_price) FROM products;
```

❌ yanlış (ciro değil)

---

## Doğru

```sql
SELECT SUM(od.quantity * od.unit_price * (1 - od.discount))
FROM order_details od;
```

---

## Yanlış 2

```sql
FROM order_details
```

❌ eksik

---

## Doğru

```sql
FROM order_details od
JOIN orders o ON o.order_id = od.order_id
```

---

# 11. Tasarım Mantığı

Bu dosya:

* modelin karar verme sürecini yönlendirir
* pattern öğrenmesini sağlar
* doğru join ve metric kullanımını pekiştirir
* hatalı SQL üretimini minimize eder

```

---

```
