import orjson

def chunk_text_from_json(json_file: str, max_words: int = 450):
    """
    Reads JSON file (from PDF or DOCX extraction),
    splits text into chunks, collects images.
    Returns dict: {"chunks": [...], "images": [...]}
    """
    if isinstance(json_file, str):
        with open(json_file, "rb") as f:
            pages = orjson.loads(f.read())
    else:
        raise ValueError("Expected JSON file path as str")

    chunk_list = []
    image_list = []

    for page in pages:
        text = page.get("text", "")
        words = text.split()
        chunk_index = 1

        # Split text into chunks
        for i in range(0, len(words), max_words):
            chunk_text = " ".join(words[i:i + max_words])
            chunk_id = f"{page.get('page', 0)}_{chunk_index}"

            chunk_list.append({
                "id": chunk_id,
                "page": page.get("page", 0),
                "chunk": chunk_text,
                "images": page.get("images", [])  # include images per chunk
            })
            chunk_index += 1

        # Collect all images
        for img in page.get("images", []):
            image_list.append(img)

    return {"chunks": chunk_list, "images": image_list}
