import math
import random


def calculate_ror_analytical(win_rate, payoff_ratio, risk_per_trade_percent):
    """
    Calculates Risk of Ruin closer to analytical methods.
    Using the formula for RoR = ((1 - W) / (W * (1 + R))) ^ (Capital / RiskUnit)
    This is for 1:1 payout. For asymmetric, we use the Kelly approximation or simulation.

    Let's using a quick simulation for accuracy with asymmetric payoff (0.5 R:R).
    """
    pass


def run_simulation(
    capital,
    risk_amt,
    win_rate,
    payoff,
    simulations=10000,
    max_trades=1000,
    ruin_threshold=0.2,
):
    ruin_count = 0
    final_capitals = []

    # Ruin threshold at 20% of capital (psychological break point) or 0?
    # PDF said "Active Ruin", usually means hitting 0 or a stop level.
    # Let's assume 0 for "Mathematical Ruin" but note the 65% drawdown.

    cutoff = capital * 0.01  # Effectively zero

    for i in range(simulations):
        cap = capital
        peak = capital
        ruined = False
        for _ in range(max_trades):
            if random.random() < win_rate:
                cap += risk_amt * payoff
            else:
                cap -= risk_amt

            if cap <= cutoff:
                ruined = True
                break

        if ruined:
            ruin_count += 1
        final_capitals.append(cap)

    return (ruin_count / simulations) * 100


print(
    f"{'Scenario':<40} | {'WinRate':<8} | {'Payoff':<6} | {'BetSize':<8} | {'RoR (Est)':<10}"
)
print("-" * 85)

# 1. Baseline
ror_base = run_simulation(10000, 500, 0.70, 0.50)
print(
    f"{'Baseline ($10k, $500, 70% WR, 0.5 RR)':<40} | {'70%':<8} | {'0.5':<6} | {'$500':<8} | {ror_base:.2f}%"
)

# 2. Increase WR to 75%
ror_wr75 = run_simulation(10000, 500, 0.75, 0.50)
print(
    f"{'Increase WR ($10k, $500, 75% WR)':<40} | {'75%':<8} | {'0.5':<6} | {'$500':<8} | {ror_wr75:.2f}%"
)

# 3. Increase WR to 80%
ror_wr80 = run_simulation(10000, 500, 0.80, 0.50)
print(
    f"{'Increase WR ($10k, $500, 80% WR)':<40} | {'80%':<8} | {'0.5':<6} | {'$500':<8} | {ror_wr80:.2f}%"
)

# 4. Improve Payoff to 0.7 (holding 70% WR)
ror_rr07 = run_simulation(10000, 500, 0.70, 0.70)
print(
    f"{'Improve R:R ($10k, $500, 0.7 RR)':<40} | {'70%':<8} | {'0.7':<6} | {'$500':<8} | {ror_rr07:.2f}%"
)

# 5. Reduce Size to $250
ror_size250 = run_simulation(10000, 250, 0.70, 0.50)
print(
    f"{'Reduce Size ($10k, $250, 70% WR)':<40} | {'70%':<8} | {'0.5':<6} | {'$250':<8} | {ror_size250:.2f}%"
)

# 6. Reduce Size to $200
ror_size200 = run_simulation(10000, 200, 0.70, 0.50)
print(
    f"{'Reduce Size ($10k, $200, 70% WR)':<40} | {'70%':<8} | {'0.5':<6} | {'$200':<8} | {ror_size200:.2f}%"
)
