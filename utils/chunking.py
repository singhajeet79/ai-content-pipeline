def chunk_text(text, max_chars=3000):

    chunks = []
    current = ""

    for line in text.split("\n"):
        if len(current) + len(line) < max_chars:
            current += line + "\n"
        else:
            chunks.append(current)
            current = line

    if current:
        chunks.append(current)

    return chunks