# 🍵 Matcha Recipe Generator

AI-powered matcha recipe generator using fine-tuned distilgpt2.

## Features

- Generate creative matcha recipes
- Control creativity with temperature slider (0.5-1.5)
- Add inspiration keywords (e.g., "mango", "ice cream")
- Clean, modern web interface
- Deployed on Hetzner Cloud

## Installation

### Prerequisites
- Python 3.11+
- UV package manager
- Docker (for deployment)

### Setup

1. Install dependencies:
```bash
uv sync --all-extras
```

2. Activate environment:
```bash
source .venv/bin/activate
```

## Training the Model

### Automatic (using Makefile):
```bash
make train
```

This will:
1. Scrape matcha recipes from websites
2. Save to `assets/matcha_recipes.txt`
3. Fine-tune distilgpt2 for 2 epochs
4. Save model to `artefacts/matcha-model/`

### Manual:
```bash
# Scrape data
python src/matchagen/datatools.py

# Train model
python src/matchagen/main.py
```

## Building the Package

Create a wheel distribution:
```bash
make wheel
# or
uv build --clean
```

Output: `dist/matchagen-0.1.0-py3-none-any.whl`

## Running Locally

### Option 1: Direct Python
```bash
cd backend
python app.py
```
Visit http://localhost:8000

### Option 2: Docker (Multi-Container)
```bash
make build
make run
```
Visit http://localhost

This runs two containers:
- **Frontend**: Nginx serving static files on port 80
- **Backend**: FastAPI API server on internal port 8000

The nginx reverse proxy forwards API requests to the backend.

## Deployment to Hetzner

### 1. Create Hetzner Cloud Server

1. Sign up at https://www.hetzner.com/cloud
2. Create new project
3. Launch server (CX11: €4.15/month)
4. Choose Ubuntu 22.04
5. Add your SSH key

### 2. Server Setup

SSH into server:
```bash
ssh root@YOUR_HETZNER_IP
```

Install Docker:
```bash
apt update
apt install -y docker.io docker-compose git
systemctl enable docker
systemctl start docker
```

### 3. Deploy Application

On your local machine:
```bash
# Build wheel and images
make build

# Save and transfer images
docker save matchagen-backend:latest matchagen-frontend:latest | gzip > matchagen.tar.gz
scp matchagen.tar.gz docker-compose.yml root@YOUR_HETZNER_IP:/app/
```

On Hetzner server:
```bash
mkdir -p /app
cd /app
docker load < matchagen.tar.gz
docker compose up -d
```

### 4. Configure Firewall

In Hetzner Cloud Console:
- Go to Firewalls
- Add rule: TCP, Port 80, Source: 0.0.0.0/0

### 5. Access Application

Visit: `http://YOUR_HETZNER_IP`

## Usage

1. Open web interface
2. Adjust temperature slider (higher = more creative)
3. Optionally add inspiration keyword
4. Click "Generate Recipe"
5. Enjoy your AI-generated matcha recipe!

## Project Structure

```
matchagen/
├── src/matchagen/        # Core package
│   ├── datatools.py      # Recipe scraping
│   ├── models.py         # GPT-2 fine-tuning
│   └── main.py           # Training pipeline
├── backend/              # FastAPI API service
│   ├── Dockerfile        # Backend container image
│   ├── app.py            # API endpoints
│   └── utils.py          # Helper functions
├── frontend/             # Nginx frontend service
│   ├── Dockerfile        # Frontend container image
│   ├── nginx.conf        # Nginx configuration
│   └── static/           # HTML/CSS/JS files
├── assets/               # Training data
├── artefacts/            # Trained models
├── docker-compose.yml    # Multi-container orchestration
└── Makefile              # Build automation
```

## Development

Run tests:
```bash
make test
```

Clean all generated files:
```bash
make clean
```

Full rebuild from scratch:
```bash
make all
```

## Technologies

- **Model:** distilgpt2 (HuggingFace)
- **Backend:** FastAPI + Uvicorn
- **Frontend:** Vanilla HTML/CSS/JS
- **Package Manager:** UV
- **Containerization:** Docker + Docker Compose
- **Deployment:** Hetzner Cloud

## Troubleshooting

### Model not generating coherent recipes
- Increase training epochs to 3-4
- Add more recipe data (target 100+ recipes)
- Adjust learning rate (try 3e-5)

### Docker image too large
- Use CPU-only PyTorch (already configured)
- Remove unnecessary dependencies

### Generation too slow
- Reduce max_length to 200
- Use batch size 1 for inference

### Port 80 blocked
- Check Hetzner firewall settings
- Verify docker-compose port mapping

## License

MIT
