# Hetzner Cloud Deployment Guide - Matchagen

Complete guide for deploying the Matchagen (AI Matcha Recipe Generator) application to Hetzner Cloud.

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Hetzner Cloud Console Setup](#2-hetzner-cloud-console-setup)
3. [Server Initial Configuration](#3-server-initial-configuration)
4. [Building the Application Locally](#4-building-the-application-locally)
5. [Deploying to Hetzner Cloud](#5-deploying-to-hetzner-cloud)
6. [Accessing the Application](#6-accessing-the-application)

---

## 1. Prerequisites

### Required Accounts
- ✅ **Hetzner Cloud account** - Sign up at https://www.hetzner.com/

### Required Tools (Local Machine)
- ✅ **SSH client**
- ✅ **Docker**
- ✅ **rsync** - For transferring files

---

## 2. Hetzner Cloud Console Setup

### Step 1: Create a New Project
1. Log in to Hetzner Cloud Console.
2. Click **"New Project"**.
3. Name it: `matchagen-deployment`.

### Step 2: Create a Cloud Server
1. Click **"Add Server"**.
2. **Location**: Choose closest to you.
3. **Image**: Ubuntu 22.04 LTS.
4. **Type**: **CPX21** (3 vCPU, 4GB RAM) is recommended due to the ML model.
   - *Note: CPX11 (2GB RAM) might struggle with the T5 model loading.*
5. **SSH Keys**: Add your public SSH key (`cat ~/.ssh/id_ed25519.pub`).
6. **Name**: `matchagen-server`.
7. Click **"Create & Buy Now"**.

### Step 3: Note Your Server IP
Copy the IPv4 address: `xxx.xxx.xxx.xxx`.

---

## 3. Server Initial Configuration

Connect to your server:
```bash
ssh root@xxx.xxx.xxx.xxx
```

Run the following commands on the server to set up Docker:

```bash
# 1. Update system
apt update && apt upgrade -y

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Install Docker Compose Plugin
apt install docker-compose-plugin -y

# 4. Create application directory
mkdir -p /opt/matchagen
```

---

## 4. Building the Application Locally

Before deploying, ensure your project is ready locally.

```bash
# Navigate to project directory
cd /Users/DINGZEEFS/MADS-deployment/2-frontend/matchagen

# 1. Train the model (if not already done)
make train

# 2. Build the python package (wheel)
make wheel
```

Ensure you have the following key files/folders:
- `artefacts/matcha-model/` (The trained T5 model)
- `dist/` (The python wheel)
- `docker-compose.yml`
- `backend/` and `frontend/` directories

---

## 5. Deploying to Hetzner Cloud

### Method: Transfer Files and Build on Server

We will use `rsync` to copy the project files to the server, then build the containers there.

#### Step 1: Transfer Files
Run this from your **local machine** (inside `2-frontend/matchagen/`):

```bash
# Replace xxx.xxx.xxx.xxx with your server IP
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' \
  --exclude='node_modules' --exclude='.DS_Store' \
  ./ root@xxx.xxx.xxx.xxx:/opt/matchagen/
```

#### Step 2: Build and Run on Server
SSH into your server and start the application:

```bash
ssh root@xxx.xxx.xxx.xxx
```

Then on the server:

```bash
cd /opt/matchagen

# Build and start containers
docker compose up -d --build
```

#### Step 3: Check Status
```bash
docker compose ps
```
You should see `matchagen-backend` and `matchagen-frontend` running.

---

## 6. Accessing the Application

### Default Access
The `docker-compose.yml` maps the frontend to port `8080`.

Access your application at:
**http://xxx.xxx.xxx.xxx:8080**

### Optional: Running on Port 80
If you want to access it without the port number (http://xxx.xxx.xxx.xxx), modify `docker-compose.yml` on the server:

1. Edit the file:
   ```bash
   nano docker-compose.yml
   ```
2. Change ports for `frontend`:
   ```yaml
   ports:
     - "80:80"  # Changed from 8080:80
   ```
3. Restart:
   ```bash
   docker compose down
   docker compose up -d
   ```

### Troubleshooting
- **Logs**: `docker compose logs -f`
- **Model not found**: Ensure `artefacts/` folder was transferred correctly.
- **Frontend error**: Check if backend is healthy `curl http://localhost:8000/health` (inside server).
