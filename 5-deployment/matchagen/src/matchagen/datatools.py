"""Data collection module for scraping matcha recipes from websites."""

import json
import os
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from firecrawl import Firecrawl
from loguru import logger
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

RECIPE_URLS = [
    "https://www.acozykitchen.com/matcha-iced-latte",
    "https://www.jadeleafmatcha.com/blogs/matcha-recipes",
    "https://www.justonecookbook.com/matcha-recipes/",
    "https://maeda-en.com/pages/recipes",
    "https://teakandthyme.com/recipes/matcha-recipes/",
    "https://www.breakfastcriminals.com/matcha-101-healthy-recipes/",
    "https://zhangcatherine.com/best-matcha-10-recipes/",
    "https://teakandthyme.com/mango-matcha-latte/",
    "https://shaynaskitchen.com/recipes/iced-mango-matcha/",
]


class Recipe(BaseModel):
    """Pydantic schema for recipe extraction."""

    title: str = Field(description="The name of the recipe")
    ingredients: list[str] = Field(description="List of ingredients")
    instructions: list[str] = Field(
        description="List of step-by-step instructions"
    )  # noqa: E501


def parse_recipes_from_markdown(markdown: str, url: str) -> list[dict]:
    """Parse recipe information from markdown text.

    Args:
        markdown: Markdown content from the page
        url: URL of the page (for recipe title fallback)

    Returns:
        List of recipe dictionaries
    """
    import re

    recipes = []

    # Look for common recipe patterns in markdown
    # Pattern 1: Ingredients and Instructions sections
    ingredients_pattern = (
        r"(?:##?\s*Ingredients?|INGREDIENTS?)[:\s]*\n(.*?)(?=##|$)"  # noqa: E501
    )
    instructions_pattern = r"(?:##?\s*(?:Instructions?|Directions?|Method|Steps?)|INSTRUCTIONS?)[:\s]*\n(.*?)(?=##|$)"  # noqa: E501

    ingredients_match = re.search(
        ingredients_pattern, markdown, re.IGNORECASE | re.DOTALL
    )
    instructions_match = re.search(
        instructions_pattern, markdown, re.IGNORECASE | re.DOTALL
    )

    if ingredients_match and instructions_match:
        # Extract ingredients
        ingredients_text = ingredients_match.group(1)
        ingredients = [
            line.strip().lstrip("-*•").strip()
            for line in ingredients_text.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

        # Extract instructions
        instructions_text = instructions_match.group(1)
        instructions = [
            line.strip().lstrip("0123456789.-*•").strip()
            for line in instructions_text.split("\n")
            if line.strip()
            and not line.strip().startswith("#")
            and len(line.strip()) > 10
        ]

        if ingredients and instructions:
            # Try to find title
            title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
            title = title_match.group(1) if title_match else "Matcha Recipe"

            recipes.append(
                {
                    "title": title,
                    "ingredients": ingredients[:20],  # Limit to 20
                    "instructions": instructions[:15],  # Limit to 15
                }
            )

    return recipes


def extract_pagination_info(markdown: str) -> int:
    """Extract the maximum page number from pagination.

    Args:
        markdown: Markdown content

    Returns:
        Maximum page number (1 if no pagination found)
    """
    import re

    # Look for pagination patterns
    page_numbers = []

    # Pattern 1: page=N in URLs
    page_matches = re.findall(r"page[=\s]+(\d+)", markdown, re.IGNORECASE)
    page_numbers.extend([int(p) for p in page_matches])

    # Pattern 2: Standalone numbers that could be page numbers
    # Look for sequences like [1] [2] [3] ... [26]
    bracket_numbers = re.findall(r"\[(\d+)\]", markdown)
    page_numbers.extend([int(n) for n in bracket_numbers if int(n) < 100])

    return max(page_numbers) if page_numbers else 1


def extract_recipe_links_from_markdown(
    markdown: str, base_url: str
) -> list[str]:  # noqa: E501
    """Extract recipe links from markdown text.

    Args:
        markdown: Markdown content
        base_url: Base URL for the page

    Returns:
        List of recipe URLs
    """
    import re
    from urllib.parse import urljoin, urlparse

    links = []
    base_domain = urlparse(base_url).netloc

    # Method 1: Find plain recipe URLs in text
    url_pattern = r"https://[^\s\)]+/blogs/[^\s\)]*/[a-z0-9-]+"
    plain_urls = re.findall(url_pattern, markdown)
    for url in plain_urls:
        if urlparse(url).netloc == base_domain:
            skip_patterns = [
                "/tagged",
                "/account",
                "/checkout",
                "/policies",
                "/pages",
                "/collections",
            ]
            if not any(pattern in url for pattern in skip_patterns):
                links.append(url)

    # Method 2: Find markdown formatted links [text](url)
    link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    matches = re.findall(link_pattern, markdown)

    for text, url in matches:
        # Skip if URL is empty or just an anchor
        if not url or url.startswith("#"):
            continue

        # Skip images, CSS, JS files
        if any(
            ext in url.lower()
            for ext in [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".svg",
                ".css",
                ".js",
                ".ico",
            ]
        ):
            continue

        # Only include links that look like recipes
        text_lower = text.lower()
        url_lower = url.lower()

        # Check if it's a recipe path (e.g., /blogs/matcha-recipes/recipe-name)
        is_recipe_path = (
            "/blogs/" in url_lower
            and "/matcha-recipes/" in url_lower
            and url_lower.count("/") >= 4
        )

        # Or contains recipe keywords
        has_keywords = any(
            keyword in text_lower
            for keyword in ["recipe", "latte", "smoothie", "dessert", "cake"]
        )

        if is_recipe_path or has_keywords:
            # Make absolute URL
            if url.startswith("http"):
                full_url = url
            elif url.startswith("/"):
                full_url = urljoin(base_url, url)
            else:
                continue

            # Only include links from same domain
            if urlparse(full_url).netloc == base_domain:
                # Skip pagination, tagged, and other system links
                skip_patterns = [
                    "page=",
                    "?page",
                    "/tagged/",
                    "/account/",
                    "/checkout",
                    "/policies/",
                    "/pages/",
                    "/collections/",
                    "/cdn/",
                ]
                if not any(pattern in full_url for pattern in skip_patterns):
                    links.append(full_url)

    return list(set(links))  # Remove duplicates


def is_valid_recipe(recipe) -> bool:
    """Check if a recipe has valid data.

    Args:
        recipe: Recipe dictionary or any object

    Returns:
        True if recipe has both ingredients and instructions
    """
    # Ensure we have a dict
    if not isinstance(recipe, dict):
        return False

    ingredients = recipe.get("ingredients", [])
    instructions = recipe.get("instructions", [])
    has_ingredients = bool(ingredients and len(ingredients) > 0)
    has_instructions = bool(instructions and len(instructions) > 0)

    # Filter out recipes with suspicious content
    if has_instructions:
        first_instruction = instructions[0].lower()
        # Filter out login pages, listings, etc.
        suspicious_keywords = [
            "sign in",
            "login",
            "email",
            "password",
            "register",
        ]
        has_suspicious = any(
            keyword in first_instruction for keyword in suspicious_keywords
        )
        if has_suspicious:
            return False
    return has_ingredients and has_instructions


def scrape_with_firecrawl(
    url: str, visited: set[str] | None = None, depth: int = 0
) -> list[dict]:
    """Scrape recipes using Firecrawl API.

    Args:
        url: URL of the recipe page
        visited: Set of already visited URLs
        depth: Current recursion depth

    Returns:
        List of recipe dictionaries
    """
    if visited is None:
        visited = set()

    # Avoid revisiting URLs and limit depth
    if url in visited or depth > 1:
        return []

    visited.add(url)

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        logger.warning("FIRECRAWL_API_KEY not set, skipping Firecrawl")
        return []

    try:
        logger.info(f"Scraping {url} with Firecrawl (depth={depth})")
        firecrawl = Firecrawl(api_key=api_key)

        # Try structured data extraction first
        result = firecrawl.scrape(
            url,
            formats=[{"type": "json", "schema": Recipe.model_json_schema()}],
        )

        # Debug logging
        logger.debug(f"Firecrawl result type: {type(result)}")
        if result and hasattr(result, "json"):
            logger.debug(f"JSON result type: {type(result.json)}")
            logger.debug(f"JSON result: {result.json}")

        # Extract recipes from result (result is a Document object)
        recipes = []
        if result and hasattr(result, "json") and result.json:
            extracted = result.json
            logger.debug(f"Extracted type: {type(extracted)}")
            # Ensure extracted is a dict or list, not a Document object
            if hasattr(extracted, "__dict__"):
                # Convert Document-like objects to dict
                try:
                    extracted = dict(extracted)
                except Exception as e:
                    logger.debug(f"Could not convert to dict: {e}")
                    extracted = None

            if extracted:
                # Handle both single recipe and list of recipes
                if isinstance(extracted, dict):
                    if is_valid_recipe(extracted):
                        recipes.append(extracted)
                elif isinstance(extracted, list):
                    valid_recipes = [
                        r for r in extracted if is_valid_recipe(r)
                    ]  # noqa: E501
                    recipes.extend(valid_recipes)

        # If no recipes found, try markdown approach
        markdown_text = None
        if not recipes:
            logger.debug("No recipes from JSON schema, trying markdown")
            md_result = firecrawl.scrape(url, formats=["markdown"])
            logger.debug(f"Markdown result type: {type(md_result)}")

            # Check if markdown extraction succeeded
            if md_result and hasattr(md_result, "markdown"):
                markdown_text = md_result.markdown
                if markdown_text:
                    logger.debug(f"Markdown length: {len(markdown_text)}")
                    # Try to parse recipes from markdown
                    parsed = parse_recipes_from_markdown(markdown_text, url)
                    recipes.extend([r for r in parsed if is_valid_recipe(r)])

        # If still no recipes and we have markdown, try extracting links
        if not recipes and markdown_text and depth == 0:
            logger.debug("No recipes found, looking for recipe links")

            # Check for pagination
            max_page = extract_pagination_info(markdown_text)

            # For known paginated sites, try more pages
            if "jadeleafmatcha.com" in url:
                max_page = max(max_page, 26)  # We know Jade Leaf has 26 pages

            logger.info(f"Detected pagination: {max_page} pages")

            # Collect recipe links from all pages
            all_recipe_links = []

            # If paginated, scrape all pages (limit to 30 for safety)
            if max_page > 1:
                from urllib.parse import (parse_qs, urlencode, urlparse,
                                          urlunparse)

                parsed_url = urlparse(url)
                base_path = parsed_url.path
                query_params = parse_qs(parsed_url.query)

                for page_num in range(1, min(max_page + 1, 31)):
                    # Build paginated URL
                    query_params["page"] = [str(page_num)]
                    new_query = urlencode(query_params, doseq=True)
                    page_url = urlunparse(
                        (
                            parsed_url.scheme,
                            parsed_url.netloc,
                            base_path,
                            "",
                            new_query,
                            "",
                        )
                    )

                    page_info = f"page {page_num}/{max_page}"
                    logger.info(f"Scraping {page_info}: {page_url}")  # noqa: E501

                    # Get markdown for this page
                    page_result = firecrawl.scrape(
                        page_url, formats=["markdown"]
                    )  # noqa: E501
                    if page_result and hasattr(page_result, "markdown"):
                        page_links = extract_recipe_links_from_markdown(
                            page_result.markdown, page_url
                        )  # noqa: E501
                        all_recipe_links.extend(page_links)
                        link_count = len(page_links)
                        logger.info(f"Found {link_count} links on {page_info}")

                    time.sleep(2)  # Be polite between page requests
            else:
                # No pagination, just extract from current page
                all_recipe_links = extract_recipe_links_from_markdown(
                    markdown_text, url
                )

            # Remove duplicates
            all_recipe_links = list(set(all_recipe_links))
            total_links = len(all_recipe_links)
            logger.info(
                f"Total {total_links} unique recipe links to scrape"
            )  # noqa: E501

            # Scrape all recipe links
            for i, link in enumerate(all_recipe_links, 1):
                recipe_num = f"{i}/{len(all_recipe_links)}"
                logger.info(f"Scraping recipe {recipe_num}: {link}")  # noqa: E501
                time.sleep(1)  # Be polite
                link_recipes = scrape_with_firecrawl(link, visited, depth + 1)
                recipes.extend(link_recipes)

        logger.info(f"Extracted {len(recipes)} recipes from {url}")
        return recipes

    except Exception as e:
        logger.warning(f"Firecrawl failed for {url}: {e}")
        return []


def scrape_recipe_page(
    url: str, visited: set[str] | None = None
) -> list[dict]:  # noqa: E501
    """Scrape a recipe page and extract recipe information.

    Args:
        url: URL of the recipe page
        visited: Set of already visited URLs to avoid loops

    Returns:
        List of recipe dictionaries
    """
    if visited is None:
        visited = set()

    if url in visited:
        return []

    # Skip non-recipe URLs
    skip_patterns = ["collections", "products", "cart", "account", "tagged"]
    if any(pattern in url.lower() for pattern in skip_patterns):
        return []

    visited.add(url)
    recipes = []

    try:
        logger.info(f"Scraping {url}")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Try to find recipe structured data (JSON-LD)
        json_ld = soup.find("script", {"type": "application/ld+json"})
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, list):
                    data = data[0] if data else {}
                if data.get("@type") == "Recipe":
                    recipe = extract_recipe_from_json_ld(data)
                    if recipe:
                        recipes.append(recipe)
                        return recipes
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback: Try to find recipe links and scrape them
        if ("/recipes" in url or "/matcha-recipes" in url) and len(
            visited
        ) < 50:  # noqa: E501
            recipe_links = find_recipe_links(soup, url)
            for link in recipe_links[:10]:  # Limit to 10 recipes per listing
                if link not in visited:
                    time.sleep(1)  # Be polite
                    recipes.extend(scrape_recipe_page(link, visited))
            return recipes

        # Try to extract recipe from page structure
        recipe = extract_recipe_from_html(soup, url)
        if recipe:
            recipes.append(recipe)

    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")

    return recipes


def extract_recipe_from_json_ld(data: dict) -> dict | None:
    """Extract recipe from JSON-LD structured data.

    Args:
        data: JSON-LD data dictionary

    Returns:
        Recipe dictionary or None
    """
    try:
        recipe = {
            "title": data.get("name", "Matcha Recipe"),
            "ingredients": [],
            "instructions": [],
        }

        # Extract ingredients
        ingredients = data.get("recipeIngredient", [])
        if isinstance(ingredients, list):
            recipe["ingredients"] = ingredients
        elif isinstance(ingredients, str):
            recipe["ingredients"] = [ingredients]

        # Extract instructions
        instructions = data.get("recipeInstructions", [])
        if isinstance(instructions, list):
            for step in instructions:
                if isinstance(step, dict):
                    text = step.get("text", "")
                elif isinstance(step, str):
                    text = step
                else:
                    continue
                if text:
                    recipe["instructions"].append(text)
        elif isinstance(instructions, str):
            recipe["instructions"] = [instructions]

        if recipe["ingredients"] and recipe["instructions"]:
            return recipe
    except Exception:
        pass
    return None


def find_recipe_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    """Find recipe links on a recipe listing page.

    Args:
        soup: BeautifulSoup object
        base_url: Base URL for relative links

    Returns:
        List of recipe URLs
    """
    links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if any(
            keyword in href.lower()
            for keyword in ["recipe", "matcha", "latte", "smoothie"]
        ):
            if href.startswith("http"):
                links.append(href)
            elif href.startswith("/"):
                links.append(urljoin(base_url, href))
    return list(set(links))  # Remove duplicates


def extract_recipe_from_html(soup: BeautifulSoup, url: str) -> dict | None:
    """Extract recipe from HTML structure.

    Args:
        soup: BeautifulSoup object
        url: URL of the page

    Returns:
        Recipe dictionary or None
    """
    try:
        # Try common selectors for recipe title
        title = None
        for selector in ["h1", ".recipe-title", ".entry-title", "h1.title"]:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                break
        if not title:
            title = "Matcha Recipe"

        # Try to find ingredients
        ingredients = []
        for selector in [
            ".ingredients li",
            ".recipe-ingredients li",
            '[itemprop="recipeIngredient"]',
            ".ingredient",
        ]:
            elems = soup.select(selector)
            if elems:
                ingredients = [elem.get_text(strip=True) for elem in elems]
                break

        # Try to find instructions
        instructions = []
        for selector in [
            ".instructions li",
            ".recipe-instructions li",
            '[itemprop="recipeInstructions"] li',
            ".instruction-step",
            ".step",
        ]:
            elems = soup.select(selector)
            if elems:
                instructions = [elem.get_text(strip=True) for elem in elems]
                break

        # If no list items, try paragraphs
        if not instructions:
            for selector in [
                ".instructions p",
                ".recipe-instructions p",
                ".directions p",
            ]:
                elems = soup.select(selector)
                if elems:
                    instructions = [
                        elem.get_text(strip=True)
                        for elem in elems
                        if elem.get_text(strip=True)
                    ]
                    break

        if ingredients and instructions:
            return {
                "title": title,
                "ingredients": ingredients,
                "instructions": instructions,
            }
    except Exception:
        pass
    return None


def format_recipe(recipe: dict) -> str:
    """Format a recipe dictionary as readable text.

    Args:
        recipe: Dictionary with title, ingredients, instructions

    Returns:
        Formatted recipe string
    """
    text = f"{recipe['title']}\n\n"
    text += "Ingredients:\n"
    for ingredient in recipe["ingredients"]:
        text += f"- {ingredient}\n"
    text += "\nInstructions:\n"
    for i, step in enumerate(recipe["instructions"], 1):
        text += f"{i}. {step}\n"
    text += "\n---\n\n"
    return text


def save_recipes_to_file(recipes: list[dict], filepath: Path | str):
    """Save recipes to a text file for training.

    Args:
        recipes: List of recipe dictionaries
        filepath: Path to save the text file (can be string or Path)
    """
    filepath = Path(filepath)  # Convert to Path if string
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open("w") as file:
        for recipe in recipes:
            file.write(format_recipe(recipe))

    logger.info(f"Saved {len(recipes)} recipes to {filepath}")


def load_or_scrape_data(data_config: dict) -> Path:
    """Load existing recipe data or scrape new data.

    Args:
        data_config: Data configuration dictionary

    Returns:
        Path to the recipe text file
    """
    assets_dir = Path(data_config["assets_dir"])
    filepath = assets_dir / data_config["filename"]

    if filepath.exists():
        logger.info(f"Recipe data already exists at {filepath}")
        return filepath

    logger.info("Scraping matcha recipes from websites...")
    all_recipes = []

    for url in RECIPE_URLS:
        # Try Firecrawl first
        recipes = scrape_with_firecrawl(url)

        # Fall back to BeautifulSoup if Firecrawl fails
        if not recipes:
            recipes = scrape_recipe_page(url)

        all_recipes.extend(recipes)
        logger.info(f"Found {len(recipes)} recipes from {url}")
        time.sleep(2)  # Be polite to servers

    if not all_recipes:
        logger.warning("No recipes scraped, using fallback samples")
        all_recipes = get_fallback_recipes()

    save_recipes_to_file(all_recipes, filepath)
    return filepath


def get_fallback_recipes() -> list[dict]:
    """Get fallback recipes if scraping fails.

    Returns:
        List of sample recipe dictionaries
    """
    return [
        {
            "title": "Classic Matcha Latte",
            "ingredients": [
                "1 tsp matcha powder",
                "2 tbsp hot water",
                "1 cup milk of choice",
                "1 tsp honey or sweetener",
            ],
            "instructions": [
                "Whisk matcha with hot water until smooth",
                "Heat milk and froth if desired",
                "Pour matcha into a cup",
                "Add milk and sweetener",
                "Stir and enjoy",
            ],
        },
        {
            "title": "Iced Matcha Latte",
            "ingredients": [
                "1 tsp matcha powder",
                "2 tbsp hot water",
                "1 cup cold milk",
                "Ice cubes",
                "Sweetener to taste",
            ],
            "instructions": [
                "Whisk matcha with hot water",
                "Fill glass with ice",
                "Pour matcha over ice",
                "Add cold milk",
                "Sweeten to taste and stir",
            ],
        },
    ]


if __name__ == "__main__":
    # Test the scraper
    test_config = {
        "assets_dir": "assets",
        "filename": "matcha_recipes.txt",
    }
    data_file = load_or_scrape_data(test_config)
    print(f"Data saved to: {data_file}")
