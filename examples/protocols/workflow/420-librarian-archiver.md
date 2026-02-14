---
title: Librarian Archiver
type: protocol
tags: [automation, library, ingestion, workflow]
---

# Protocol 420: Librarian Archiver

> **Purpose**: Automated ingestion of external knowledge (Articles, YouTube) into the Sovereign Library.
> **Trigger**: User runs `/archive <url>`

## 1. Architecture

The Librarian splits ingestion into two streams:

1. **Articles**: Fetches text, uses LLM to extract metadata (Title, Author, Summary), and saves as Markdown.
2. **YouTube**: Fetches transcript, uses LLM to summarize and chapterize, and saves as Markdown.

## 2. Storage Schema

- **Articles**: `.context/library/articles/YYYY-MM-DD-slug.md`
- **Videos**: `.context/library/videos/YYYY-MM-DD-slug.md`

## 3. Usage

```bash
# Unified Command
python3 .agent/scripts/librarian/archive.py "https://example.com/article"
python3 .agent/scripts/librarian/archive.py "https://youtube.com/watch?v=..."
```

## 4. Dependencies

- `requests`, `beautifulsoup4` (Articles)
- `youtube-transcript-api` (Videos)
- `gemini_client` (Metadata Enrichment)
