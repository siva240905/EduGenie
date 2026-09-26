# EduGenie Deployment Guide

This guide covers step-by-step instructions to deploy **EduGenie** to Render, Vercel, Railway, or Docker.

---

## 🚀 Method 1: Deploy on Render.com (Recommended Free Hosting)

Render provides free hosting for FastAPI applications directly linked to your GitHub repository.

### Steps:
1. Log in to [Render.com](https://render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository: `https://github.com/siva240905/EduGenie`.
4. Configure the settings:
   - **Name**: `edugenie`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: `Free`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key)*
6. Click **Create Web Service**. Your app will be live at `https://edugenie.onrender.com`.

---

## ⚡ Method 2: Deploy on Vercel

1. Go to [Vercel Dashboard](https://vercel.com).
2. Import your GitHub repository `https://github.com/siva240905/EduGenie`.
3. Add environment variable `GEMINI_API_KEY`.
4. Deploy! Vercel will automatically use `vercel.json` and build the FastAPI app.

---

## 🐳 Method 3: Containerized Deployment (Docker)

Build and run locally or on any cloud server with Docker:

```bash
# 1. Build image
docker build -t edugenie:latest .

# 2. Run container
docker run -d -p 8000:8000 -e GEMINI_API_KEY="your_key" edugenie:latest
```
