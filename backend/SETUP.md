# Lore Emotion - Backend Setup Guide

## Prerequisites

- Python 3.10+
- Conda (Anaconda or Miniconda) - **Optional but recommended**
- Docker Desktop (for containerized PostgreSQL and Redis) - **Recommended**
  - OR PostgreSQL 14+ (if not using Docker)
  - OR Redis 6+ (if not using Docker)
- AWS Account (for Cognito)

## Installation

### 0. Install Conda (Optional - Skip if using venv)

If you don't have conda installed, you have two options:

**Option A: Install Miniconda (Lightweight)**
1. Download from: https://docs.conda.io/en/latest/miniconda.html
2. Run the installer and follow the prompts
3. **Important**: Check "Add Miniconda to PATH" during installation, OR
4. After installation, restart PowerShell or run:
   ```powershell
   # Add conda to PATH for current session
   $env:Path += ";$env:USERPROFILE\miniconda3\Scripts;$env:USERPROFILE\miniconda3"
   ```

**Option B: Install Anaconda (Full Package)**
1. Download from: https://www.anaconda.com/download
2. Run the installer and follow the prompts
3. Restart PowerShell after installation

**Verify conda installation:**
```powershell
conda --version
```

### 1. Create Environment

**Option A: Using Conda (Recommended)**
```powershell
cd backend

# Create new conda environment with Python 3.10
conda create -n lore-emotion python=3.10 -y

# Activate the environment
conda activate lore-emotion
```

**Option B: Using venv (if conda is not available)**
```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate the environment
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
# If using conda - make sure environment is activated
conda activate lore-emotion

# If using venv - make sure it's activated (you should see (venv) in prompt)
# .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**Troubleshooting conda activation:**
- If `conda activate` doesn't work, try: `conda init powershell` then restart PowerShell
- Or use: `conda env create -f environment.yml` to create environment from the YAML file

### 3. Configure Environment

Copy the example environment file and update with your values:

```powershell
copy .env.example .env
```

Update `.env` with your configuration:
- Database URLs (PostgreSQL)
- AWS credentials and Cognito settings
- Redis URL
- Encryption keys (generate secure keys!)
- API settings

### 4. Generate Encryption Key

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Use this as your `ENCRYPTION_KEY` in `.env`

### 5. Setup PostgreSQL Database

You have two options: use Docker (recommended for local development) or install PostgreSQL directly.

#### Option A: Using Docker (Recommended)

**Prerequisites**: Install Docker Desktop from https://www.docker.com/products/docker-desktop/

**1. Run PostgreSQL Container:**
```powershell
# Pull and run PostgreSQL 14 container
docker run --name lore-emotion-postgres `
  -e POSTGRES_USER=lore_user `
  -e POSTGRES_PASSWORD=lore_password `
  -e POSTGRES_DB=postgres `
  -p 5432:5432 `
  -v lore-postgres-data:/var/lib/postgresql/data `
  -d postgres:14
```

**2. Verify PostgreSQL is running:**
```powershell
docker ps
# You should see lore-emotion-postgres container running
```

**3. Create the databases:**
```powershell
# Connect to PostgreSQL container
docker exec -it lore-emotion-postgres psql -U lore_user -d postgres

# In the PostgreSQL prompt, create databases:
CREATE DATABASE lore_emotion;
CREATE DATABASE lore_emotion_identity;

# List databases to verify
\l

# Exit PostgreSQL prompt
\q
```

**4. Update your `.env` file with Docker database URLs:**
```env
DATABASE_URL=postgresql://lore_user:lore_password@localhost:5432/lore_emotion
DATABASE_IDENTITY_URL=postgresql://lore_user:lore_password@localhost:5432/lore_emotion_identity
```

**Useful Docker Commands:**
```powershell
# Stop the container
docker stop lore-emotion-postgres

# Start the container
docker start lore-emotion-postgres

# Remove the container (data persists in volume)
docker rm lore-emotion-postgres

# View logs
docker logs lore-emotion-postgres

# Remove volume (deletes all data!)
docker volume rm lore-postgres-data
```

#### Option B: Local PostgreSQL Installation

**1. Download and Install PostgreSQL 14+:**
   - Windows: https://www.postgresql.org/download/windows/
   - Run the installer and remember your postgres password

**2. Create databases using pgAdmin or command line:**
```powershell
# Using psql command line
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE lore_emotion;
CREATE DATABASE lore_emotion_identity;
\q
```

**3. Update your `.env` file:**
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/lore_emotion
DATABASE_IDENTITY_URL=postgresql://postgres:your_password@localhost:5432/lore_emotion_identity
```

### 6. Setup Redis Cache

You have three options: Docker (recommended for local development), AWS ElastiCache (recommended for production), or local installation.

#### Option A: Using Docker (Recommended for Local Development)

```powershell
# Run Redis container
docker run --name lore-emotion-redis `
  -p 6379:6379 `
  -d redis:6-alpine

# Verify Redis is running
docker ps

# Test Redis connection
docker exec -it lore-emotion-redis redis-cli ping
# Should return: PONG
```

**Update `.env` file:**
```env
REDIS_URL=redis://localhost:6379/0
REDIS_SSL=false
```

**Useful Docker Commands:**
```powershell
# Stop Redis
docker stop lore-emotion-redis

# Start Redis
docker start lore-emotion-redis

# View logs
docker logs lore-emotion-redis

# Remove container
docker rm lore-emotion-redis
```

#### Option B: AWS ElastiCache (Recommended for Production)

**1. Create ElastiCache Redis Cluster:**

```powershell
# Using AWS CLI
aws elasticache create-cache-cluster `
  --cache-cluster-id lore-emotion-cache `
  --engine redis `
  --cache-node-type cache.t3.micro `
  --num-cache-nodes 1 `
  --engine-version 7.0 `
  --preferred-availability-zone us-east-2a `
  --security-group-ids sg-xxxxx `
  --cache-subnet-group-name your-subnet-group `
  --tags Key=Project,Value=LoreEmotion Key=Environment,Value=Production
```

**Or using AWS Console:**
1. Go to AWS Console → ElastiCache
2. Click **Create** → **Redis cluster**
3. Configure:
   - **Cluster name**: `lore-emotion-cache`
   - **Engine version**: Redis 7.0 or later
   - **Node type**: `cache.t3.micro` (development) or `cache.r6g.large` (production)
   - **Number of replicas**: 2 (for high availability)
   - **Multi-AZ**: Enabled (recommended for production)
   - **Encryption in-transit**: Enabled (recommended)
   - **Encryption at-rest**: Enabled (recommended)
4. **Networking**:
   - Select your VPC
   - Choose subnet group
   - Select security group (allow inbound on port 6379 from your backend)
5. **Backup**: Enable automatic backups
6. Click **Create**

**2. Configure Security Group:**

Your ElastiCache cluster must be accessible from your backend servers:

```powershell
# Add inbound rule to ElastiCache security group
aws ec2 authorize-security-group-ingress `
  --group-id sg-elasticache-xxxxx `
  --protocol tcp `
  --port 6379 `
  --source-group sg-backend-xxxxx
```

**3. Get Connection Endpoint:**

```powershell
# Get cluster endpoint
aws elasticache describe-cache-clusters `
  --cache-cluster-id lore-emotion-cache `
  --show-cache-node-info `
  --query 'CacheClusters[0].CacheNodes[0].Endpoint' `
  --output table
```

Endpoint format: `lore-emotion-cache.xxxxx.0001.use2.cache.amazonaws.com`

**4. Update `.env` file:**

```env
# Without TLS (not recommended for production)
REDIS_URL=redis://lore-emotion-cache.xxxxx.0001.use2.cache.amazonaws.com:6379/0
REDIS_SSL=false

# With TLS (recommended for production)
REDIS_URL=rediss://lore-emotion-cache.xxxxx.0001.use2.cache.amazonaws.com:6379/0
REDIS_SSL=true
```

**5. Test Connection:**

```powershell
# From your backend server (must be in same VPC)
telnet lore-emotion-cache.xxxxx.0001.use2.cache.amazonaws.com 6379

# Or use redis-cli
redis-cli -h lore-emotion-cache.xxxxx.0001.use2.cache.amazonaws.com -p 6379 ping
# Should return: PONG

# With TLS
redis-cli -h lore-emotion-cache.xxxxx.0001.use2.cache.amazonaws.com -p 6379 --tls ping
```

**6. Monitor ElastiCache:**

```powershell
# View cluster metrics
aws elasticache describe-cache-clusters `
  --cache-cluster-id lore-emotion-cache `
  --show-cache-node-info

# View CloudWatch metrics
aws cloudwatch get-metric-statistics `
  --namespace AWS/ElastiCache `
  --metric-name CPUUtilization `
  --dimensions Name=CacheClusterId,Value=lore-emotion-cache `
  --start-time 2025-11-23T00:00:00Z `
  --end-time 2025-11-23T23:59:59Z `
  --period 3600 `
  --statistics Average
```

**ElastiCache Best Practices:**
- Enable **automatic failover** with Multi-AZ for high availability
- Use **encryption in-transit** (TLS) for production
- Enable **encryption at-rest** for sensitive data
- Set up **CloudWatch alarms** for CPU, memory, and evictions
- Use **Redis AUTH** token for additional security
- Enable **automatic backups** with appropriate retention period
- Use **parameter groups** to customize Redis configuration
- Monitor **cache hit ratio** and optimize accordingly

**Cost Optimization:**
- Use **Reserved Nodes** for predictable workloads (up to 55% savings)
- Start with smaller node types (`cache.t3.micro`) and scale as needed
- Use **single node** for development, **multi-node with replicas** for production
- Enable **Auto Discovery** for cluster mode to reduce connection overhead

#### Option C: Local Redis Installation

**Windows:**
1. Download Redis from: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`
3. Update `.env`:
   ```env
   REDIS_URL=redis://localhost:6379/0
   REDIS_SSL=false
   ```

### 7. Run Migrations

```powershell
# Make sure your environment is activated and databases are running
# Initialize database tables
python -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"
```

### 8. Setup AWS Cognito

1. Go to AWS Console → Cognito
2. Create a User Pool with these settings:
   - Email sign-in
   - Password policy: Strong (12+ chars, mixed case, numbers, symbols)
   - MFA: Optional
   - Email verification required
   - Add custom attribute: `anonymous_id` (String, Developer only)

3. Create an App Client:
   - Enable USER_PASSWORD_AUTH flow
   - No client secret
   - Copy User Pool ID and Client ID to `.env`

### 9. Run the Application

```powershell
# Make sure your environment is activated
# For conda:
conda activate lore-emotion

# For venv:
# .\venv\Scripts\Activate.ps1

# Development mode
python app/main.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/api/docs`

## Running Tests

```powershell
# Activate your environment first
# For conda:
conda activate lore-emotion

# For venv:
# .\venv\Scripts\Activate.ps1

# Run tests with coverage
pytest tests/ -v --cov=app
```

## Managing Environments

### If Using Conda

#### List all environments
```powershell
conda env list
```

#### Deactivate environment
```powershell
conda deactivate
```

#### Remove environment (if needed)
```powershell
conda env remove -n lore-emotion
```

#### Export environment (for sharing)
```powershell
conda env export > environment.yml
```

#### Create from environment file
```powershell
conda env create -f environment.yml
```

#### Initialize conda in PowerShell (if commands don't work)
```powershell
conda init powershell
# Then restart PowerShell
```

### If Using venv

#### Deactivate environment
```powershell
deactivate
```

#### Remove environment
```powershell
# Simply delete the venv folder
Remove-Item -Recurse -Force .\venv
```

## Docker Compose (All Services)

For convenience, you can run PostgreSQL, Redis, and the backend together using Docker Compose.

**Create `docker-compose.yml` in the backend directory:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    container_name: lore-emotion-postgres
    environment:
      POSTGRES_USER: lore_user
      POSTGRES_PASSWORD: lore_password
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lore_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6-alpine
    container_name: lore-emotion-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres-data:
```

**Usage:**
```powershell
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (deletes data!)
docker-compose down -v
```

**After starting services, create databases:**
```powershell
docker exec -it lore-emotion-postgres psql -U lore_user -d postgres -c "CREATE DATABASE lore_emotion;"
docker exec -it lore-emotion-postgres psql -U lore_user -d postgres -c "CREATE DATABASE lore_emotion_identity;"
```

## Docker Deployment (Backend Application)

```powershell
docker build -t lore-emotion-backend .
docker run -p 8000:8000 --env-file .env lore-emotion-backend
```

**Note**: If using conda in Docker, you can create a multi-stage build with conda or use the miniconda base image.

## Production Considerations

1. **Security**:
   - Use strong encryption keys
   - Enable HTTPS only
   - Configure CORS properly
   - Enable rate limiting
   - Set up AWS WAF

2. **Monitoring**:
   - Configure Sentry DSN
   - Set up CloudWatch logs
   - Enable Prometheus metrics
   - Monitor Redis and PostgreSQL

3. **Scaling**:
   - Use managed PostgreSQL (RDS)
   - Use ElastiCache for Redis (see Option B in section 6)
   - Deploy behind load balancer (ALB/NLB)
   - Enable auto-scaling for EC2/ECS

4. **Database**:
   - Enable connection pooling
   - Set up read replicas
   - Regular backups
   - Implement data retention policies

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/confirm` - Confirm email
- `POST /api/v1/auth/signin` - Sign in
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/forgot-password` - Initiate password reset
- `POST /api/v1/auth/reset-password` - Complete password reset

### Posts
- `POST /api/v1/posts/` - Create anonymous post
- `GET /api/v1/posts/` - List posts
- `GET /api/v1/posts/{id}` - Get specific post
- `GET /api/v1/posts/similar/{id}` - Find similar posts

### Responses
- `POST /api/v1/responses/` - Create response
- `GET /api/v1/responses/{post_id}` - Get responses
- `POST /api/v1/responses/{id}/helpful` - Mark helpful

### User
- `GET /api/v1/user/profile` - Get profile
- `GET /api/v1/user/privacy-settings` - Get privacy settings
- `PUT /api/v1/user/privacy-settings` - Update settings
- `GET /api/v1/user/my-posts` - Get user's posts
- `DELETE /api/v1/user/account` - Delete account
- `POST /api/v1/user/data-export` - Request data export

### Health & Metrics
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
