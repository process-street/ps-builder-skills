#!/usr/bin/env python3
"""
Search Gong transcripts for mentions of given terms.

Usage:
    python gong_search.py "term1" "term2" "term3"

Output:
    Prints matched calls with date, title, and surrounding context snippet.
    Prints "No matching Gong calls found." if nothing matches.

Requires: Local Gong transcript files in scripts/gong_output/transcripts/
          Run gong_extract.py first to pull transcripts from the Gong API.
"""

import os
import sys

TRANSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "gong_output", "transcripts")


def search(terms):
    if not os.path.isdir(TRANSCRIPTS_DIR):
        print(f"Transcripts directory not found: {TRANSCRIPTS_DIR}")
        return

    matches = []
    for fname in sorted(os.listdir(TRANSCRIPTS_DIR)):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(TRANSCRIPTS_DIR, fname)
        try:
            with open(fpath, "r", errors="replace") as f:
                content = f.read()
        except Exception as e:
            continue

        content_lower = content.lower()
        for term in terms:
            if term and len(term) > 3 and term.lower() in content_lower:
                call_date = fname[:10]
                call_title = fname[12:].replace(".txt", "").replace("_", " ")
                idx = content_lower.find(term.lower())
                snippet = content[max(0, idx - 150):idx + 150].strip().replace("\n", " ")
                matches.append({
                    "date": call_date,
                    "title": call_title[:80],
                    "snippet": snippet,
                    "term_matched": term,
                })
                break  # one match per file is enough

    # Keep only the 3 most recent
    matches = matches[-3:]

    if not matches:
        print("No matching Gong calls found.")
        return

    for m in matches:
        print(f"Date: {m['date']} | Title: {m['title']}")
        print(f"Term matched: {m['term_matched']}")
        print(f"Context: {m['snippet']}")
        print()


if __name__ == "__main__":
    terms = sys.argv[1:]
    if not terms:
        print("Usage: gong_search.py term1 term2 ...")
        sys.exit(1)
    search(terms)
