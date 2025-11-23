# Plan: Integrate Chef Transformer T5 into Matchagen

I am replacing the current GPT-2 based model with the T5-based Chef Transformer to improve recipe generation quality and enforce "Matcha" ingredients.

## Status Update
-   [x] **Dependencies**: Added `sentencepiece>=0.1.99`.
-   [x] **Model Logic**: Implemented `src/matchagen/models.py` with T5 and **Strategy A** (Code Injection).
-   [x] **Setup Script**: Updated `src/matchagen/main.py` to handle download and training.
-   [x] **Backend**: Updated `backend/app.py` to handle ingredient lists.
-   [ ] **Fine-Tuning**: Currently failing. `Parsed 0 recipes` error in `src/matchagen/main.py`. Need to fix the parser to handle the `matcha_recipes_combined_cleaned.txt` format.
-   [ ] **Verification**: Need to successfully run `make train` (fine-tuning) and `make test`.

## Next Steps

### 1. Fix Data Parsing (Critical)
-   **Problem**: The training script reported `Parsed 0 recipes` when reading `assets/matcha_recipes_combined_cleaned.txt`.
-   **Action**: Inspect the format of `assets/matcha_recipes_combined_cleaned.txt` (it seems to be one huge line or has a different separator than `---`).
-   **Fix**: Update `load_recipes` in `src/matchagen/main.py` to correctly parse the cleaned data file.

### 2. Fix Training Loop
-   **Problem**: `ValueError: No columns in the dataset match the model's forward method signature`.
-   **Action**: Ensure the dataset columns (`input_ids`, `attention_mask`, `labels`) are correctly passed to the model.
-   **Fix**: The `preprocess_function` returns `model_inputs`, but `Dataset.map` might be dropping columns if not explicitly told to keep them or if `remove_unused_columns` defaults to `True`. We need to ensure `input_ids` and `labels` are preserved.

### 3. Verification
-   Run `make train` to verify the parsing fix and training loop.
-   Run `make test` to see the T5 model in action.
