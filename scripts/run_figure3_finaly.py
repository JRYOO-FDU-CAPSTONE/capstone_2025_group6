#!/usr/bin/env python3
import os, sys, subprocess, re, lzma, math, csv
import matplotlib.pyplot as plt

# ========= CONFIG (edit if you must, otherwise leave as-is) =========
TRACE   = "data/tectonic/201910/Region1/full_0_0.1.trace"  # has numeric suffixes → OK
SIZE_GB = 400
CAPS    = [0.1, 0.3, 0.5, 0.7, 0.9]
OUTROOT = "runs_fig3"
TITLE   = "Figure 3: Peak DT vs PROTECTED cap (EDE)"
# ====================================================================

# embed fonts as vectors in PDF
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype']  = 42

PEAK_PATTERNS = [
    r"Peak\s+Service\s+Time\s+Utilization\s*\(%\)\s*-\s*([0-9]+(?:\.[0-9]+)?)",
    r"Peak\s+Service\s+Time\s+Util\w*\s*\(%\)\s*-\s*([0-9]+(?:\.[0-9]+)?)",
    r"Peak\w*.*?Util\w*\s*\(%\)\s*-\s*([0-9]+(?:\.[0-9]+)?)",
    r"Peak\s+Service\s+Time\s+Utilization\s*\(%\)\s*\[GET\]\s*-\s*([0-9]+(?:\.[0-9]+)?)",
]

def parse_peak_from_stdout(txt: str):
    for pat in PEAK_PATTERNS:
        m = re.search(pat, txt, re.I)
        if m: return float(m.group(1))   # already in %
    return math.nan

def parse_peak_from_stats(run_dir: str):
    stats = None
    for r, _, fs in os.walk(run_dir):
        for f in fs:
            if f.endswith(".stats.lzma"):
                stats = os.path.join(r, f); break
        if stats: break
    if not stats: return math.nan
    try:
        with lzma.open(stats, "rt", encoding="utf-8", errors="ignore") as fh:
            txt = fh.read()
        nums = re.findall(r"[-+]?\d*\.\d+(?:[eE][-+]?\d+)?", txt)
        return float(nums[-1]) * 100.0 if nums else math.nan  # fraction → %
    except Exception:
        return math.nan

def run_one(cap: float):
    run_dir = os.path.join(OUTROOT, f"ede_cap_{cap}")
    os.makedirs(run_dir, exist_ok=True)
    cmd = [
        sys.executable, "-m", "BCacheSim.cachesim.simulate_ap",
        "--trace", TRACE,
        "--ap", "AcceptAll", "--ap-threshold", "0",
        "--eviction-policy", "EDE",
        "--ede_protected_cap", str(cap), "--ede_alpha_tti", "0.5",
        "--prefetch-when", "never",
        "-s", str(SIZE_GB),
        "--log-interval", "600",
        "-o", run_dir, "--override",
    ]
    print(">>", " ".join(cmd))
    p = subprocess.run(cmd, capture_output=True, text=True)
    stdout_path = os.path.join(run_dir, "stdout.txt")
    with open(stdout_path, "w") as f: f.write(p.stdout)
    # first preference: explicit “Eviction Policy: EDE” print proves wiring
    wired = ("Eviction Policy: EDE" in p.stdout) or ("[EDEPolicy] init" in p.stdout)
    peak = parse_peak_from_stdout(p.stdout)
    if math.isnan(peak):
        peak = parse_peak_from_stats(run_dir)
    return run_dir, p.returncode, wired, peak

def main():
    os.makedirs(OUTROOT, exist_ok=True)
    rows = []
    xs, ys = [], []
    for cap in CAPS:
        run_dir, rc, wired, peak = run_one(cap)
        if not math.isnan(peak):
            print(f"[OK] cap={cap}  Peak DT = {peak:.3f}%  {'(EDE wired)' if wired else ''}")
            xs.append(cap); ys.append(peak)
            rows.append({"cap": cap, "peak_dt_percent": peak, "wired": int(wired), "rc": rc, "dir": run_dir})
        else:
            print(f"[WARN] cap={cap}  Peak DT not found. Check: {run_dir}/stdout.txt")
            rows.append({"cap": cap, "peak_dt_percent": "", "wired": int(wired), "rc": rc, "dir": run_dir})

    # Save CSV
    csv_path = os.path.join(OUTROOT, "figure3_results.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["cap", "peak_dt_percent", "wired", "rc", "dir"])
        w.writeheader()
        for r in rows: w.writerow(r)
    print("Saved:", csv_path)

    # Plot only the points we actually have
    if ys:
        plt.figure(figsize=(6.6,4.4))
        plt.plot(xs, ys, marker="o")
        plt.title(TITLE)
        plt.xlabel("PROTECTED cap (fraction of cache)")
        plt.ylabel("Peak DT (% of provisioned disk time)")
        plt.grid(True)
        plt.tight_layout()
        png = os.path.join(OUTROOT, "figure3_peakdt_vs_cap.png")
        pdf = os.path.join(OUTROOT, "figure3_peakdt_vs_cap.pdf")  # VECTOR
        plt.savefig(png, dpi=180)
        plt.savefig(pdf)  # vector PDF
        print("Saved:", png)
        print("Saved:", pdf)
    else:
        print("No valid points to plot.")

if __name__ == "__main__":
    main()
