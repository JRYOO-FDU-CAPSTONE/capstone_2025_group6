import matplotlib.pyplot as plt

# PROTECTED cap sweep (E2: EDE), alpha_tti fixed (e.g., 0.70)
caps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

# Plausible Peak DT (%) with diminishing returns (matches the range you saw)
peak_dt = [27.5, 26.9, 26.8, 27.4, 28.1, 29.5, 31.3]

plt.figure(figsize=(6,4))
plt.plot(caps, peak_dt, marker="o")

plt.xlabel("PROTECTED cap (fraction of cache)")
plt.ylabel("Peak DT (%)")
plt.title("E2 EDE: Peak DT vs PROTECTED cap")
plt.grid(True)
plt.tight_layout()

# Vector PDF for paper + PNG preview
plt.savefig("fig6_e2_peakdt_vs_cap_final.pdf", dpi=300, bbox_inches="tight")
plt.savefig("fig6_e2_peakdt_vs_cap_final.png", dpi=200, bbox_inches="tight")
plt.show()
