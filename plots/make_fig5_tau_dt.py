import json, glob, os
import matplotlib.pyplot as plt

def peak(path):
    with open(path) as f: j = json.load(f)
    return float(j["Peak DT (%)"])

pts = []
for m in glob.glob("./output/e1_tau_*/metrics.json"):
    tau = float(m.split("/")[2].split("_")[-1])
    pts.append((tau, peak(m)))
pts.sort()

xs = [x for x,_ in pts]
ys = [y for _,y in pts]

plt.figure()
plt.plot(xs, ys, marker="o")
plt.xlabel(r"$\tau_{DT}$")
plt.ylabel("Peak DT (%)")
plt.title("DT-SLRU: Peak DT vs $\\tau_{DT}$")
plt.grid(True, alpha=0.3)
os.makedirs("figures", exist_ok=True)
plt.tight_layout()
plt.savefig("figures/figure5.pdf")
print("Wrote figures/figure5.pdf")
