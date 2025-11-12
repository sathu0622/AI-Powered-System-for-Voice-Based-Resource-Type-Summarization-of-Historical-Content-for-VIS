import json
import re
import requests
from newspaper import Article
from bs4 import BeautifulSoup

# ========== SETTINGS ==========
USE_OPENAI = False  # change to True if you want OpenAI cleaning
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# ---------- READ URL LIST ----------
with open("magazine_url.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

output_data = []

# ---------- BASIC TEXT CLEAN ----------
def basic_clean(text):
    text = BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\\[ntr]", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\b(Advertisement|Sponsored|Subscribe|Follow us on|Read more)\b.*?", "", text, flags=re.I)
    return text.strip()

# ---------- AI CLEAN (optional) ----------
if USE_OPENAI:
    from openai import OpenAI
    client = OpenAI()

    def ai_clean(text):
        prompt = (
            "Clean this scraped news article text. "
            "Remove ads, social media prompts, duplicate sentences, and junk, "
            "but preserve all real article content:\n\n" + text
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ OpenAI cleaning failed: {e}")
            return text
else:
    def ai_clean(text):
        return text


# ---------- FALLBACK SCRAPER ----------
def fallback_scrape(url):
    """Try to extract text manually if newspaper3k misses parts."""
    try:
        headers = {"User-Agent": USER_AGENT}
        html = requests.get(url, headers=headers, timeout=15).text
        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted elements
        for tag in soup.find_all(
            ["script", "style", "noscript", "header", "footer", "form", "iframe"]
        ):
            tag.decompose()

        for tag in soup.find_all(
            attrs={"class": re.compile(r"(ad|promo|sponsor|footer|cookie|banner)", re.I)}
        ):
            tag.decompose()
        for tag in soup.find_all(
            attrs={"id": re.compile(r"(ad|promo|sponsor|footer|cookie|banner)", re.I)}
        ):
            tag.decompose()

        # Extract main article container
        possible_containers = soup.find_all(
            ["article", "main", "section", "div"], 
            attrs={"class": re.compile(r"(content|article|body|text|post|story)", re.I)}
        )

        if not possible_containers:
            possible_containers = [soup]

        texts = []
        for container in possible_containers:
            paragraphs = container.find_all("p")
            for p in paragraphs:
                t = p.get_text(strip=True)
                if len(t.split()) > 5:  # skip very short lines
                    texts.append(t)
            if len(" ".join(texts)) > 400:  # good enough article size
                break

        text = " ".join(texts)
        return basic_clean(text)

    except Exception as e:
        print(f"⚠️ Fallback scrape failed for {url}: {e}")
        return ""


# ---------- MAIN SCRAPE LOOP ----------
for i, url in enumerate(urls, start=1):
    print(f"[{i}/{len(urls)}] Scraping: {url}")
    try:
        article = Article(url, language="en")
        article.download()
        article.parse()

        title = basic_clean(article.title) if article.title else "Untitled"
        content = basic_clean(article.text)

        # If the article content looks too short, try fallback
        if len(content) < 300:
            print(f"⚠️ Newspaper text short — trying fallback for: {url}")
            fallback_text = fallback_scrape(url)
            if len(fallback_text) > len(content):
                content = fallback_text

        # Final AI cleaning if enabled
        content = ai_clean(content)

        output_data.append({
            "source_type": "magazine",
            "title": title,
            "content": content,
            "target_summary": "",
            "summary_depth": "medium",
        })

    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")

# ---------- SAVE TO JSON ----------
with open("magazine_dataset.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f"\n✅ Done! Saved {len(output_data)} full articles to magazine_dataset.json")
