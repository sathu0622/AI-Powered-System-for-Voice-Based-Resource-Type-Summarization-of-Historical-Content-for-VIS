import json
import re
from newspaper import Article
from bs4 import BeautifulSoup

# ========== SETTINGS ==========
USE_OPENAI = False  # change to True if you want to use OpenAI API for final text cleaning

# ---------- READ URL LIST ----------
with open("urls2.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

output_data = []

# ---------- BASIC TEXT CLEANING ----------
def basic_clean(text):
    """Remove HTML, extra spaces, newlines, and unwanted characters."""
    text = BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)  # collapse multiple spaces/newlines/tabs
    text = re.sub(r"\\[ntr]", " ", text)  # remove escaped \n, \t, etc.
    text = re.sub(r"[^\x00-\x7F]+", " ", text)  # remove non-ASCII junk (emojis, etc.)
    return text.strip()

# ---------- OPTIONAL: OPENAI CLEANING ----------
if USE_OPENAI:
    from openai import OpenAI
    client = OpenAI()

    def ai_clean(text):
        """Use OpenAI model to make text more natural and remove artifacts."""
        prompt = (
            "Clean the following news article text. Remove ads, gibberish, or weird characters, "
            "but keep all meaningful sentences intact:\n\n" + text
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.2
            )
            cleaned = response.choices[0].message.content.strip()
            return cleaned
        except Exception as e:
            print(f"⚠️ OpenAI cleaning failed: {e}")
            return text
else:
    def ai_clean(text):
        return text

# ---------- SCRAPE LOOP ----------
for i, url in enumerate(urls, start=1):
    print(f"[{i}/{len(urls)}] Scraping: {url}")
    try:
        article = Article(url, language="en")
        article.download()
        article.parse()

        content = basic_clean(article.text)
        content = ai_clean(content)
        title = basic_clean(article.title) if article.title else "Untitled"

        data = {
            "source_type": "newspaper",
            "title": title,
            "content": content,
            "target_summary": "",
            "summary_depth": "short"
        }

        output_data.append(data)

    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")

# ---------- SAVE TO JSON ----------
with open("scraped_articles_newspaper_2.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f"\n✅ Scraping complete! Saved {len(output_data)} clean articles to scraped_articles_newspaper_2.json")
