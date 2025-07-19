# Railway Deployment Guide

## Quick Deploy

1. **Fork/Clone** this repository
2. **Connect** to Railway
3. **Deploy** - Railway will automatically detect the Python app

## Configuration

The app uses these files for Railway deployment:

- `railway.json` - Railway configuration
- `start.sh` - Startup script
- `wsgi.py` - Alternative WSGI entry point
- `requirements-railway.txt` - Railway-optimized dependencies
- `Procfile` - Heroku-style process definition

## Environment Variables

Railway automatically sets:
- `PORT` - The port to bind to (usually 8080)
- `RAILWAY_ENVIRONMENT` - Set to "production"

## Troubleshooting 502 Bad Gateway

### Common Causes:

1. **Missing Dependencies**: The app requires heavy ML libraries
2. **Memory Issues**: Face processing requires significant RAM
3. **Startup Timeout**: App takes time to load models
4. **Port Binding**: App must bind to `0.0.0.0:PORT`

### Debug Steps:

1. **Check Logs**: View Railway deployment logs
2. **Test Health Endpoint**: Visit `/health` after deployment
3. **Verify Dependencies**: Ensure all packages install correctly
4. **Check Memory**: Railway provides limited RAM

### Solutions:

1. **Use Railway-Specific Requirements**:
   ```bash
   # Use requirements-railway.txt instead of requirements.txt
   pip install -r requirements-railway.txt
   ```

2. **Increase Memory** (if available):
   - Railway Pro plans offer more RAM
   - Consider model optimization

3. **Use Headless OpenCV**:
   ```python
   # requirements-railway.txt uses opencv-python-headless
   ```

4. **CPU-Only PyTorch**:
   ```python
   # requirements-railway.txt uses torch+cpu
   ```

## Health Check Endpoints

- `GET /health` - Basic health check
- `GET /ready` - Railway-ready check
- `GET /ping` - Simple ping test

## Manual Deployment

If automatic deployment fails:

1. **SSH into Railway**:
   ```bash
   railway login
   railway shell
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements-railway.txt
   ```

3. **Test Locally**:
   ```bash
   python wsgi.py
   ```

4. **Check Logs**:
   ```bash
   railway logs
   ```

## Performance Optimization

1. **Use CPU-Only Models**: Reduces memory usage
2. **Lazy Loading**: Load models on first request
3. **Caching**: Cache processed results
4. **Image Compression**: Reduce input image sizes

## Monitoring

Monitor these metrics:
- Memory usage
- Response times
- Error rates
- Model loading times

## Support

If issues persist:
1. Check Railway status page
2. Review application logs
3. Test with minimal dependencies
4. Consider alternative deployment platforms 