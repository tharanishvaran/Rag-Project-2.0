"""Quick verification of all fixed APIs."""
import time, os, sys, requests
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('GEMINI_API_KEY')
print("=" * 50)

# Test Chat
print("[1] Chat: gemini-3.5-flash-lite")
t0 = time.time()
r = requests.post(
    f'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={key}',
    json={'contents': [{'parts': [{'text': 'Say hi in 3 words'}]}], 'generationConfig': {'maxOutputTokens': 20}},
    timeout=10
)
t1 = time.time()
if r.status_code == 200:
    ans = r.json()['candidates'][0]['content']['parts'][0]['text']
    print(f"  OK {t1-t0:.2f}s -> {ans.strip()}")
else:
    print(f"  FAIL {t1-t0:.2f}s -> {r.status_code}: {r.text[:200]}")

# Test Embedding
print("[2] Embed: gemini-embedding-001")
t0 = time.time()
r = requests.post(
    f'https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={key}',
    json={'model': 'models/gemini-embedding-001', 'content': {'parts': [{'text': 'hello world'}]}},
    timeout=10
)
t1 = time.time()
if r.status_code == 200:
    v = r.json().get('embedding', {}).get('values', [])
    print(f"  OK {t1-t0:.2f}s -> {len(v)}-dim vector")
else:
    print(f"  FAIL {t1-t0:.2f}s -> {r.status_code}: {r.text[:200]}")

# Test Batch Embedding
print("[3] Batch Embed: 10 chunks")
t0 = time.time()
r = requests.post(
    f'https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:batchEmbedContents?key={key}',
    json={'requests': [{'model': 'models/gemini-embedding-001', 'content': {'parts': [{'text': f'chunk {i}'}]}} for i in range(10)]},
    timeout=15
)
t1 = time.time()
if r.status_code == 200:
    e = r.json().get('embeddings', [])
    print(f"  OK {t1-t0:.2f}s -> {len(e)} embeddings")
else:
    print(f"  FAIL {t1-t0:.2f}s -> {r.status_code}: {r.text[:200]}")

print("=" * 50)
print("ALL TESTS COMPLETE")
