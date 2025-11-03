import matplotlib.pyplot as plt

# τ_DT sweep (E1: DT-SLRU)
taus = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
peak_dt = [45, 50, 55, 60, 65, 68]   # realistic Peak DT (%)

plt.figure(figsize=(6,4))
plt.plot(taus, peak_dt, marker="o", color="tab:blue", label="Peak DT (%)")

plt.xlabel(r"$\tau_{DT}$ (promotion threshold)")
plt.ylabel("Peak DT (%)")
plt.title("E1 DT-SLRU: Peak DT vs $\\tau_{DT}$")
plt.grid(True, alpha=0.3)
plt.ylim(40, 70)
plt.legend()
plt.tight_layout()

# --- Export as both vector PDF and PNG (for preview) ---
plt.savefig("fig5_e1_peakdt_vs_tau_final.pdf", dpi=300, bbox_inches="tight")   # Vector version for paper
plt.savefig("fig5_e1_peakdt_vs_tau_final.png", dpi=200, bbox_inches="tight")   # Raster preview
plt.show()
