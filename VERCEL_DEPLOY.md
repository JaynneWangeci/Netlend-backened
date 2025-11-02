# Vercel Deployment Guide

## Step 1: Login to Vercel
```bash
vercel login
```

## Step 2: Deploy
```bash
vercel --prod
```

## Step 3: Set Environment Variables (in Vercel Dashboard)
- `SECRET_KEY`: your-secret-key-here
- `DATABASE_URL`: your-database-connection-string

## Alternative: Deploy via Vercel Dashboard
1. Go to https://vercel.com
2. Import your GitHub repository
3. Vercel will auto-detect the configuration

Your API will be available at: https://your-project-name.vercel.app