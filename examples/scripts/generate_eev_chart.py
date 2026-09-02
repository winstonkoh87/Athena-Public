"""
Protocol 330: EEV Three-Line Model Visualization
Generates the Economic Expected Value chart for the TOTO CS-A case study.

UEV is anchored to Singapore Pools' TOTO system entry pricing structure:
  $1 (Ordinary) → $7 (Sys7) → $28 (Sys8) → $84 (Sys9) → $210 (Sys10)

Key design choices:
  - UEV peaks at $1 (the dream acquisition point)
  - UEV gently declines $1→$28 (casual flutter zone)
  - UEV drops sharply $28→$84 (anxiety accelerates)
  - UEV = 0 at $84 (System 9 — zero utility threshold)
  - UEV goes deeply negative beyond $84 (addiction territory)
  - EEV = MEV + UEV; the Limit Point is where EEV = 0

Calibration: Median SG earner ($5,500/mth). The UEV curve shape
would be vastly flatter for high-net-worth individuals (Bill Gates,
Elon Musk) whose utility function is concave at all lottery-relevant levels.

Usage:
    python3 generate_eev_chart.py

Output:
    Saves to: examples/protocols/decision/eev_three_line_model.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import PchipInterpolator

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

OUTPUT_DIR = Path(__file__).parent
HOUSE_EDGE = 0.46  # 46% house edge (only 54% enters prize pool)
MAX_SPEND = 130  # X-axis max (show full UEV negative territory)

# ═══════════════════════════════════════════════════════════════
# UEV Control Points — Anchored to TOTO System Entry Pricing
# ═══════════════════════════════════════════════════════════════
#
# Each control point is justified by behavioral economics:
#
# $0:   No ticket → no utility. Baseline.
# $1:   PEAK. $1 Ordinary entry. The dream is acquired.
#       $1 → $12M. Maximum psychological utility per dollar.
#       For a $5.5K/mth earner, $1 = 0.018% of income. Invisible.
#       Utility value: ~$12 (the fantasy premium).
#
# $7:   System 7. Still cheap (1 hawker meal). 7 entries.
#       Marginally more probability, but the dream was already
#       acquired at $1. Minor extra hope. UEV ≈ $10.
#
# $28:  System 8. Cost of a family hawker dinner. 28 entries.
#       0.5% of monthly income. End of the "casual flutter" zone.
#       You start to NOTICE the money. UEV ≈ $5.
#       INFLECTION POINT: decline accelerates sharply from here.
#
# $44:  System Roll. Almost a day's wages for many workers.
#       0.8% of monthly income. The fun is being overtaken by
#       "I really shouldn't." UEV ≈ $2.
#
# $84:  System 9. 84 entries. 1.5% of monthly income.
#       UEV = 0. The fantasy premium has been FULLY consumed
#       by financial anxiety. The zero-utility boundary.
#       Singapore Pools' pricing here acts as a psychological
#       Schelling point — beyond this, you're gambling, not playing.
#
# $120: Deep negative. Monthly spend of $120/draw × 8 draws =
#       $960/mth = 17.5% of income. Guilt, shame, hiding from spouse.
#
# $210: System 10. 3.8% of monthly income PER DRAW.
#       Addiction territory. Genuine financial destruction.

uev_x = np.array([0, 1, 7, 28, 44, 84, 120, 210])
uev_y = np.array([0, 12, 10, 5, 2, 0, -15, -40])

# PCHIP (Piecewise Cubic Hermite Interpolating Polynomial)
# — monotone-preserving, no overshoot, smooth C1 curve
uev_spline = PchipInterpolator(uev_x, uev_y)

# ═══════════════════════════════════════════════════════════════
# Mathematical Models
# ═══════════════════════════════════════════════════════════════

x = np.linspace(0.01, MAX_SPEND, 1000)

# MEV: Mathematical Expected Value (linear negative slope)
mev = -HOUSE_EDGE * x

# UEV: Utility Expected Value (spline through control points)
uev = uev_spline(x)

# EEV: Economic Expected Value (the combined GTO metric)
eev = mev + uev

# ═══════════════════════════════════════════════════════════════
# Find Key Crossings
# ═══════════════════════════════════════════════════════════════

# EEV = 0 (Limit Point)
eev_zero_idx = np.argmin(np.abs(eev))
limit_point = x[eev_zero_idx]

# UEV = 0 (Utility Zero Crossing)
# Search after the peak region (skip first 100 points)
uev_search = uev[100:]
uev_zero_idx = np.argmin(np.abs(uev_search)) + 100
uev_zero_x = x[uev_zero_idx]

# UEV peak
uev_peak_idx = np.argmax(uev)
uev_peak_x = x[uev_peak_idx]
uev_peak_val = uev[uev_peak_idx]

# ═══════════════════════════════════════════════════════════════
# Plotting
# ═══════════════════════════════════════════════════════════════

plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(16, 9))

# --- Three Lines ---
ax.plot(
    x,
    mev,
    color="#FF4444",
    linewidth=2.5,
    label="MEV (Math Expected Value)",
    linestyle="--",
    alpha=0.85,
)
ax.plot(
    x,
    uev,
    color="#44AAFF",
    linewidth=2.5,
    label="UEV (Utility Expected Value)",
    linestyle="-.",
    alpha=0.85,
)
ax.plot(
    x,
    eev,
    color="#00FF88",
    linewidth=3.5,
    label="EEV (Economic Expected Value)",
    zorder=5,
)

# --- Zero line ---
ax.axhline(y=0, color="white", linewidth=0.8, linestyle="-", alpha=0.4)

# --- Fill regions ---
ax.fill_between(
    x,
    eev,
    0,
    where=(eev > 0),
    color="#00FF88",
    alpha=0.10,
    label="Rational Zone (EEV > 0)",
)
ax.fill_between(
    x,
    eev,
    0,
    where=(eev < 0),
    color="#FF4444",
    alpha=0.10,
    label="Wealth Destruction (EEV < 0)",
)

# --- TOTO System Entry vertical markers ---
toto_costs = [1, 7, 28, 44, 84]
toto_labels = ["$1\nOrdinary", "$7\nSys7", "$28\nSys8", "$44\nRoll", "$84\nSys9"]
for cost, label in zip(toto_costs, toto_labels):
    ax.axvline(x=cost, color="#555555", linewidth=0.8, linestyle=":", alpha=0.5)

# --- Limit Point marker (EEV = 0) ---
ax.plot(
    limit_point,
    0,
    "o",
    color="#FFD700",
    markersize=14,
    zorder=10,
    markeredgecolor="white",
    markeredgewidth=2,
)

ax.annotate(
    f"LIMIT POINT\nEEV = 0 at ${limit_point:.0f}",
    xy=(limit_point, 0),
    xytext=(limit_point + 12, 5),
    fontsize=13,
    fontweight="bold",
    color="#FFD700",
    arrowprops=dict(
        facecolor="#FFD700", edgecolor="#FFD700", shrink=0.05, width=2, headwidth=10
    ),
    bbox=dict(boxstyle="round,pad=0.5", fc="black", ec="#FFD700", lw=2, alpha=0.9),
)

# --- UEV Zero Crossing marker (UEV = 0 at $84) ---
ax.plot(
    uev_zero_x,
    0,
    "D",
    color="#44AAFF",
    markersize=10,
    zorder=10,
    markeredgecolor="white",
    markeredgewidth=1.5,
)

ax.annotate(
    f"UEV = 0\n(${uev_zero_x:.0f})",
    xy=(uev_zero_x, 0),
    xytext=(uev_zero_x + 8, 4),
    fontsize=10,
    fontweight="bold",
    color="#44AAFF",
    arrowprops=dict(
        facecolor="#44AAFF", edgecolor="#44AAFF", shrink=0.05, width=1.5, headwidth=8
    ),
    bbox=dict(boxstyle="round,pad=0.4", fc="black", ec="#44AAFF", lw=1.5, alpha=0.9),
)

# --- Phase annotations ---
# Phase 1: The Spike (peak at ~$1)
ax.annotate(
    "Phase 1: THE SPIKE\n(dy/dx = 0, Max Utility)",
    xy=(uev_peak_x, uev_peak_val),
    xytext=(8, uev_peak_val + 3),
    fontsize=9,
    color="#44AAFF",
    alpha=0.9,
    arrowprops=dict(
        facecolor="#44AAFF", edgecolor="#44AAFF", shrink=0.05, width=1, headwidth=6
    ),
    bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="#44AAFF", lw=1.5, alpha=0.8),
)

# Phase 2: Slow Decay ($1→$28)
ax.annotate(
    "Phase 2: SLOW DECAY\n($1 to $28 — Casual Flutter)",
    xy=(15, float(uev_spline(15))),
    xytext=(25, float(uev_spline(15)) + 5),
    fontsize=9,
    color="#88CCFF",
    alpha=0.9,
    arrowprops=dict(
        facecolor="#88CCFF", edgecolor="#88CCFF", shrink=0.05, width=1, headwidth=6
    ),
    bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="#88CCFF", lw=1.5, alpha=0.8),
)

# Phase 3: The Crash ($28→$84+)
crash_x = 60
crash_uev = float(uev_spline(crash_x))
ax.annotate(
    "Phase 3: THE CRASH\n(Anxiety overtakes fantasy)",
    xy=(crash_x, crash_uev),
    xytext=(crash_x + 15, crash_uev + 6),
    fontsize=9,
    color="#FF6666",
    alpha=0.9,
    arrowprops=dict(
        facecolor="#FF6666", edgecolor="#FF6666", shrink=0.05, width=1, headwidth=6
    ),
    bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="#FF6666", lw=1.5, alpha=0.8),
)

# --- Zone labels ---
ax.text(
    6,
    5.5,
    "RATIONAL",
    fontsize=14,
    fontweight="bold",
    color="#00FF88",
    alpha=0.6,
    ha="center",
)
ax.text(
    90,
    -25,
    "WEALTH\nDESTRUCTION",
    fontsize=14,
    fontweight="bold",
    color="#FF4444",
    alpha=0.6,
    ha="center",
)
ax.text(
    105,
    -8,
    "ADDICTION\nTERRITORY",
    fontsize=11,
    fontweight="bold",
    color="#FF6666",
    alpha=0.4,
    ha="center",
    fontstyle="italic",
)

# --- Title and labels ---
ax.set_title(
    "Protocol 330: The EEV Three-Line Model\n"
    r"Singapore TOTO \$12M Draw — CS-A (Median SG Earner, \$5.5K/mth)",
    fontsize=16,
    fontweight="bold",
    color="white",
    pad=20,
)
ax.set_xlabel(
    "Total Spend on Lottery Tickets ($)", fontsize=13, color="#AAAAAA", labelpad=10
)
ax.set_ylabel("Expected Value ($/draw)", fontsize=13, color="#AAAAAA", labelpad=10)

# --- Legend ---
legend = ax.legend(
    loc="lower left", fontsize=10, framealpha=0.8, edgecolor="#555555", fancybox=True
)
legend.get_frame().set_facecolor("black")

# --- Grid ---
ax.grid(True, alpha=0.15, linestyle="--")
ax.set_xlim(0, MAX_SPEND)
y_min = min(float(np.min(eev)), float(np.min(uev))) - 5
ax.set_ylim(y_min, uev_peak_val + 8)

# --- X-axis markers (anchored to TOTO pricing) ---
ax.set_xticks([0, 1, 7, 16, 28, 44, 84, 120])
ax.set_xticklabels(
    ["$0", "$1", "$7", "$16", "$28", "$44", "$84", "$120"], fontsize=10, color="white"
)

# ═══════════════════════════════════════════════════════════════
# Save
# ═══════════════════════════════════════════════════════════════

output_path = OUTPUT_DIR.parent / "protocols" / "decision" / "eev_three_line_model.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="black")
plt.close()

# ═══════════════════════════════════════════════════════════════
# Output Diagnostics
# ═══════════════════════════════════════════════════════════════

print(f"EEV Three-Line Model saved to: {output_path}")
print("")
print("=== Key Values ===")
print(f"  UEV peak:       ${uev_peak_val:.2f} at ${uev_peak_x:.1f}")
print(f"  UEV = 0:        ${uev_zero_x:.0f} (System 9 boundary)")
print(f"  EEV = 0:        ${limit_point:.1f} (LIMIT POINT)")
print(f"  MEV at limit:   ${mev[eev_zero_idx]:.2f}")
print(f"  UEV at limit:   ${uev[eev_zero_idx]:.2f}")
print("")
print("=== Diagnostics at TOTO Price Points ===")
for cost, label in [
    (1, "Ordinary"),
    (7, "Sys7"),
    (28, "Sys8"),
    (44, "Roll"),
    (84, "Sys9"),
    (210, "Sys10"),
]:
    if cost <= MAX_SPEND:
        u = float(uev_spline(cost))
        m = -HOUSE_EDGE * cost
        e = m + u
        print(
            f"  ${cost:>3} ({label:>8}):  MEV=${m:>7.2f}  UEV=${u:>7.2f}  EEV=${e:>7.2f}"
        )
    else:
        u = float(uev_spline(cost))
        m = -HOUSE_EDGE * cost
        e = m + u
        print(
            f"  ${cost:>3} ({label:>8}):  MEV=${m:>7.2f}  UEV=${u:>7.2f}  EEV=${e:>7.2f}  [off chart]"
        )
