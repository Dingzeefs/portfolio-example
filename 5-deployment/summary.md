# Summary week 5

View the deployed project here: [http://46.224.49.75:8080/](http://46.224.49.75:8080/)

---

### Docker Architecture

**Multi-stage Frontend Build:**
1. **Stage 1 (Builder)**: Node.js Alpine – runs `npm install` and builds static files via Vite
2. **Stage 2 (Runtime)**: Nginx Alpine – serves the static files generated in Stage 1

**Backend Build:**
- Base image: Python 3.12 Slim
- Dependencies: PyTorch, Transformers, FastAPI, Uvicorn
- Model artifacts are loaded dynamically at container startup

---

## Model Training & Fine-tuning

### The Dataset: Matcha Recipes

I curated a dataset of matcha recipes by collecting both traditional and modern sources, formatting each entry as follows:

```
Title: [Recipe Name]
Ingredients:
- [Ingredient 1]
- [Ingredient 2]
...
Directions:
1. [Step 1]
2. [Step 2]
...
```

**Dataset Statistics:**
- Source file: `assets/matcha_recipes_combined.txt`
- Format: Plain text, structured by title/ingredients/directions
- Preprocessing: Cleaned and normalized for consistency

---

### Model Selection: T5 (Text-to-Text Transfer Transformer)

T5 was selected for its:
1. **Versatile Architecture**: Uniform text-to-text interface for all NLP tasks
2. **Strong Pretraining**: Leveraging the C4 corpus
3. **Efficient Fine-tuning**: Exceptional transfer learning
4. **Controllable Generation**: Supports tuning for creativity and temperature

---

### Fine-tuning Strategy: Layer Freezing

To prevent overfitting on a small dataset and speed up training, I froze the encoder and trained only the decoder:

```python
# Freeze encoder layers
for param in model.encoder.parameters():
    param.requires_grad = False

# Fine-tune decoder
for param in model.decoder.parameters():
    param.requires_grad = True
```

**Why?**
- **Encoder Frozen:** Keeps broad language understanding intact
- **Decoder Trainable:** Learns domain-specific recipe patterns
- **Result:** Faster, more robust fine-tuning with fewer resources

---

### Training Configuration

```python
training_args = {
    "num_train_epochs": 10,
    "learning_rate": 5e-5,
    "per_device_train_batch_size": 8,
    "warmup_steps": 500,
    "weight_decay": 0.01,
    "logging_steps": 10,
    "save_steps": 140,
}
```

---

### Model Artifacts

- `model.safetensors` (850 MB): Model weights
- `config.json`: Model configuration
- `tokenizer.json` (2.3 MB): Tokenizer vocab
- `generation_config.json`: Text generation parameters
- `checkpoint-140/`: Last training checkpoint with optimizer state

---

[Go back to Homepage](../README.md)

