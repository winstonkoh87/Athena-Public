import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

# Define the domain
x = np.linspace(-600, 1200, 1000)

# Construct the Multimodal Distribution (The "Barbell")
# Weights
w1, w2, w3 = 0.10, 0.70, 0.20

# Distributions
dist1 = stats.norm.pdf(x, -500, 40)  # Sharp peak at -500 (Risk)
dist2 = stats.norm.pdf(x, 50, 150)  # Wide bell at +50 (Income)
dist3 = stats.norm.pdf(x, 1000, 180)  # Tapering tail at +1000 (Jackpot)

# Combined PDF
y = (w1 * dist1) + (w2 * dist2) + (w3 * dist3)

# Plotting
plt.figure(figsize=(12, 7))
plt.style.use("dark_background")

# Plot the curve
plt.plot(
    x, y, color="#00FFFF", linewidth=3, label="PnL Probability Density"
)  # Cyan Neon

# Fill areas with gradient-like transparency
plt.fill_between(x, y, where=(x < -200), color="#FF3333", alpha=0.4)  # Red
plt.fill_between(
    x, y, where=((x >= -200) & (x < 400)), color="#33FF33", alpha=0.4
)  # Green
plt.fill_between(x, y, where=(x >= 400), color="#FFD700", alpha=0.4)  # Gold


# Custom Annotation Helper
def add_premium_label(text, xy, xytext, color):
    plt.annotate(
        text,
        xy=xy,
        xytext=xytext,
        arrowprops=dict(
            facecolor=color, edgecolor=color, shrink=0.05, width=1.5, headwidth=8
        ),
        ha="center",
        va="center",
        color="white",
        weight="bold",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.4", fc="black", ec=color, lw=2, alpha=0.9),
    )


# 1. Tail Risk Annotation
add_premium_label(
    "THE PUNISHMENT BOX\n(Risk of Ruin: -$500)",
    xy=(-500, 0.001),
    xytext=(-500, 0.0035),
    color="#FF3333",
)

# 2. Base Income Annotation
add_premium_label(
    "THE INCOME ZONE\n(Base Case: +$50)",
    xy=(50, 0.0028),
    xytext=(50, 0.0055),
    color="#33FF33",
)

# 3. Jackpot Annotation
add_premium_label(
    "THE BLACK SWAN\n(Jackpot: +$1000)",
    xy=(1000, 0.0008),
    xytext=(1000, 0.0035),
    color="#FFD700",
)

# EV Line
plt.axvline(185, color="white", linestyle="--", linewidth=2, alpha=0.8)
plt.text(
    195,
    0.0045,
    "EXPECTED VALUE\n(+$185 per Trade)",
    color="white",
    fontsize=12,
    fontweight="bold",
)

# Labels and Title
plt.title(
    'EURAUD Short Strategy: The "Python Snake" Distribution',
    fontsize=18,
    color="white",
    weight="bold",
    pad=20,
)
plt.xlabel("PnL (USD)", fontsize=14, color="#AAAAAA")
plt.yticks([])  # Hide y-axis numbers for cleanliness
plt.grid(True, alpha=0.15, linestyle="--")

# X-Axis Styling
plt.xticks(
    [-500, 0, 185, 1000], ["-$500", "$0", "+$185", "+$1000"], fontsize=12, color="white"
)

# Save directly to target folder
output_path = (
    "/Users/[AUTHOR]/Desktop/FX Trading/Feb 2026/euraud_distribution_analytic.png"
)
plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="black")
print(f"Distribution curve generated at: {output_path}")
