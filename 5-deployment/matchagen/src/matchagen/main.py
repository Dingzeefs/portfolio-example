"""Setup script to download, fine-tune, and cache the Chef Transformer model."""

import re
from pathlib import Path
from typing import List, Dict

import tomli
import torch
from datasets import Dataset
from loguru import logger
from matchagen import custom_logger  # noqa: F401
from matchagen.models import RecipeGenerator
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)


def load_recipes(file_path: Path) -> List[Dict[str, str]]:
    """Load and parse recipes from text file."""
    with file_path.open("r") as f:
        content = f.read()

    # Split by ---
    raw_recipes = content.split("---")
    parsed_recipes = []

    for raw in raw_recipes:
        if not raw.strip():
            continue

        try:
            lines = raw.strip().split("\n")
            title = lines[0].strip()
            
            ingredients = []
            directions = []
            current_section = None

            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                
                if "Ingredients:" in line:
                    current_section = "ingredients"
                    continue
                elif "Instructions:" in line:
                    current_section = "directions"
                    continue
                
                if current_section == "ingredients":
                    # Remove bullet points
                    ing = line.lstrip("-").strip()
                    if ing:
                        ingredients.append(ing)
                elif current_section == "directions":
                    # Remove numbers (1. Step -> Step)
                    direction = re.sub(r"^\d+\.\s*", "", line).strip()
                    if direction:
                        directions.append(direction)

            if title and ingredients and directions:
                parsed_recipes.append({
                    "title": title,
                    "ingredients": ingredients,
                    "directions": directions
                })
        except Exception as e:
            logger.warning(f"Failed to parse recipe: {e}")

    return parsed_recipes


def format_for_t5(recipes: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Format recipes for T5 training."""
    formatted = []
    for r in recipes:
        # Input: items: ing1, ing2
        input_text = "items: " + ", ".join(r["ingredients"])
        
        # Target: title: T <section> ingredients: I <sep> I <section> directions: D <sep> D
        # Based on Chef Transformer format
        target_text = f"title: {r['title']} <section> "
        target_text += "ingredients: " + " <sep> ".join(r["ingredients"]) + " <section> "
        target_text += "directions: " + " <sep> ".join(r["directions"])
        
        formatted.append({"input_text": input_text, "target_text": target_text})
    
    return formatted


def main():
    """Download and fine-tune the T5 model."""
    # Load configuration
    config_file = Path("matchagen.toml")
    if not config_file.exists():
        artefacts_dir = Path("artefacts")
        assets_dir = Path("assets")
    else:
        with config_file.open("rb") as f:
            config = tomli.load(f)
        artefacts_dir = Path(config.get("data", {}).get("artefacts_dir", "artefacts"))
        assets_dir = Path(config.get("data", {}).get("assets_dir", "assets"))

    model_name = "flax-community/t5-recipe-generation"
    output_dir = artefacts_dir / "matcha-model"
    recipe_file = assets_dir / "matcha_recipes_combined_cleaned.txt"

    logger.info(f"Loading model {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    # FREEZE ENCODER (Strategy B: Few-Shot Fine-Tuning)
    logger.info("Freezing encoder layers...")
    for param in model.encoder.parameters():
        param.requires_grad = False
        
    # Prepare Data
    if recipe_file.exists():
        logger.info(f"Loading recipes from {recipe_file}...")
        recipes = load_recipes(recipe_file)
        logger.info(f"Parsed {len(recipes)} recipes.")
        
        data = format_for_t5(recipes)
        dataset = Dataset.from_list(data)
        
        # Tokenize
        def preprocess_function(examples):
            inputs = examples["input_text"]
            targets = examples["target_text"]
            
            model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding="max_length")
            labels = tokenizer(targets, max_length=512, truncation=True, padding="max_length")
            
            model_inputs["labels"] = labels["input_ids"]
            return model_inputs

        tokenized_dataset = dataset.map(preprocess_function, batched=True)
        
        # Training Config
        training_args = Seq2SeqTrainingArguments(
            output_dir=str(output_dir),
            eval_strategy="no",
            learning_rate=2e-4, # Slightly higher LR for head tuning
            per_device_train_batch_size=4,
            weight_decay=0.01,
            save_total_limit=1,
            num_train_epochs=5, # Few epochs for few-shot
            predict_with_generate=True,
            logging_steps=10,
            push_to_hub=False,
        )
        
        trainer = Seq2SeqTrainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            tokenizer=tokenizer,
            data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
        )
        
        logger.info("Starting few-shot fine-tuning...")
        trainer.train()
        logger.info("Fine-tuning complete!")
        
    else:
        logger.warning(f"Recipe file {recipe_file} not found. Skipping fine-tuning.")

    # Save Model
    logger.info(f"Saving model to {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # Verify
    logger.info("Verifying model loads correctly...")
    generator = RecipeGenerator(str(output_dir))
    
    # Test generation
    logger.info("Running test generation with inputs: 'milk, sugar'")
    test_recipe = generator.generate("milk, sugar")
    logger.info("Test generation result:")
    logger.info("\n" + test_recipe)
    
    logger.info("Setup complete!")


if __name__ == "__main__":
    main()
