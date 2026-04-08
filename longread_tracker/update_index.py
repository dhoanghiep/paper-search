#!/usr/bin/env python3
"""
Mark papers as read in the index and append to knowledge memory.
Called after Claude has summarized the papers.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

TRACKER_DIR = Path(__file__).parent
INDEX_FILE = TRACKER_DIR / "index.json"
MEMORY_FILE = TRACKER_DIR / "knowledge_memory.md"

def mark_papers_read(paper_ids: list, summaries: list = None):
    with open(INDEX_FILE) as f:
        index = json.load(f)

    index["read_papers"].extend(paper_ids)
    index["read_papers"] = list(set(index["read_papers"]))
    index["last_run"] = datetime.now().isoformat()
    index["total_processed"] = len(index["read_papers"])

    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)

    print(f"Index updated: {len(index['read_papers'])} total papers tracked")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: update_index.py 'id1,id2,id3'")
        sys.exit(1)
    ids = [i.strip() for i in sys.argv[1].split(",") if i.strip()]
    mark_papers_read(ids)
