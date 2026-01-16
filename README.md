
# Internal Website Intelligence & Contact Discovery Tool

A full-stack internal web application that allows authenticated users to submit a company website URL and automatically extract structured company and contact information using web scraping and AI.

The system scrapes public pages, extracts contact details, formats results into validated JSON using an LLM, stores them in a database, and displays them in a clean UI with history tracking.

📦 DELIVERABLE 1: Source Code Structure

internal-website-intel/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       └── scans.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   └── users.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── scan.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── scan.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ultimate_scraper.py
│   │   │   ├── ultimate_extractor.py
│   │   │   ├── llm_service.py
│   │   │   └── database_service.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── rate_limit.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── validators.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   └── history/
│   │       ├── page.tsx
│   │       └── [id]/
│   │           └── page.tsx
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── ScanForm.tsx
│   │   ├── ScanResult.tsx
│   │   └── HistoryList.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── auth.ts
│   ├── types/
│   │   └── index.ts
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── .env.local.example
│   └── README.md
├── .gitignore
└── README.md (main)

✨ Features
Core

Login-only authentication using JWT (no signup)

Website scraping (homepage + relevant pages like About/Contact)

Contact extraction (emails, phone numbers, social links, addresses)

AI-powered structuring using Google Gemini (validated JSON output)

Database persistence using SQLite + SQLAlchemy

History page with pagination and delete support

Protected frontend routes

Bonus

Rate limiting (login & scan endpoints)

Multi-strategy scraping (BeautifulSoup + Selenium)

JSON export for scan results

Progress indicators & loading states

Responsive UI with Tailwind CSS

🛠 Tech Stack

Frontend: Next.js (App Router), TypeScript, Tailwind CSS

Backend: FastAPI (Python)

Database: SQLite (via SQLAlchemy ORM)

AI: Google Gemini (structured JSON output)

Scraping: BeautifulSoup + Selenium

Auth: JWT (python-jose)

Rate Limiting: SlowAPI

🚀 Setup & Run
Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload


Backend runs at: http://localhost:8000
API Docs: http://localhost:8000/docs

Frontend
cd frontend
npm install
cp .env.local.example .env.local
npm run dev


Frontend runs at: http://localhost:3000

🔐 Default Credentials

admin / password123

demo / password123

🧠 How It Works (High-Level)

User logs in → backend issues JWT

User submits a website URL

Backend scrapes relevant pages

Contact info is extracted deterministically

AI formats data into structured JSON

Output is validated with Pydantic

Result is saved to database

Frontend displays result and history

⚙️ Design Notes

SQLite chosen for easy local development (swap to PostgreSQL via env)

AI output is strictly validated before persistence

Scraping is best-effort due to website variability

JWT stored in localStorage for simplicity (cookies recommended for prod)

📌 Known Limitations

History detail route (/history/[id]) is optional polish; results are already viewable via History page

Scraping may fail on heavily protected websites

📄 License

Internal demo project for assignment evaluation.

