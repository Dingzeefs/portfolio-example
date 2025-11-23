"""Model generation using Chef Transformer (T5)."""

import re
import string  # Ensure this is imported!
from typing import List, Union

import torch
from loguru import logger
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class RecipeGenerator:
    """Recipe generator using Chef Transformer (T5)."""

    def __init__(self, model_path: str):
        """Initialize generator with T5 model.

        Args:
            model_path: Path to saved model directory or HuggingFace model ID
        """
        logger.info("=" * 60)
        logger.info("!!! CACHE BUSTER: VERSION 2025-LATTE-ENFORCER-V1 !!!")
        logger.info("!!! IF YOU DONT SEE THIS, THE CODE IS OLD !!!")
        logger.info("=" * 60)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading model from {model_path} on {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(self.device)
        self.model.eval()

    def generate(
        self,
        prompt: Union[str, List[str]],
        temperature: float = 0.9,
        max_length: int = 256,
    ) -> str:
        """Generate a recipe using the T5 model with safety checks.

        Args:
            prompt: Ingredients string (comma-separated) or list of ingredients
            temperature: Sampling temperature
            max_length: Maximum tokens to generate

        Returns:
            Formatted recipe text
        """
        # 1. Parse and Clean Input
        if isinstance(prompt, str):
            raw_ingredients = [
                i.strip().lower() for i in prompt.split(",") if i.strip()
            ]
        else:
            raw_ingredients = [i.lower() for i in prompt]

        # 2. Safety Filter (Prevent "Garlic Lattes")
        forbidden = [
            "chicken",
            "onion",
            "garlic",
            "beef",
            "pork",
            "fish",
            "oil",
            "salt",
            "pepper",
            "soup",
            "broth",
        ]

        clean_ingredients = [
            i for i in raw_ingredients if not any(bad in i for bad in forbidden)
        ]

        if len(clean_ingredients) != len(raw_ingredients):
            num_filtered = len(raw_ingredients) - len(clean_ingredients)
            logger.warning(f"Filtered out {num_filtered} unsafe ingredients")

        # 3. Ensure Matcha is present (Guidance for T5)
        if not any("matcha" in i for i in clean_ingredients):
            clean_ingredients.append("matcha powder")

        # 4. BARISTA LOGIC (Force "Latte" Style by ensuring Milk + Sweetener)
        # We select milk deterministically based on the input ingredients to ensure
        # logical pairings (e.g., tropical fruit -> coconut milk).

        if not any("milk" in i for i in clean_ingredients):
            chosen_milk = self._select_logical_milk(clean_ingredients)
            clean_ingredients.append(chosen_milk)
            logger.info(f"Auto-added liquid base: {chosen_milk}")

        # Ensure a Sweetener (Defaulting to Honey as a safe choice)
        if not any(
            s in str(clean_ingredients) for s in ["syrup", "honey", "sugar", "agave"]
        ):
            chosen_sweet = "honey"
            clean_ingredients.append(chosen_sweet)
            logger.info(f"Auto-added sweetener: {chosen_sweet}")

        # The model expects "items: ing1, ing2, ..."
        input_text = f"items: {', '.join(clean_ingredients)}"
        logger.info(f"Generating recipe for input: {input_text}")

        # 5. Generate with T5
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                min_length=60,
                do_sample=True,
                temperature=temperature,
                top_k=50,  # Only consider top 50 tokens (CRITICAL for speed!)
                top_p=0.92,  # Nucleus sampling (CRITICAL for speed!)
                repetition_penalty=1.2,
                no_repeat_ngram_size=2,
                num_return_sequences=1,
            )

        # Decode output
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=False)
        logger.info(f"Raw model output: {generated_text}")

        # 6. Parse and Format
        return self._parse_t5_output(generated_text, clean_ingredients)

    def _select_logical_milk(self, ingredients: List[str]) -> str:
        """Deterministically select a milk type based on input ingredients.

        Returns:
            str: The selected milk type
        """
        # Join ingredients for easy searching
        context = " ".join(ingredients).lower()

        # Logic 1: Tropical -> Coconut
        if any(
            word in context
            for word in ["mango", "pineapple", "coconut", "tropical", "passion"]
        ):
            return "coconut milk"

        # Logic 2: Nutty/Chocolate -> Almond
        if any(
            word in context for word in ["almond", "nut", "chocolate", "cocoa", "cacao"]
        ):
            return "almond milk"

        # Logic 3: Soy preference
        if any(word in context for word in ["soy", "bean", "tofu"]):
            return "soy milk"

        # Default safe option
        return "oat milk"

    def _parse_t5_output(self, text: str, input_ingredients: List[str] = None) -> str:
        """Parse the T5 output string into a readable recipe.

        Args:
            text: Raw model output
            input_ingredients: Original ingredients from prompt

        Expected format (roughly):
        title: Title <section> ingredients: ing1 <sep> ing2
        <section> directions: step1 <sep> step2
        """
        # Clean up the text first
        text = text.replace("</s>", "").replace("<pad>", "").strip()

        # Default values
        title = "Matcha Recipe"
        ingredients = []
        directions = []

        try:
            # Split into main sections
            parts = text.split("<section>")

            for part in parts:
                part = part.strip()
                if part.startswith("title:"):
                    title = part.replace("title:", "").strip()
                elif part.startswith("ingredients:"):
                    ing_text = part.replace("ingredients:", "").strip()
                    ingredients = [i.strip() for i in ing_text.split("<sep>")]
                elif part.startswith("directions:"):
                    dir_text = part.replace("directions:", "").strip()
                    directions = [d.strip() for d in dir_text.split("<sep>")]

            # RECOVERY: Ensure all input ingredients are present in the list
            if input_ingredients:
                current_lower = [i.lower() for i in ingredients]
                for original in input_ingredients:
                    # Don't duplicate if already roughly there
                    # CHECK: Is 'original' (e.g. "coconut milk") inside
                    # any 'current' (e.g. "2 cups coconut milk")?
                    is_present = False
                    original_clean = original.lower()

                    for existing in current_lower:
                        if original_clean in existing:
                            is_present = True
                            break

                    if not is_present:
                        logger.info(f"Recovering dropped ingredient: {original}")
                        ingredients.append(original)

            if not ingredients and not directions:
                logger.warning("Standard parsing failed, returning raw text")
                return text

            # THEME ENFORCER: Force "Latte" naming convention
            if "milkshake" in title.lower() or "smoothie" in title.lower():
                logger.info(f"Enforcing Latte Theme: Renaming '{title}'")
                title = title.replace("Milkshake", "Latte").replace("Smoothie", "Latte")
                title = title.replace("milkshake", "Latte").replace("smoothie", "Latte")

            # Ensure it ends with Latte if generic
            if "recipe" in title.lower():
                title = title.replace("Recipe", "Latte")

            # Ensure "Matcha" is in the title
            if "matcha" not in title.lower():
                title = f"Matcha {title}"

            # QUICK FIX: Generate better title if model produced garbage
            title_words = title.strip().split()

            # Fix 1: Title too simple (e.g., just "matcha")
            if len(title_words) <= 2:
                logger.info(f"Title too simple: '{title}' - generating better one")
                main_ingredient = None
                for ing in ingredients:
                    ing_lower = ing.lower()
                    if (
                        "matcha" not in ing_lower
                        and "milk" not in ing_lower
                        and "water" not in ing_lower
                        and "ice" not in ing_lower
                    ):
                        main_ingredient = ing.strip()
                        break

                if main_ingredient:
                    title = f"{main_ingredient.title()} Matcha Latte"
                else:
                    title = "Signature Matcha Latte"

            # Fix 2: Remove duplicate "matcha" (e.g., "matcha Matcha...")
            if title.lower().count("matcha") > 1:
                title = " ".join(
                    word
                    for i, word in enumerate(title_words)
                    if word.lower() != "matcha"
                    or i == 0
                    or title_words[i - 1].lower() != "matcha"
                )

            # Fix 3: Capitalize properly
            title = " ".join(word.capitalize() for word in title.split())

            # HALLUCINATION CHECK: Detect Oven/Baking/Ice Cream instructions
            combined_text = " ".join(directions).lower()
            banned_words = [
                "oven",
                "bake",
                "baking",
                "preheat",
                "churn",
                "ice cream maker",
                "freezer",
                "loaf",
                "pan",
                "gelato",
                "ice bath",
            ]

            if any(bad in combined_text for bad in banned_words):
                msg = "Model hallucinated a solid food recipe!"
                logger.warning(f"{msg} Rewriting directions.")
                # Emergency Override: Generate standard Latte steps
                directions = self._generate_emergency_latte_steps(ingredients)

            # 6. Format (Inside Try Block to catch formatting errors)
            return self._format_recipe(title, ingredients, directions)

        except Exception as e:
            logger.error(f"Error parsing/formatting recipe: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return f"Error parsing generated recipe.\nRaw output: {text}"

    def _generate_emergency_latte_steps(self, ingredients: List[str]) -> List[str]:
        """Generate standard latte steps if the model goes rogue (baking/cooking)."""
        steps = []

        # Identify components
        liquid_keywords = ["milk", "water", "soy", "oat", "almond", "coconut"]
        liquids = [
            i
            for i in ingredients
            if any(keyword in i.lower() for keyword in liquid_keywords)
        ]
        powders = [
            i
            for i in ingredients
            if "powder" in i.lower() and "matcha" not in i.lower()
        ]
        sweeteners = [
            i
            for i in ingredients
            if any(s in i.lower() for s in ["honey", "syrup", "sugar", "agave"])
        ]
        others = [
            i
            for i in ingredients
            if i not in liquids
            and i not in powders
            and i not in sweeteners
            and "matcha" not in i.lower()
        ]

        # Step 1: Sift Matcha
        steps.append(
            "Sift the matcha powder into your favorite mug to remove any lumps."
        )

        # Step 2: Base Water/Milk
        steps.append(
            "Add hot water (about 175°F) and whisk vigorously "
            "until a foamy paste forms."
        )

        # Step 3: Milk
        if liquids:
            milk = liquids[0]
            steps.append(
                f"Steam or froth the {milk} until warm and creamy, "
                f"then pour it over the matcha base."
            )
        else:
            steps.append("Steam your milk of choice and pour it over the matcha base.")

        # Step 4: Sweetener
        if sweeteners:
            steps.append(f"Stir in the {sweeteners[0]} to sweeten to your liking.")

        # Step 5: Extras (Powders go in early, Others go in late)
        for p in powders:
            steps.insert(2, f"Whisk in the {p} along with the matcha paste.")

        for o in others:
            steps.append(f"Top with {o} or stir it in gently.")

        steps.append("Enjoy your perfectly handcrafted matcha latte!")

        return steps

    def _format_recipe(
        self, title: str, ingredients: List[str], directions: List[str]
    ) -> str:
        """Format recipe as readable text.

        Args:
            title: Recipe title
            ingredients: List of ingredients
            directions: List of instruction steps

        Returns:
            Formatted recipe text
        """
        # POST-PROCESSING SAFETY CHECK (UNIVERSAL):
        # Ensure ALL ingredients are actually used in the steps.

        combined_directions = " ".join(directions).lower()

        # Don't check for these basics as they are often implied or used as 'milk'
        skip_check = ["matcha", "water", "ice", "sugar", "syrup", "milk"]

        for ing in ingredients:
            simple_ing = ing.lower()

            # Skip basics to avoid false positives/clutter
            if any(s in simple_ing for s in skip_check):
                continue

            # Extract main noun (e.g. "protein powder" -> "protein")
            # Check if significant word exists in directions
            # FIX: Remove punctuation so "honey," becomes "honey"
            clean_ing = simple_ing.translate(str.maketrans("", "", string.punctuation))
            words = [
                w
                for w in clean_ing.split()
                if len(w) > 3 and w not in ["powder", "extract"]
            ]

            if not words:
                continue  # Skip if we filtered everything out

            found = False
            for word in words:
                if word in combined_directions:
                    found = True
                    break

            if not found:
                logger.warning(f"Model forgot to use {ing}. Injecting step.")

                # Clean ingredient name for injection (remove "to taste", etc)
                ing_name = ing.split(",")[0].strip()

                # Context-aware injection
                if "powder" in simple_ing or "collagen" in simple_ing:
                    directions.append(
                        f"Add the {ing_name} and whisk vigorously until smooth."
                    )
                elif any(x in simple_ing for x in ["honey", "extract"]):
                    directions.append(f"Stir in the {ing_name} to taste.")
                elif any(
                    x in simple_ing for x in ["berry", "fruit", "mango", "strawberry"]
                ):
                    directions.append(
                        f"Muddle the {ing_name} at the bottom of the glass."
                    )
                else:
                    # Fallback for things like Lavender
                    directions.append(f"Add the {ing_name} and mix gently to combine.")

        output = [f"Title: {title}", ""]

        output.append("Ingredients:")
        for ing in ingredients:
            if ing:
                output.append(f"- {ing.capitalize()}")
        output.append("")

        output.append("Directions:")
        for i, direction in enumerate(directions, 1):
            if direction:
                # FIX: Remove leading numbers from model output
                # (e.g. "1. Preheat" -> "Preheat")
                clean_direction = re.sub(r"^\d+\.\s*", "", direction)

                # FIX: "7 10 minutes" -> "7-10 minutes"
                # Look for digit space digit patterns
                pattern = r"(\d+)\s+(\d+)\s*(min|hour)"
                fixed_direction = re.sub(pattern, r"\1-\2 \3", clean_direction)
                output.append(f"{i}. {fixed_direction.capitalize()}")

        return "\n".join(output)
