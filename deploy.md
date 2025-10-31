# Render Deployment Guide for NetLend Backend

## Quick Deploy Steps:

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn 'app:create_app()'`
     - **Environment**: Python 3

3. **Add Environment Variables** in Render dashboard:
   ```
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   DATABASE_URL=postgresql://... (Render will provide this)
   SENDGRID_API_KEY=your-sendgrid-api-key
   MAIL_DEFAULT_SENDER=noreply@netlend.com
   CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
   CLOUDINARY_API_KEY=your-cloudinary-api-key
   CLOUDINARY_API_SECRET=your-cloudinary-api-secret
   ```

4. **Create PostgreSQL Database**:
   - In Render dashboard: "New +" → "PostgreSQL"
   - Copy the connection string to DATABASE_URL

## Alternative: One-Click Deploy
Use the render.yaml file for automatic setup by connecting your repo to Render.

Your app will be available at: `https://your-app-name.onrender.com`