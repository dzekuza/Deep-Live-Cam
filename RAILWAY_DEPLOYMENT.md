# Railway Deployment Guide for Deep-Live-Cam

This guide will help you deploy your Deep-Live-Cam face swap application to Railway, making it available online 24/7.

## Prerequisites

- GitHub account
- Railway account (free at [railway.app](https://railway.app))
- Your Deep-Live-Cam code pushed to a GitHub repository

## Step 1: Prepare Your Repository

Your repository should contain:
- ✅ `Dockerfile` (already configured)
- ✅ `railway.json` (deployment config)
- ✅ `.dockerignore` (optimizes build)
- ✅ `requirements-docker.txt` (fixed for deployment)
- ✅ `web_api.py` (Flask web API)

## Step 2: Deploy to Railway

### Option A: Deploy via Railway Dashboard

1. **Go to Railway Dashboard**
   - Visit [railway.app](https://railway.app)
   - Sign in with your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your Deep-Live-Cam repository

3. **Configure Deployment**
   - Railway will automatically detect the Dockerfile
   - The `railway.json` file will configure the deployment
   - No additional configuration needed

4. **Deploy**
   - Click "Deploy" to start the build process
   - Wait for the build to complete (5-10 minutes)

### Option B: Deploy via Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Deploy**
   ```bash
   railway up
   ```

## Step 3: Configure Environment Variables (Optional)

In Railway dashboard, you can set environment variables:

- `PORT=8000` (default, Railway sets this automatically)
- `FLASK_ENV=production`
- `FLASK_DEBUG=0`

## Step 4: Access Your Deployed App

Once deployed, Railway will provide:
- **Public URL**: `https://your-app-name.railway.app`
- **Custom Domain**: You can add your own domain in Railway settings

## Step 5: Monitor Your Deployment

### Railway Dashboard Features:
- **Logs**: View real-time application logs
- **Metrics**: Monitor CPU, memory usage
- **Deployments**: Track deployment history
- **Settings**: Configure environment variables

### Health Check:
Your app includes a health endpoint: `https://your-app-name.railway.app/health`

## Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check Railway logs for error messages
   - Ensure all files are committed to GitHub
   - Verify Dockerfile syntax

2. **App Won't Start**
   - Check if port 8000 is exposed in Dockerfile
   - Verify `web_api.py` starts correctly
   - Check environment variables

3. **Face Swap Not Working**
   - Ensure AI models downloaded correctly
   - Check if all dependencies installed
   - Verify GPU/CPU compatibility

### Performance Tips:

1. **Use Railway Pro** (if needed)
   - Better CPU/memory allocation
   - GPU instances available
   - Faster build times

2. **Optimize Docker Image**
   - Multi-stage builds
   - Layer caching
   - Smaller base images

## Cost Estimation

### Railway Free Tier:
- **$5 credit/month**
- **512MB RAM, 0.5 CPU**
- **Suitable for testing**

### Railway Pro:
- **Pay-as-you-go pricing**
- **Better performance**
- **GPU instances available**

## Security Considerations

1. **Environment Variables**
   - Never commit secrets to GitHub
   - Use Railway's environment variable feature

2. **CORS Configuration**
   - Your app allows all origins (`*`)
   - Consider restricting for production

3. **Rate Limiting**
   - Consider adding rate limiting for production use

## Next Steps

After successful deployment:

1. **Test the Web Interface**
   - Upload images
   - Test face swap functionality
   - Verify all features work

2. **Monitor Performance**
   - Check Railway metrics
   - Monitor response times
   - Watch for errors

3. **Scale if Needed**
   - Upgrade to Railway Pro for better performance
   - Add custom domain
   - Configure CDN

## Support

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: Report bugs in your repository

---

**Your Deep-Live-Cam app will be available at:**
`https://your-app-name.railway.app`

**Health check:**
`https://your-app-name.railway.app/health` 