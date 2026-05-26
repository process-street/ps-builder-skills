#!/usr/bin/env python3
"""
Search Gmail thread files for mentions of given terms.

Usage:
    python gmail_search.py "term1" "term2" "term3"

Searches: scripts/gmail_output/threads/*.txt
Output:   Prints matched threads with date, subject, and context snippet.
          Prints "No matching Gmail threads found." if nothing matches.

Requires: Local Gmail thread files in scripts/gmail_output/threads/
          Run gmail_extract.py first to pull threads from the Gmail API.
"""

import os
import sys

THREADS_DIR = os.path.join(os.path.dirname(__file__), "gmail_output", "threads")


def search(terms):
    if not os.path.isdir(THREADS_DIR):
        print(f"Gmail threads directory not found: {THREADS_DIR}")
        print("Run gmail_extract.py first.")
        return

    matches = []
    for fname in sorted(os.listdir(THREADS_DIR)):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(THREADS_DIR, fname)
        try:
            with open(fpath, "r", errors="replace") as f:
                content = f.read()
        except Exception:
            continue

        content_lower = content.lower()
        for term in terms:
            if term and len(term) > 3 and term.lower() in content_lower:
                # Date from filename (first 10 chars: YYYY-MM-DD)
                thread_date = fname[:10]
                # Subject from filename (after date_threadid_)
                parts = fname.split("_", 2)
                subject = parts[2].replace(".txt", "").replace("_", " ") if len(parts) > 2 else fname

                # Find surrounding context
                idx = content_lower.find(term.lower())
                snippet = content[max(0, idx - 150):idx + 150].strip().replace("\n", " ")

                matches.append({
                    "date": thread_date,
                    "subject": subject[:80],
                    "snippet": snippet,
                    "term_matched": term,
                })
                break  # one match per file

    # Most recent 3
    matches = matches[-3:]

    if not matches:
        print("No matching Gmail threads found.")
        return

    for m in matches:
        print(f"Date: {m['date']} | Subject: {m['subject']}")
        print(f"Term matched: {m['term_matched']}")
        print(f"Context: {m['snippet']}")
        print()


if __name__ == "__main__":
    terms = sys.argv[1:]
    if not terms:
        print("Usage: gmail_search.py term1 term2 ...")
        sys.exit(1)
    search(terms)
