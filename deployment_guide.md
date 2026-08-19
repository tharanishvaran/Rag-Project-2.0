# 🎁 100% FREE Hosting Guide (Zero Credit Card Required)

This guide shows you how to host your entire **SmartDoc RAG AI 2.0** application **100% FREE forever** without entering any credit card information!

---

## 🟢 100% Free Tier Breakdown

| Component | Provider | Cost | Credit Card Needed? |
| :--- | :--- | :--- | :--- |
| **Frontend** | **Vercel** | **$0 / Free Forever** | ❌ No |
| **Backend API** | **Render.com** | **$0 / Free Forever** | ❌ No |
| **Database** | **Aiven.io** or **TiDB Cloud** | **$0 / Free Forever** | ❌ No |

---

## 🛠️ Step 1: Create Free MySQL Database on TiDB Cloud or Aiven

### Option A: TiDB Cloud (Recommended - Free Serverless MySQL)
1. Go to **[TiDB Cloud (tidbcloud.com)](https://tidbcloud.com)** and sign up with your **Google Account** (No credit card needed).
2. Click **Create Cluster** → Choose **Serverless (Free)**.
3. Once created, click **Connect** → Copy your connection details:
   - Host
   - User
   - Password
   - Port (4000 or 3306)
4. Your `DATABASE_URL` format:
   ```env
   DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:<port>/test
   ```

---

## 🛠️ Step 2: Host Flask Backend for FREE on Render.com

1. Push your project code to **GitHub**.
2. Sign up on **[Render.com](https://render.com)** with your GitHub account (No credit card needed).
3. Click **New +** → **Web Service** → Select your GitHub repo.
4. Fill in the following details:
   - **Name**: `smartdoc-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Instance Type**: **Free ($0/month)**
5. Under **Environment Variables**, click **Add Environment Variable**:

   | Key | Value |
   | :--- | :--- |
   | `FLASK_ENV` | `production` |
   | `DATABASE_URL` | `mysql+pymysql://username:password@host:port/dbname` |
   | `GEMINI_API_KEY` | `your-gemini-api-key` |
   | `JWT_SECRET_KEY` | `my-secret-key-12345` |
   | `PYTHON_VERSION` | `3.11.0` |

6. Click **Create Web Service**. Render will deploy your API and give you a free URL (e.g. `https://smartdoc-backend.onrender.com`).

---

## 🛠️ Step 3: Host React Frontend for FREE on Vercel

1. Sign up on **[Vercel.com](https://vercel.com)** using your **GitHub** account (No credit card needed).
2. Click **Add New...** → **Project** → Select your `Rag-Project-2.0` repository.
3. Configure settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Expand **Environment Variables** and add:

   | Key | Value |
   | :--- | :--- |
   | `VITE_API_BASE_URL` | `https://smartdoc-backend.onrender.com/api` |

5. Click **Deploy**. In under 1 minute, Vercel will build your website and provide a free live link (e.g. `https://smartdoc-ai.vercel.app`)!

---

## 📌 Summary Checklist
- [x] TiDB Cloud / Aiven (Free MySQL DB - $0)
- [x] Render.com (Free Python Backend API - $0)
- [x] Vercel (Free React Web App - $0)

🎉 Your application is now live on the internet 100% free!
