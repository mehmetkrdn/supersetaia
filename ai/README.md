# AI katmanı: Doğal dil → SQL (Northwind)

Bu klasör **“Zekayı kurgulayan (AI uzmanı)”** işinin çıktılarını içerir: veritabanı şemasının AI’ya öğretilmesi ve doğal dil sorularının PostgreSQL SELECT sorgusuna çevrilmesi için **Gemini API** kullanılır.

## Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `schema_prompt.md` | Northwind tabloları, kolonlar, join’ler ve güvenlik kuralları. Gemini’ye verilen “şema rehberi”. |
| `nl_to_sql.py` | Doğal dil sorusu alır, Gemini’ye şema + soruyu gönderir, dönen SQL’i (sadece SELECT) döndürür. |
| `requirements.txt` | Python bağımlılığı: `google-generativeai`. |

## Kurulum

1. Sanal ortam (önerilir):
   ```bash
   cd ai
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Gemini API anahtarı**  
   Proje kökündeki **`.env`** dosyasına yazın (bu dosya `.gitignore`’da olduğu için GitHub’a gitmez):

   ```
   GEMINI_API_KEY=buraya-anahtarınızı-yapıştırın
   ```

   - `.env` yoksa `.env.example` dosyasını kopyalayıp `.env` yapın, sonra anahtarı ekleyin.
   - [Google AI Studio](https://aistudio.google.com/apikey) veya Google Cloud üzerinden API anahtarı alabilirsiniz.
   - Alternatif: `GOOGLE_API_KEY` da okunur.

## Kullanım

### Komut satırı

```bash
cd ai
python nl_to_sql.py "En çok satan 5 ürün hangileri?"
```

Çıktı: Üretilen SQL (sadece SELECT).

### Python içinden

```python
from ai.nl_to_sql import question_to_sql

sql = question_to_sql("Kategoriye göre toplam satışları listele")
print(sql)
```

İsteğe bağlı olarak kendi şema metnini de verebilirsiniz:

```python
sql = question_to_sql("Almanya'daki müşteri sayısı?", schema_prompt=my_schema_text)
```

## Güvenlik

- Script yalnızca **SELECT** (ve gerekirse **WITH**) üretilmesine izin verir. INSERT/UPDATE/DELETE/DROP vb. dönerse `ValueError` fırlatılır.
- Veritabanına bağlanmaz; sadece SQL metni üretir. Sorguyu çalıştırmak “Veriyi bağlayan (Köprü)” katmanının işidir.

## Sonraki adımlar (diğer roller)

- **Yetki uzmanı:** Rol/ülke filtrelerini bu katmana nasıl geçireceğinizi (ör. `question_to_sql`’e ek parametre) ve SQL’e nasıl yansıtacağınızı tasarlayın.
- **Köprü uzmanı:** `question_to_sql` çıktısını PostgreSQL’de çalıştırıp sonucu chatbot ekranında gösterecek backend’i yazın.
