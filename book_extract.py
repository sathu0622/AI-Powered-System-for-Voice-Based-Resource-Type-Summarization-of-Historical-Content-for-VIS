# Install dependencies if needed:
# pip install pdfplumber

import pdfplumber
import re
import json
import os

# Path to your PDF
pdf_path = r"D:\grade-10-history-text-book-64017cf286c01.pdf"

# Output JSON file
output_json = r"C:\Users\DELL\Downloads\book_full.json"

# Extract text from PDF
all_text = ""
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            all_text += page_text + "\n"

# Remove page numbers (lines with only digits)
all_text = "\n".join([line for line in all_text.splitlines() if not re.match(r'^\d+$', line.strip())])

# Regex pattern to detect headings (chapter or subchapter)
# Example patterns: "1", "1.1", "1.2", "Chapter 1", "King Vasabha"
heading_pattern = re.compile(r'^(?:\d+(?:\.\d+)*|Chapter\s+\w+|[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s*$', re.MULTILINE)

# Find all headings
headings = heading_pattern.findall(all_text)

# Split text into sections based on headings
sections = heading_pattern.split(all_text)[1:]  # skip text before first heading

# Combine headings and content into a list of dictionaries
book_data = []
for heading, content in zip(headings, sections):
    # Clean heading text
    clean_heading = re.sub(r'[\r\n]+', ' ', heading.strip())
    book_data.append({
        "title": clean_heading,
        "content": content.strip()
    })

# Save everything in a single JSON file
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(book_data, f, ensure_ascii=False, indent=4)

print(f"All subtopics extracted and saved in '{output_json}' successfully!")
