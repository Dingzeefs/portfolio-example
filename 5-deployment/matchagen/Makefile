.PHONY: install scrape train wheel build run stop deploy clean test all

# Install dependencies
install:
	uv sync --all-extras

# Scrape matcha recipes
scrape:
	@if [ ! -f assets/matcha_recipes_combined_cleaned.txt ]; then \
		echo "Scraping matcha recipes..."; \
		.venv/bin/python -m matchagen.datatools; \
	else \
		echo "✓ Recipes already exist: assets/matcha_recipes_combined_cleaned.txt"; \
	fi

# Train the model
train: scrape
	@if [ ! -d artefacts/matcha-model ]; then \
		echo "Training T5 Chef Transformer (flax-community/t5-recipe-generation)..."; \
		.venv/bin/python src/matchagen/main.py; \
	else \
		echo "Model already trained in artefacts/"; \
	fi

# Build wheel package
wheel: train
	@if [ ! -f dist/matchagen-*.whl ]; then \
		echo "Building wheel..."; \
		uv build; \
	else \
		echo "Wheel already exists in dist/"; \
	fi

# Build Docker images (frontend + backend)
build: wheel
	docker compose build

# Run Docker containers locally
run: build
	docker compose up -d
	@echo "Matcha Recipe Generator running at http://localhost"

# Stop and remove containers
stop:
	docker compose down

# Deploy to Hetzner
deploy: build
	@echo "Deployment instructions:"
	@echo "1. Save images:"
	@echo "   docker save matchagen-backend:latest matchagen-frontend:latest | gzip > matchagen.tar.gz"
	@echo "2. Copy files:"
	@echo "   scp matchagen.tar.gz docker-compose.yml root@YOUR_IP:/app/"
	@echo "3. On server, load images:"
	@echo "   docker load < /app/matchagen.tar.gz"
	@echo "4. Run containers:"
	@echo "   cd /app && docker compose up -d"

# Test generation locally
test: install
	@.venv/bin/python -c "from matchagen import RecipeGenerator; \
		g = RecipeGenerator('artefacts/matcha-model'); \
		print(g.generate('mango'))"

# Clean generated files
clean:
	rm -rf dist/ artefacts/ assets/*.txt __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Full pipeline from scratch
all: clean install train wheel build
