# FaceSwap App - Deployment Guide

This repository contains a full-stack FaceSwap application featuring:
- **Frontend**: Next.js (App Router) + Tailwind CSS + Clerk Auth
- **Backend**: FastAPI + SQLAlchemy + Celery
- **Worker**: Celery + InsightFace + ONNX Runtime (CPU optimized)
- **Storage**: Supabase Storage
- **Payments**: Razorpay

## 🚀 Deployment

### Prerequisites
You will need accounts on:
1.  **GitHub** (to host this code)
2.  **Supabase** (for Database & Storage)
3.  **Clerk** (for Authentication)
4.  **Razorpay** (for Payments)
5.  **Railway** or **Render** (to host Backend & Worker)
6.  **Vercel** (to host Frontend)

---

### 1. Environment Variables
You will need to provide these variables to your cloud providers.

#### Backend & Worker (Railway/Render)
| Variable | Description |
|---|---|
| `DATABASE_URL` | Postgres connection string (from Supabase/Railway) |
| `REDIS_URL` | Redis connection string (from Railway/Render) |
| `SUPABASE_URL` | Your Supabase Project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Your Supabase **Service Role** Key (NOT Anon key) |
| `RAZORPAY_KEY_ID` | Razorpay Key ID |
| `RAZORPAY_KEY_SECRET` | Razorpay Key Secret |
| `CLERK_SECRET_KEY` | Clerk Secret Key |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`| Clerk Publishable Key (Optional for backend, needed for frontend) |

#### Frontend (Vercel)
| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | URL of your deployed Backend (e.g. `https://my-api.railway.app`) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk Publishable Key |
| `CLERK_SECRET_KEY` | Clerk Secret Key |
| `NEXT_PUBLIC_RAZORPAY_KEY_ID` | Razorpay Key ID |

---

### 2. Deploying Backend & Worker (Railway/Render)

This project uses a single `Dockerfile` for both services.

**For The Web Service (API):**
- **Build Command**: (Default)
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

**For The Background Worker:**
- **Build Command**: (Default)
- **Start Command**: `celery -A worker.tasks.celery_app worker --loglevel=info`

*Note: Ensure both services share the same `REDIS_URL` and `DATABASE_URL`.*

---

### 3. Deploying Frontend (Vercel)

1.  Import this repository into Vercel.
2.  **Framework Preset**: Next.js
3.  **Root Directory**: `frontend` (Important! Click "Edit" next to Root Directory)
4.  Add the Environment Variables listed above.
5.  Deploy!

---

### Local Development

1.  **Backend**: `cd backend && uvicorn main:app --reload`
2.  **Worker**: `cd worker && celery -A tasks.celery_app worker --loglevel=info -P solo`
3.  **Frontend**: `cd frontend && npm run dev`
