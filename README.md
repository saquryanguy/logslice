# logslice

Stream and filter structured logs from multiple services with a unified query syntax.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install -e .
```

---

## Usage

```python
from logslice import LogStream

# Connect to multiple services and filter with a unified query
stream = LogStream(sources=["nginx", "postgres", "redis"])

for entry in stream.query('level="error" AND service="nginx"'):
    print(entry)
```

Run from the command line:

```bash
logslice --sources nginx postgres --query 'level="error"' --tail
```

**Example output:**

```
[2024-03-12T14:22:01Z] nginx  ERROR  upstream timed out (110) while reading response
[2024-03-12T14:22:03Z] nginx  ERROR  connect() failed (111) while connecting to upstream
```

---

## Features

- Stream logs in real time from multiple services simultaneously
- Filter using a simple, unified query syntax across all sources
- Supports structured log formats (JSON, logfmt, key-value pairs)
- Lightweight CLI and Python API

---

## Query Syntax

Queries use a simple key-value expression language with optional boolean operators:

| Example | Description |
|---|---|
| `level="error"` | Match a specific field value |
| `level="error" AND service="nginx"` | Combine conditions with AND |
| `level="warn" OR level="error"` | Match either condition with OR |
| `service="redis" AND NOT level="debug"` | Exclude matches with NOT |

---

## License

MIT © 2024 Your Name
