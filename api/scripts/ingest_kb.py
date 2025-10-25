import os, sys, json
from typing import List, Tuple
from app.services.kb import kb_upsert
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def read_jsonl(path: str) -> List[Tuple[str, str]]:
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            q = obj.get("question", "").strip()
            s = obj.get("solution", "").strip()
            if q and s:
                pairs.append((q, s))
    return pairs

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.ingest_kb <path_to_jsonl>")
        sys.exit(1)
    path = sys.argv[1]
    pairs = read_jsonl(path)
    n = kb_upsert(pairs)
    print(f"Inserted {n} items into KB (backend={os.getenv('KB_BACKEND','memory')}).")

if __name__ == "__main__":
    main()
