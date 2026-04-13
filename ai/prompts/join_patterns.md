
---

````md
# join_patterns.md

## Amaç

Bu doküman, Northwind analitik şeması için standart (canonical) join pattern’lerini tanımlar.

Amaç:
- doğru ilişkilerin kullanılması
- join hatalarının önlenmesi
- eksik veri bağlamının engellenmesi
- LLM’in deterministik SQL üretmesi

Bu dosya özellikle şu hataları önler:
- eksik join
- yanlış join yönü
- gereksiz join
- schema uydurma

---

# 1. Temel Kural

## Altın Kural

Her **satış / ciro / performans** sorusunda:

```sql
order_details + orders birlikte kullanılmalıdır
````

### Zorunlu Pattern

```sql
FROM order_details od
JOIN orders o ON o.order_id = od.order_id
```

### Sebep

* `order_details` → metrik (quantity, price, discount)
* `orders` → bağlam (tarih, müşteri, çalışan, kargo)

`orders` olmadan analiz eksik olur.

---

# 2. Temel Join Pattern’leri

---

## 2.1 Ürün Satış Pattern

### Kullanım

* en çok satan ürünler
* ürün bazlı ciro

```sql
FROM products p
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id
```

---

## 2.2 Kategori Satış Pattern

### Kullanım

* kategori bazlı satış
* kategori karşılaştırma

```sql
FROM categories cat
JOIN products p ON cat.category_id = p.category_id
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id
```

---

## 2.3 Müşteri Satış Pattern

### Kullanım

* müşteri bazlı satış
* en çok alışveriş yapanlar

```sql
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
```

---

## 2.4 Çalışan Satış Pattern

### Kullanım

* çalışan performansı
* satış temsilcisi analizi

```sql
FROM employees e
JOIN orders o ON e.employee_id = o.employee_id
JOIN order_details od ON o.order_id = od.order_id
```

---

## 2.5 Tedarikçi Satış Pattern

### Kullanım

* tedarikçi performansı

```sql
FROM suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
JOIN order_details od ON p.product_id = od.product_id
JOIN orders o ON o.order_id = od.order_id
```

---

## 2.6 Kargo / Nakliye Pattern

### Kullanım

* kargo firması analizi
* sipariş dağılımı

```sql
FROM shippers sh
LEFT JOIN orders o ON sh.shipper_id = o.ship_via
```

---

## 2.7 Stok / Envanter Pattern

### Kullanım

* stok analizi
* ürün durumu

```sql
FROM products p
LEFT JOIN categories cat ON p.category_id = cat.category_id
LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
```

NOT:

* satış yoksa `order_details` kullanılmaz

---

# 3. Kombine Pattern’ler

---

## 3.1 Full Analiz Pattern (Dashboard)

### Kullanım

* çok boyutlu analiz

```sql
FROM order_details od
JOIN orders o ON o.order_id = od.order_id
JOIN products p ON p.product_id = od.product_id
JOIN categories cat ON cat.category_id = p.category_id
JOIN customers c ON c.customer_id = o.customer_id
JOIN employees e ON e.employee_id = o.employee_id
```

---

## 3.2 Tarih Bazlı Analiz

```sql
FROM order_details od
JOIN orders o ON o.order_id = od.order_id
```

Tarih alanı:

```sql
o.order_date
```

---

## 3.3 Sipariş Durumu

```sql
FROM orders o
```

Durum:

```sql
-- bekleyen
o.shipped_date IS NULL

-- gönderilen
o.shipped_date IS NOT NULL
```

---

# 4. Join Yönü Kuralları

## 4.1 FK yönünü takip et

Doğru:

```sql
orders.customer_id → customers.customer_id
```

```sql
JOIN customers c ON c.customer_id = o.customer_id
```

---

## 4.2 Keyfi ters join yapma

Yanlış:

```sql
JOIN orders o ON o.customer_id = c.customer_id
```

---

# 5. Join Tipi Kuralları

## 5.1 Varsayılan: INNER JOIN

* normal analizlerde kullan

## 5.2 LEFT JOIN

* eksik veri önemliyse
* tüm kayıtlar korunacaksa

---

# 6. Kritik Anti-Pattern’ler

---

## 6.1 orders olmadan order_details

❌ Yanlış:

```sql
FROM order_details od
```

✔ Doğru:

```sql
FROM order_details od
JOIN orders o ON o.order_id = od.order_id
```

---

## 6.2 categories → orders direkt

❌ Yanlış:

```sql
categories → orders
```

✔ Doğru:

```sql
categories → products → order_details → orders
```

---

## 6.3 Yanlış satış hesaplama

❌ Yanlış:

```sql
SUM(products.unit_price)
```

✔ Doğru:

```sql
SUM(od.quantity * od.unit_price * (1 - od.discount))
```

---

## 6.4 Alakasız join

❌ Yanlış:

```sql
customers → suppliers
```

---

## 6.5 Gereksiz tüm tabloları join etmek

❌ Yanlış

✔ Sadece gereken tablolar

---

# 7. Cross-DB Join Kuralları

## 7.1 Varsayılan

Şunlara join yapma:

* companies
* branches
* departments
* teams
* regions

---

## 7.2 Ne zaman yapılır?

Sadece:

* kullanıcı isterse
* sistem destekliyorsa

---

## 7.3 Sebep

* güvenlik ihlali önlenir
* yanlış veri bağlamı engellenir
* sistem uyumluluğu korunur

---

# 8. Performans Kuralları

* minimum join kullan
* gereksiz GROUP BY kullanma
* gereksiz DISTINCT kullanma

---

# 9. Pattern Seçim Mantığı

| Soru tipi             | Pattern        |
| --------------------- | -------------- |
| en çok satan ürün     | ürün satış     |
| kategoriye göre satış | kategori satış |
| müşteri bazlı satış   | müşteri        |
| çalışan performansı   | çalışan        |
| stok durumu           | inventory      |
| kargo analizi         | shipping       |

---

# 10. Final Kontrol Listesi

SQL üretmeden önce:

* doğru tablo seçildi mi
* doğru join yolu kullanıldı mı
* orders + order_details var mı (satışta)
* gereksiz join var mı
* FK yönü doğru mu
* user intent karşılanıyor mu

```

---

