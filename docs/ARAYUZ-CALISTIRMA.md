# Arayüzü çalıştırma

Modern arayüz (React + Vite) ve backend (FastAPI) ile doğal dil → SQL akışını tarayıcıda deneyebilirsin.

## Gereksinimler

- **Python** (zaten var)
- **Node.js** (frontend için): [nodejs.org](https://nodejs.org) — LTS sürümünü indir, kur (npm birlikte gelir)

## 1. Backend’i başlat

Proje kökünde (`C:\Users\esrag\Desktop\chatbot`):

```powershell
py -m pip install fastapi uvicorn python-dotenv google-generativeai
py -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend çalışır: http://localhost:8000  
`.env` içinde `GEMINI_API_KEY` tanımlı olmalı.

## 2. Frontend’i başlat

**Yeni bir terminal** aç, proje kökünde:

```powershell
cd frontend
npm install
npm run dev
```

Tarayıcıda aç: **http://localhost:5173**

## 3. Nasıl kullanılır?

1. Metin kutusuna doğal dilde soru yaz (örn. "En çok satan 5 ürün hangileri?").
2. **SQL üret** butonuna tıkla.
3. Üretilen SQL aşağıda görünür. Sonuç tablosu Köprü API’si eklendiğinde doldurulacak.

## Klasör yapısı

- **backend/** — FastAPI; `POST /api/ask` → `ai.nl_to_sql` çağrısı.
- **frontend/** — React + Vite; tek sayfa, soru + SQL + (ileride) sonuç alanı.
