---
description: Integrate Wikipedia locally for zero-latency context injection
type: protocol
id: 140
status: experimental
created: 2026-02-15
---

# Protocol 140: The Exocortex (Wikipedia Integration)

> **Philosophy**: "We don't download the internet. We download the map."

## 1. The Strategy: "Tiered Omniscience"

We avoid the bloat of the full 100GB+ dump. We allow Athena to "know" everything by having:

1. **The Index**: A map of every concept (Titles).
2. **The Abstract**: The first paragraph of every concept (Abstracts).
3. **The Deep Dive**: On-demand access to the full text (Kiwix/Web).

## 2. The Mechanics (Python + BZ2)

We use the standard `xml.sax` and `bz2` libraries to stream-read the compressed dumps without unpacking them.

### Data Source

- **Target**: `enwiki-latest-abstract.xml.gz` (~6GB unpacked, ~1GB compressed)
- **URL**: `https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-abstract.xml.gz`

### The "Flash-RAG" Script (`exocortex.py`)

A light wrapper around `xml.sax` to parse the compressed XML stream.

```python
import xml.sax
import gzip

class AbstractHandler(xml.sax.ContentHandler):
    def __init__(self, target_term):
        self.target = target_term
        self.in_doc = False
        self.buffer = ""
        self.found = None

    def startElement(self, name, attrs):
        if name == "doc": self.in_doc = True
    
    def characters(self, content):
        if self.in_doc: self.buffer += content

    def endElement(self, name):
        if name == "doc":
            if self.target.lower() in self.buffer.lower(): # Simple match
                self.found = self.buffer
                # In a real implementation, we would yield or stop here
            self.buffer = ""
            self.in_doc = False
```

## 3. The "Full Mirror" (Kiwix)

For deep research without internet, we use Kiwix.

- **Tool**: `kiwix-serve`
- **Data**: `wikipedia_en_all_nopic.zim` (~40GB)
- **Port**: 8080 (Localhost)
- **Integration**: Athena queries `http://localhost:8080/search?q=Term`

## 4. Implementation Plan

1. **User Action**: Download `abstract.xml.gz`.
2. **System Action**:
    - Build a fast keyword index (Sqlite) from the XML (~5 mins).
    - Query the index primarily.
3. **Fallback**: If index fails, search web.
