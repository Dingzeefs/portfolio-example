"""Scrape Jade Leaf Matcha recipes in batches."""

import os
import sys
import time

sys.path.insert(0, "src")  # noqa: E402

from dotenv import load_dotenv  # noqa: E402
from firecrawl import Firecrawl  # noqa: E402
from loguru import logger  # noqa: E402

from matchagen.datatools import (  # noqa: E402
    extract_recipe_links_from_markdown, save_recipes_to_file,
    scrape_with_firecrawl)

load_dotenv()


def scrape_jade_leaf_batch(start_page: int, end_page: int, output_file: str):
    """Scrape a batch of pages from Jade Leaf Matcha.

    Args:
        start_page: First page to scrape (1-indexed)
        end_page: Last page to scrape (inclusive)
        output_file: File to save recipes to
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        logger.error("FIRECRAWL_API_KEY not set")
        return

    firecrawl = Firecrawl(api_key=api_key)
    base_url = "https://www.jadeleafmatcha.com/blogs/matcha-recipes"

    all_recipe_links = []
    all_recipes = []
    visited: set[str] = set()

    logger.info(f"Scraping Jade Leaf pages {start_page}-{end_page}")

    # Collect recipe links from all pages in batch
    for page_num in range(start_page, end_page + 1):
        page_url = f"{base_url}?page={page_num}"
        logger.info(f"Scraping page {page_num}/{end_page}: {page_url}")

        try:
            page_result = firecrawl.scrape(page_url, formats=["markdown"])
            if page_result and hasattr(page_result, "markdown"):
                page_links = extract_recipe_links_from_markdown(
                    page_result.markdown, page_url
                )
                all_recipe_links.extend(page_links)
                link_count = len(page_links)
                logger.info(f"  Found {link_count} links on page {page_num}")
            time.sleep(2)  # Be polite
        except Exception as e:
            logger.error(f"  Failed to scrape page {page_num}: {e}")

    # Remove duplicates
    all_recipe_links = list(set(all_recipe_links))
    logger.info(f"Total {len(all_recipe_links)} unique recipe links to scrape")

    # Scrape each recipe
    for i, link in enumerate(all_recipe_links, 1):
        logger.info(f"Scraping recipe {i}/{len(all_recipe_links)}: {link}")
        try:
            recipes = scrape_with_firecrawl(link, visited, depth=1)
            all_recipes.extend(recipes)
            time.sleep(1)
        except Exception as e:
            logger.error(f"  Failed: {e}")

    # Save results
    logger.info(f"Scraped {len(all_recipes)} valid recipes")
    if all_recipes:
        save_recipes_to_file(all_recipes, output_file)
        logger.info(f"Saved to {output_file}")

    return len(all_recipes)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Jade Leaf in batches")
    parser.add_argument("start", type=int, help="Start page (1-indexed)")
    parser.add_argument("end", type=int, help="End page (inclusive)")
    parser.add_argument(
        "--output",
        default="assets/matcha_recipes_batch.txt",
        help="Output file",
    )

    args = parser.parse_args()

    scrape_jade_leaf_batch(args.start, args.end, args.output)
