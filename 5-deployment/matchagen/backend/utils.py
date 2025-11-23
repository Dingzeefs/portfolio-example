"""Utility functions for backend processing."""


def parse_recipe_text(text: str) -> dict:
    """Parse generated recipe text into structured components.

    Args:
        text: Raw generated recipe text

    Returns:
        Dictionary with title, ingredients, and instructions
    """
    lines = [line.strip() for line in text.split("\\n") if line.strip()]

    if not lines:
        return {
            "title": "Matcha Recipe",
            "ingredients": [],
            "instructions": [],
        }

    title = lines[0] if lines else "Matcha Recipe"
    ingredients = []
    instructions = []

    in_ingredients = False
    in_instructions = False

    for line in lines[1:]:
        lower_line = line.lower()

        # Check for section headers
        if "ingredient" in lower_line:
            in_ingredients = True
            in_instructions = False
            continue
        if "instruction" in lower_line or "step" in lower_line:
            in_instructions = True
            in_ingredients = False
            continue

        # Parse ingredients
        if in_ingredients and line.startswith("-"):
            ingredients.append(line[1:].strip())

        # Parse instructions
        elif in_instructions and (line[0].isdigit() or line.startswith("-")):
            # Remove numbering if present
            instruction = line.lstrip("0123456789.-) ").strip()
            if instruction:
                instructions.append(instruction)

    return {
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
    }


def format_recipe_html(recipe_dict: dict) -> str:
    """Format parsed recipe as HTML.

    Args:
        recipe_dict: Dictionary from parse_recipe_text

    Returns:
        HTML formatted recipe
    """
    html = f"<h3>{recipe_dict['title']}</h3>"

    if recipe_dict["ingredients"]:
        html += "<h4>Ingredients:</h4><ul>"
        for ingredient in recipe_dict["ingredients"]:
            html += f"<li>{ingredient}</li>"
        html += "</ul>"

    if recipe_dict["instructions"]:
        html += "<h4>Instructions:</h4><ol>"
        for instruction in recipe_dict["instructions"]:
            html += f"<li>{instruction}</li>"
        html += "</ol>"

    return html
