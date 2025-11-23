"""Clean training data by removing brand names and normalizing text."""

import re
from pathlib import Path

# Brand names to remove/replace
BRAND_PATTERNS = [
    # Jade Leaf variations
    (r"Jade Leaf Teahouse Ceremonial Matcha", "ceremonial matcha"),
    (r"Jade Leaf Ceremonial Matcha", "ceremonial matcha"),
    (r"Jade Leaf matcha powder", "matcha powder"),
    (r"Jade Leaf matcha", "matcha"),
    (r"Jade Leaf", ""),  # Remove completely if standalone
    # Other common matcha brands
    (r"DoMatcha", "matcha"),
    (r"Mizuba", "matcha"),
    (r"Encha", "matcha"),
    (r"Pique", "matcha"),
    # Generic brand patterns
    (r"[Bb]rand(?:ed)?\s+matcha", "matcha"),
    (r"premium grade matcha", "matcha"),
    (r"culinary grade matcha", "matcha"),
]

# Additional cleaning patterns
CLEANUP_PATTERNS = [
    # Fix multiple spaces
    (r"\s+", " "),
    # Fix lines that start with just a comma or dash after brand removal
    (r"^[-,]\s*$", ""),
    # Remove empty ingredient lines
    (r"^-\s*$", ""),
]


def clean_text(text: str) -> str:
    """Clean recipe text by removing brand names.

    Args:
        text: Raw recipe text

    Returns:
        Cleaned recipe text
    """
    cleaned = text

    # Apply brand pattern replacements
    for pattern, replacement in BRAND_PATTERNS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # Apply cleanup patterns
    for pattern, replacement in CLEANUP_PATTERNS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE)

    # Remove lines that became empty after brand removal
    lines = []
    for line in cleaned.split("\n"):
        stripped = line.strip()
        # Keep line if it's not empty or if it's a separator
        if stripped or line == "---":
            lines.append(line)

    return "\n".join(lines)


def main():
    """Clean the training data file."""
    input_file = Path("assets/matcha_recipes_combined.txt")
    output_file = Path("assets/matcha_recipes_combined_cleaned.txt")
    backup_file = Path("assets/matcha_recipes_combined_backup.txt")

    print(f"Reading from: {input_file}")

    # Read original data
    with input_file.open("r", encoding="utf-8") as f:
        original_text = f.read()

    # Clean the text
    print("Cleaning data...")
    cleaned_text = clean_text(original_text)

    # Count changes
    original_mentions = original_text.lower().count("jade leaf")
    cleaned_mentions = cleaned_text.lower().count("jade leaf")

    print(f"Original 'Jade Leaf' mentions: {original_mentions}")
    print(f"Cleaned 'Jade Leaf' mentions: {cleaned_mentions}")
    print(f"Removed: {original_mentions - cleaned_mentions} mentions")

    # Create backup of original
    print(f"Creating backup: {backup_file}")
    with backup_file.open("w", encoding="utf-8") as f:
        f.write(original_text)

    # Write cleaned data to new file
    print(f"Writing cleaned data to: {output_file}")
    with output_file.open("w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print("\n✓ Data cleaning complete!")
    print(f"  - Original: {len(original_text)} chars")
    print(f"  - Cleaned: {len(cleaned_text)} chars")
    print(f"  - Backup saved to: {backup_file}")
    print(f"  - Cleaned data saved to: {output_file}")


if __name__ == "__main__":
    main()
