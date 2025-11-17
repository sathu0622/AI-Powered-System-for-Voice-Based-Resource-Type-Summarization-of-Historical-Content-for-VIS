import json

# ---- Step 1: Load your JSON file (even if it's multi-line) ----
input_file = "input.json"       # your original JSON file
output_file = "output_oneline.json"  # the new single-line JSON file

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# ---- Step 2: Convert JSON to ONE single line ----
one_line_json = json.dumps(data, separators=(',', ':'))

# ---- Step 3: Save it ----
with open(output_file, "w", encoding="utf-8") as f:
    f.write(one_line_json)

print("JSON converted into one line and saved as:", output_file)
