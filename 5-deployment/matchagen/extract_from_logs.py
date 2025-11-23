"""Extract recipe data from log files and save as proper batch files."""

import json
import re
import sys

sys.path.insert(0, "src")  # noqa: E402

from matchagen.datatools import save_recipes_to_file  # noqa: E402


def extract_recipes_from_log(log_file: str) -> list[dict]:
    """Extract recipe JSON data from log file."""
    recipes = []

    with open(log_file) as f:
        content = f.read()

    # Find all JSON result lines
    pattern = r"JSON result: ({[^}]+(?:'[^']*'[^}]*)*})"
    matches = re.findall(pattern, content)

    for match in matches:
        try:
            # Clean up the match and parse JSON
            json_str = match.replace("'", '"')
            recipe = json.loads(json_str)

            # Only include recipes with title, ingredients, and instructions
            if (
                recipe.get("title")
                and recipe.get("ingredients")
                and recipe.get("instructions")
            ):
                recipes.append(recipe)
        except Exception:
            continue

    return recipes


if __name__ == "__main__":
    # Extract batch 1
    print("Extracting batch 1...")
    batch1_recipes = extract_recipes_from_log("batch1_rerun.txt")
    print(f"Found {len(batch1_recipes)} recipes in batch1_rerun.txt")

    # Extract batch 2
    print("\nExtracting batch 2...")
    batch2_recipes = extract_recipes_from_log("batch2_log.txt")
    print(f"Found {len(batch2_recipes)} recipes in batch2_log.txt")

    # Extract batch 3
    print("\nExtracting batch 3...")
    batch3_recipes = extract_recipes_from_log("batch3_log.txt")
    print(f"Found {len(batch3_recipes)} recipes in batch3_log.txt")

    # Combine all batches
    print("\n" + "=" * 60)
    print("Combining all batches...")
    all_recipes = batch1_recipes + batch2_recipes + batch3_recipes
    print(f"Total recipes: {len(all_recipes)}")

    if all_recipes:
        save_recipes_to_file(all_recipes, "assets/matcha_recipes_combined.txt")
        print("\n✓ Saved combined file to assets/matcha_recipes_combined.txt")
        print(f"  - Batch 1: {len(batch1_recipes)} recipes")
        print(f"  - Batch 2: {len(batch2_recipes)} recipes")
        print(f"  - Batch 3: {len(batch3_recipes)} recipes")
        print(f"  - Total: {len(all_recipes)} recipes")
    else:
        print("\n✗ No recipes extracted!")
