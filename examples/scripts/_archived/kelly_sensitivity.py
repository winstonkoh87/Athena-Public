
import numpy as np


def calculate_kelly(b, p):
    """
    b: net odds (payoff)
    p: probability of winning
    q: probability of losing (1-p)
    f* = (bp - q) / b
    """
    q = 1 - p
    f_star = (b * p - q) / b
    return max(0, f_star) # No negative betting

def run_analysis():
    # Scenario 1: Fixed Win Rate (55%), Varying RR
    # This shows how increasing the payout with the same accuracy explodes the edge.
    rr_values = np.linspace(0.5, 5.0, 10)

    print("### Scenario A: Fixed Win Rate (55%) - The 'Super Coin'")
    print("| R:R | Win Rate | Kelly (Full) | Kelly (Half) | Bankroll (Half) | EV |")
    print("|---|---|---|---|---|---|")

    for b in rr_values:
        p = 0.55
        f = calculate_kelly(b, p)
        f_half = f / 2
        bankroll = 100 / f_half if f_half > 0 else float('inf')
        ev = (b * p) - (1 - p)

        bankroll_str = f"${bankroll:,.0f}" if bankroll != float('inf') else "∞ (Don't Bet)"
        print(f"| 1:{b:.1f} | {p*100:.0f}% | {f*100:.1f}% | {f_half*100:.1f}% | {bankroll_str} | {ev*100:.1f}% |")

    print("\n")

    # Scenario B: Fixed EV (10%), Varying RR
    # This shows the "Sniper vs Tank" trade-off.
    # To keep EV constant at 0.10, P must change as B changes.
    # EV = p(b) - q(1) = 0.1
    # pb - 1 + p = 0.1
    # p(b+1) = 1.1
    # p = 1.1 / (b+1)

    print("### Scenario B: Fixed EV (10%) - Structural Trade-off")
    print("This compares different ways to achieve the SAME 10% edge.")
    print("| R:R | Req. Win Rate | Kelly (Full) | Kelly (Half) | Bankroll (Half) | Variance (Risk) |")
    print("|---|---|---|---|---|---|")

    for b in rr_values:
        p = 1.1 / (b + 1)
        if p > 1: continue # Impossible

        f = calculate_kelly(b, p)
        f_half = f / 2
        bankroll = 100 / f_half if f_half > 0 else float('inf')

        # Variance of a single bet outcome (Bernoulli variance scaled)
        # Var = E[X^2] - (E[X])^2
        # X is b with prob p, -1 with prob q
        # E[X] = 0.1
        # E[X^2] = p(b^2) + q((-1)^2) = p*b^2 + q
        var = (p * b**2 + (1-p)) - (0.1**2)
        std_dev = np.sqrt(var)

        bankroll_str = f"${bankroll:,.0f}" if bankroll != float('inf') else "∞"
        print(f"| 1:{b:.1f} | {p*100:.1f}% | {f*100:.1f}% | {f_half*100:.1f}% | {bankroll_str} | {std_dev:.2f} |")

if __name__ == "__main__":
    run_analysis()
