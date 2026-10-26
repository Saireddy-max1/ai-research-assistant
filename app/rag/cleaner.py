import re


def clean_text(text: str) -> str:

    # Normalize Windows line endings.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove trailing spaces from each line.
    lines = [line.strip() for line in text.split("\n")]

    cleaned_lines = []

    for line in lines:

        # Skip completely empty lines temporarily.
        if not line:
            cleaned_lines.append("")
            continue

        # Collapse repeated spaces.
        line = re.sub(r"[ \t]+", " ", line)

        cleaned_lines.append(line)

    # Rebuild the text.
    text = "\n".join(cleaned_lines)

    # Reduce excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()