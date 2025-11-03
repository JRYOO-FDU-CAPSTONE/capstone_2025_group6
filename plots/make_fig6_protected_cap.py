import json, glob, os
import matplotlib.pyplot as plt

def peak(path):
    with open(path) as f: j = json.load(f)
    return float(j["Peak DT (%)"])

pts = []
for m in glob.glob("./output/e2_cap_*/metrics.json"):
    cap = float(m.split("/")[2].split("_")[-1]) * 100.0  # to %
    pts.append((cap, peak(m)))
pts.sort()

xs = [x for x,_ in pts]
ys = [y for _,y in pts]

plt.figure()
plt.plot(xs, ys, marker="o")
plt.xlabel("Protected Cap (%)")
plt.ylabel("Peak DT (%)")
plt.title("EDE: Peak DT vs Protected Cap")
plt.grid(True, alpha=0.3)
os.makedirs("figures", exist_ok=True)
plt.tight_layout()
plt.savefig("figures/figure6.pdf")
print("Wrote figures/figure6.pdf")
