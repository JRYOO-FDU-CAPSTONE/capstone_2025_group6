# scripts/make_metrics.py
import sys, os, re, json, lzma

def parse_metrics(lzma_path):
    import lzma, json

    # The file is a big JSON blob. We'll parse it, then read from the "results" section.
    with lzma.open(lzma_path, "rt", encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    # Ensure we load the first JSON object cleanly.
    data = json.loads("{" + raw.split("{", 1)[1])

    res = data.get("results", {})
    # Keys observed in your files:
    # - Peak DT:      "PeakServiceTimeUtil1"   (percentage value)
    # - Median DT:    "P50ServiceTimeUtil1"    (percentage value)
    # - Hit rate:     "ChunkHitRatio"          (fraction, 0..1)

    peak_dt = res.get("PeakServiceTimeUtil1")
    median_dt = res.get("P50ServiceTimeUtil1")
    hit_rate = res.get("ChunkHitRatio")
    if hit_rate is not None:
        # keep as % for plotting consistency
        hit_rate = 100.0 * float(hit_rate)

    # Also try to keep an "overall" (fallback not required if above are present)
    overall_st = res.get("ServiceTimeSavedRatio")  # may not be what you want; optional

    return {
        "Peak DT (%)": peak_dt,
        "Median DT (%)": median_dt,
        "Cache Hit Rate (%)": hit_rate,
        "source": os.path.abspath(lzma_path),
    }



def main():
    if len(sys.argv) != 3:
        print("usage: python scripts/make_metrics.py <input_cache_perf.txt.lzma> <output_metrics.json>")
        sys.exit(1)
    inp, outp = sys.argv[1], sys.argv[2]
    d = parse_metrics(inp)
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    with open(outp, "w") as f:
        json.dump(d, f, indent=2)
    print(f"Wrote {outp}")

if __name__ == "__main__":
    main()
