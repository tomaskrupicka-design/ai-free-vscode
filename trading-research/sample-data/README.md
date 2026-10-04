# Historical data input

Place CSV files here when running local research.

Minimum format:

```csv
date,close
2025-01-02,100.25
2025-01-03,101.10
```

Optional columns: `open,high,low,volume`.

The loader sorts by date, removes duplicate timestamps, validates numeric prices,
and rejects non-positive close values.

Do not commit private brokerage exports, API keys, account IDs, or other secrets.
