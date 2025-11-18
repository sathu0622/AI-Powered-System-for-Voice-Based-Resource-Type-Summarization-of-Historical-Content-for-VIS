import json
import re

def clean_content(text):
    if not text:
        return ""
    cleaned = re.sub(r'\s+', ' ', text).strip()
    cleaned = cleaned.replace('"', '\\"')  # escape quotes
    return cleaned

# Path to your JSON file
input_file = r'D:\Research dataset\Summarization Dataset_Collecting\book_dataset.json'
output_file = r'D:\Research dataset\Summarization Dataset_Collecting\books_cleaned.json'

with open(input_file, 'r', encoding='utf-8') as f:
    raw_text = f.read()

# Remove control characters
raw_text = re.sub(r'[\x00-\x1f]+', ' ', raw_text)

cleaned_objects = []

# Try to load as proper JSON first
try:
    data = json.loads(raw_text)
    # If loaded, it's already a JSON array or dict
    if isinstance(data, list):
        for obj in data:
            if "content" in obj and obj["content"]:
                obj["content"] = clean_content(obj["content"])
            cleaned_objects.append(obj)
    elif isinstance(data, dict):
        if "content" in data and data["content"]:
            data["content"] = clean_content(data["content"])
        cleaned_objects.append(data)
except json.JSONDecodeError:
    # Fallback for messy JSON
    raw_objects = re.findall(r'\{.*?\}', raw_text, flags=re.DOTALL)
    for obj_str in raw_objects:
        try:
            obj = json.loads(obj_str)
            if "content" in obj and obj["content"]:
                obj["content"] = clean_content(obj["content"])
            cleaned_objects.append(obj)
        except:
            continue

# Save cleaned JSON
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(cleaned_objects, f, ensure_ascii=False, indent=4)

print(f"All {len(cleaned_objects)} objects fixed and saved to {output_file}")
