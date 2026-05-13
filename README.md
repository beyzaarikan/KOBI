# 🛒 Kobi.app — KOBİ'ler için AI Destekli Stok & Sipariş Yönetimi

> **KOBİ'ler ve kooperatifler için stok süreçlerini otomatikleştiren, yapay zeka ile müşteri desteği sunan ve sipariş gecikmelerini öngören modern SaaS platformu.**

---

## 🚀 Proje Hakkında

**Kobi.app**, küçük ve orta ölçekli işletmelerin (KOBİ) ve kooperatiflerin günlük operasyonel yükünü azaltmak için tasarlanmış bir yapay zeka destekli yönetim platformudur. Stok tüketim hızını analiz eder, kritik seviyelere ulaşmadan önce uyarı verir ve müşteri destek süreçlerini doğal dil işleme ile otomatikleştirir.

---

## ✨ Özellikler

### 🧠 AI Inventory Intelligence Engine
- Stok seviyelerini gerçek zamanlı analiz eder
- Tüketim hızını ölçerek "X gün sonra bitecek, Y adet sipariş ver" önerisi sunar
- Google Gemini API tabanlı akıllı karar destek sistemi

### 💬 AI Customer Support Agent
- Doğal dil işleme (NLP) ile müşteri sorularını anlayan chatbot
- *"Siparişim nerede?"*, *"Stokta var mı?"* gibi soruları RAG mimarisiyle yanıtlar
- 7/24 otomatik müşteri hizmetleri

### 📊 Modern Dashboard
- Next.js 14 App Router ile geliştirilmiş hızlı ve duyarlı arayüz
- TailwindCSS v4 ve shadcn/ui bileşenleriyle Linear/Stripe estetiği
- Dark-mode destekli kullanıcı arayüzü

### ⚡ Asenkron & Gerçek Zamanlı Mimari
- FastAPI ve WebSockets ile anlık stok uyarıları
- Asenkron veritabanı işlemleri ile yüksek performans

---

## 🛠 Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| **Frontend** | Next.js 14 (App Router), TypeScript, TailwindCSS v4, shadcn/ui |
| **Backend** | FastAPI, SQLAlchemy (Async), PostgreSQL / SQLite |
| **AI** | Google Gemini API (Agent tabanlı iş akışları) |
| **İletişim** | WebSockets, REST API |
| **DevOps** | Docker, Docker Compose |

---

## 📁 Proje Yapısı

```
KOBI/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI uygulama giriş noktası
│   │   ├── routers/              # API endpoint'leri
│   │   ├── services/
│   │   │   └── ai_agent.py       # Inventory & Customer Support Agentları
│   │   ├── models/               # SQLAlchemy modelleri
│   │   └── repositories/         # Veritabanı işlem katmanı
│   ├── scripts/
│   │   └── seed.py               # Demo veri yükleme scripti
│   └── requirements.txt
├── frontend/
│   ├── app/                      # Next.js App Router sayfaları
│   ├── components/               # UI bileşenleri
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Kurulum

### Backend

```bash
# 1. Backend klasörüne geçin
cd backend

# 2. Sanal ortam oluşturun ve aktive edin
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt
# veya manuel kurulum:
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic google-generativeai

# 4. Demo veritabanını hazırlayın
export PYTHONPATH=$(pwd)
python scripts/seed.py

# 5. API sunucusunu başlatın
uvicorn app.main:app --reload
```

API dokümantasyonuna şu adresten ulaşabilirsiniz: [http://localhost:8000/docs](http://localhost:8000/docs)

> **Not:** Google Gemini API kullanımı için `GEMINI_API_KEY` ortam değişkenini ayarlamanız gerekir.

---

### Frontend

```bash
# 1. Frontend klasörüne geçin
cd frontend

# 2. Node.js v20.x gereklidir
node --version   # v20.x olmalı

# 3. Bağımlılıkları yükleyin
npm install

# 4. Geliştirme sunucusunu başlatın
npm run dev
```

Uygulamayı tarayıcıda açın: [http://localhost:3000](http://localhost:3000)

---

### Docker ile Çalıştırma

```bash
docker-compose up --build
```

Tüm servisler otomatik olarak ayağa kalkar.

---

## 🤖 AI Agent Mimarisi

Sistemde `backend/app/services/ai_agent.py` dosyasında tanımlı iki ana Agent bulunur:

### 1. Inventory Agent
- Veritabanındaki ürün ve stok verilerini JSON formatında alır
- Sistem prompt'unda kendisine bir "Inventory Intelligence Engine" rolü atanır
- **Çıktı:** JSON formatında risk düzeyi, tahmini bitiş süresi ve yeniden sipariş miktarı önerisi

### 2. Customer Support Agent
- Mock bir RAG (Retrieval-Augmented Generation) mimarisi kullanır
- Müşteri sorusuna yanıt verebilmek için en güncel sipariş durumları context olarak prompt'a enjekte edilir
- Doğal ve akıcı Türkçe/İngilizce yanıt üretir

---

## 🎬 Demo Senaryoları

### Senaryo 1: Düşük Stok Uyarısı
1. Seed scripti çalıştırıldığında bazı ürünlerin stokları bilinçli olarak eşik değerinin altında oluşturulur
2. Dashboard açıldığında **AI Inventory Insights** paneli saniyeler içinde kritik ürünleri ve önerilen sipariş miktarını gösterir

> Örnek: *"Organik Domates Salçası kritik seviyede! 48 birim sipariş etmenizi öneriyoruz."*

### Senaryo 2: Müşteri Sipariş Sorgusu
1. Sağ alttaki **AI Support Chat** bölümüne *"Siparişim nerede?"* yazın
2. Sistem, en son siparişin güncel durumunu doğal dilde yanıtlar

> Örnek: *"Siparişiniz yola çıktı (In Transit). Tahmini teslim süresi 2 iş günüdür."*

---

## 🏗 Mimari Kararlar

**Neden FastAPI?**
Asenkron yapısı ve Python ekosistemi sayesinde Google Gemini gibi AI servisleriyle mükemmel entegrasyon sağlar; düşük gecikme süresiyle yüksek performans sunar.

**Neden Modüler Monolit?**
Başlangıç hızı ve geliştirme kolaylığı için tüm proje Routers → Services → Repositories katmanlarına ayrılmış tek bir uygulama olarak tasarlandı. İleride trafik artışına bağlı olarak Inventory, Orders ve AI Inference modülleri bağımsız mikroservislere kolayca dönüştürülebilir.

**Neden SQLite (fallback)?**
Yerel geliştirme ve demo ortamları için ek kurulum gerektirmeyen SQLite desteği sağlandı; production ortamında PostgreSQL kullanılması önerilir.
<p align="center">
  <b>Kobi.app</b> — KOBİ'lerin geleceği için yapay zeka 🚀
</p>

---
