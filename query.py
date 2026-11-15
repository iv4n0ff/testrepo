#!/usr/bin/env python3
"""Semantic search over the chunks table.  Usage:  python query.py "how do knowledge graphs help RAG" [k]"""
import sys

from ingest import connect, embed

if len(sys.argv) < 2:
    sys.exit('usage: python query.py "your question" [k]')
question = sys.argv[1]
k = int(sys.argv[2]) if len(sys.argv) > 2 else 8

qv = embed([question], kind="query")[0]
conn = connect()
rows = conn.execute(
    """SELECT a.title, a.url, c.heading, c.content,
              1 - (c.embedding <=> %(q)s) AS similarity
       FROM chunks c JOIN articles a ON a.id = c.article_id
       ORDER BY c.embedding <=> %(q)s
       LIMIT %(k)s""",
    {"q": qv, "k": k},
).fetchall()

for title, url, heading, content, sim in rows:
    print(f"\n{sim:.3f}  {title}" + (f"  ›  {heading}" if heading else ""))
    print(f"       {url}")
    print("       " + content[:300].replace("\n", " ") + ("…" if len(content) > 300 else ""))
