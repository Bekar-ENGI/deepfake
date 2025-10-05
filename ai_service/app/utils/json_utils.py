import os
import orjson

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_json(data, filename: str) -> str:
    """
    Save JSON data into OUTPUT_DIR. Returns full path.
    """
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = ".json"
    file_path = os.path.join(OUTPUT_DIR, name + ext)

    i = 1
    while os.path.exists(file_path):
        new_filename = f"{name}_duplicate_{i}{ext}"
        file_path = os.path.join(OUTPUT_DIR, new_filename)
        i += 1

    with open(file_path, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

    return file_path

def load_json(path: str):
    """
    Load JSON from full path or filename inside OUTPUT_DIR.
    """
    if os.path.isabs(path) or path.startswith(OUTPUT_DIR + os.sep):
        file_path = path
    else:
        file_path = os.path.join(OUTPUT_DIR, path)

    with open(file_path, "rb") as f:
        return orjson.loads(f.read())
