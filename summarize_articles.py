# import json
# import asyncio
# import google.generativeai as genai
# import time
# import os
# from asyncio import Semaphore

# # ================= CONFIG =================
# API_KEY = "AIzaSyBO0X8gbmqDd6CkgMMkXRqBQGFAOUN73pE"
# MODEL_NAME = "models/gemini-2.5-flash"  # Free tier
# INPUT_FILE = "magazine_dataset.json"
# OUTPUT_FILE = "articles_with_summary_magazine.json"
# CHECKPOINT_FILE = "checkpoint_magazine.json"
# MAX_PARALLEL = 3  # Number of simultaneous requests

# genai.configure(api_key=API_KEY)
# model = genai.GenerativeModel(MODEL_NAME)

# # ================= PROMPT BUILDER =================
# def build_prompt(text, depth="short"):
#     text = text.strip()
#     if "purchase a subscription" in text.lower():
#         return "The article content is unavailable. Provide a 2-sentence generic summary."
#     if depth == "short":
#         return f"Summarize this article in 3 sentences:\n\n{text}"
#     if depth == "medium":
#         return f"Summarize this article in 6–8 sentences:\n\n{text}"
#     if depth == "long":
#         return f"Write a detailed 150–200 word summary:\n\n{text}"
#     return f"Summarize:\n{text}"

# # ================= SUMMARIZE FUNCTION =================
# async def summarize_one(article, sem: Semaphore, max_retries=10):
#     async with sem:
#         content = article.get("content", "")
#         depth = article.get("summary_depth", "short")
#         prompt = build_prompt(content, depth)
#         wait_time = 5

#         for attempt in range(max_retries):
#             try:
#                 response = await model.generate_content_async(prompt)
#                 article["target_summary"] = response.text.strip()
#                 return article
#             except Exception as e:
#                 err = str(e)
#                 if "429" in err:
#                     print(f"❌ 429 — too many requests. Waiting {wait_time} sec (attempt {attempt+1})...")
#                     await asyncio.sleep(wait_time)
#                     wait_time *= 2  # exponential backoff
#                 else:
#                     print("❌ Error:", err)
#                     article["target_summary"] = ""
#                     return article
#         print("⚠️ Max retries reached. Skipping article.")
#         article["target_summary"] = ""
#         return article

# # ================= MAIN PROCESS =================
# async def run_parallel(dataset):
#     # Load checkpoint if exists
#     start_index = 0
#     if os.path.exists(CHECKPOINT_FILE):
#         with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
#             checkpoint = json.load(f)
#             start_index = checkpoint.get("last_index", 0)
#             dataset = checkpoint.get("data", dataset)
#         print(f"🔄 Resuming from article {start_index+1}...")

#     sem = Semaphore(MAX_PARALLEL)
#     tasks = []
#     results = []

#     for i in range(start_index, len(dataset)):
#         article = dataset[i]

#         # Skip very short content
#         if len(article.get("content", "").strip()) < 20:
#             article["target_summary"] = ""
#             dataset[i] = article
#             # Save checkpoint
#             with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
#                 json.dump({"last_index": i+1, "data": dataset}, f, indent=4, ensure_ascii=False)
#             continue

#         task = asyncio.create_task(summarize_one(article, sem))
#         tasks.append((i, task))

#         # When we reach MAX_PARALLEL tasks, wait for them
#         if len(tasks) >= MAX_PARALLEL:
#             for idx, t in tasks:
#                 result = await t
#                 dataset[idx] = result
#                 # Save checkpoint
#                 with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
#                     json.dump({"last_index": idx+1, "data": dataset}, f, indent=4, ensure_ascii=False)
#                 # Small sleep to prevent hitting rate limit
#                 await asyncio.sleep(1)
#             tasks = []

#     # Wait for remaining tasks
#     for idx, t in tasks:
#         result = await t
#         dataset[idx] = result
#         with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
#             json.dump({"last_index": idx+1, "data": dataset}, f, indent=4, ensure_ascii=False)
#         await asyncio.sleep(1)

#     return dataset

# # ================= ENTRY POINT =================
# if __name__ == "__main__":
#     with open(INPUT_FILE, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     print("⚡ Starting parallel-safe summarization queue...\n")
#     results = asyncio.run(run_parallel(data))

#     # Save final JSON
#     with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#         json.dump(results, f, indent=4, ensure_ascii=False)

#     print(f"\n✅ DONE — Saved summaries to {OUTPUT_FILE}")
#     if os.path.exists(CHECKPOINT_FILE):
#         os.remove(CHECKPOINT_FILE)




import json
import asyncio
import google.generativeai as genai
import time
import os
from asyncio import Semaphore

# ================= CONFIG =================
API_KEY = "AIzaSyAm_amRwIv2DZehvGYk7cLLw6k2eFHoMv0"
MODEL_NAME = "models/gemini-2.5-flash"  # Free tier
INPUT_FILE = "newspaper_dataset3.json"
OUTPUT_FILE = "articles_with_summary_newspaper3.json"
CHECKPOINT_FILE = "checkpoint_paper.json"
MAX_PARALLEL = 3  # Number of simultaneous requests

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# ================= PROMPT BUILDER (CUSTOM) =================
def build_prompt(text, source_type="newspaper"):
    text = text.strip()
    if "purchase a subscription" in text.lower():
        return "The article content is unavailable. Provide a 2-sentence generic summary."

    if source_type == "newspaper":
        return f"Summarize this text in 3 factual sentences:\n{text}"

    elif source_type == "magazine":
        return f"Summarize this text in about half its original length with a descriptive tone:\n{text}"

    else:
        return (
            "Summarize this book excerpt at about 80% of its original depth. "
            "Keep all key ideas, context, and meaning, but express them in a shorter and clearer way. "
            "Do not expand or add new information. Maintain a moderate level of detail.\n"
            f"{text}"
        )

# ================= SUMMARIZE FUNCTION =================
async def summarize_one(article, sem: Semaphore, max_retries=10):
    async with sem:
        content = article.get("content", "")
        source_type = article.get("source_type", "newspaper")  # Use your source_type field
        prompt = build_prompt(content, source_type)
        wait_time = 5

        for attempt in range(max_retries):
            try:
                response = await model.generate_content_async(prompt)
                article["target_summary"] = response.text.strip()
                return article
            except Exception as e:
                err = str(e)
                if "429" in err:
                    print(f"❌ 429 — too many requests. Waiting {wait_time} sec (attempt {attempt+1})...")
                    await asyncio.sleep(wait_time)
                    wait_time *= 2  # exponential backoff
                else:
                    print("❌ Error:", err)
                    article["target_summary"] = ""
                    return article
        print("⚠️ Max retries reached. Skipping article.")
        article["target_summary"] = ""
        return article

# ================= MAIN PROCESS =================
async def run_parallel(dataset):
    start_index = 0
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
            start_index = checkpoint.get("last_index", 0)
            dataset = checkpoint.get("data", dataset)
        print(f"🔄 Resuming from article {start_index+1}...")

    sem = Semaphore(MAX_PARALLEL)
    tasks = []

    for i in range(start_index, len(dataset)):
        article = dataset[i]

        # Skip very short content
        if len(article.get("content", "").strip()) < 20:
            article["target_summary"] = ""
            dataset[i] = article
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump({"last_index": i+1, "data": dataset}, f, indent=4, ensure_ascii=False)
            continue

        task = asyncio.create_task(summarize_one(article, sem))
        tasks.append((i, task))

        if len(tasks) >= MAX_PARALLEL:
            for idx, t in tasks:
                result = await t
                dataset[idx] = result
                with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                    json.dump({"last_index": idx+1, "data": dataset}, f, indent=4, ensure_ascii=False)
                await asyncio.sleep(1)
            tasks = []

    for idx, t in tasks:
        result = await t
        dataset[idx] = result
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_index": idx+1, "data": dataset}, f, indent=4, ensure_ascii=False)
        await asyncio.sleep(1)

    return dataset

# ================= ENTRY POINT =================
if __name__ == "__main__":
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("⚡ Starting parallel-safe summarization queue with custom prompts...\n")
    results = asyncio.run(run_parallel(data))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ DONE — Saved summaries to {OUTPUT_FILE}")
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
