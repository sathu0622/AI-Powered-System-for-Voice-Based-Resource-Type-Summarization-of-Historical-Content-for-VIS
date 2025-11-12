from newspaper import Article
import pandas as pd

# 📰 List of article URLs
urls = [
    "https://www.bbc.com/news/articles/c4gj6149gq9o",
    "https://www.bbc.com/news/articles/c0jqx5548e5o",
    "https://www.bbc.com/news/articles/c3vnkely463o",
]

data = []  # store all extracted data here

for url in urls:
    try:
        article = Article(url)
        article.download()
        article.parse()

        record = {
            "source_type": "newspaper",
            "title": article.title,
            "content": article.text,
            "target_summary": "",        # leave blank initially
            "summary_depth": "short"
        }

        data.append(record)
        print(f"✅ Saved: {article.title}")

    except Exception as e:
        print(f"❌ Failed to extract {url}: {e}")

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("newspaper_articles.csv", index=False, encoding="utf-8")

print("\n📁 Saved as 'newspaper_articles.csv'")
