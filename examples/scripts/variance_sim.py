import numpy as np


def simulate_paths(
    win_rate, payout, risk_per_bet, n_sims=1000, n_flips=1000, start_bankroll=10000
):
    results = []
    ruined_count = 0
    drawdown_50_count = 0

    # Bet size is fixed dollar amount for this comparison to isolate variance effect on a fixed strategy
    bet_size = 100

    # Alternatively, use fixed fractional betting to show volatility drag on growth
    # But user asked about "operator" getting screwed, usually fixed unit or fixed %
    # Let's use fixed units as per the user's "$100 bet" setup.

    ends = []
    max_drawdowns = []

    for _ in range(n_sims):
        balance = start_bankroll
        peak = start_bankroll
        max_dd = 0

        # Fast simulation
        # Generate all flips at once: 1 = win, 0 = loss
        # This is an approximation using binomial
        wins = np.random.binomial(1, win_rate, n_flips)

        path = [balance]
        for w in wins:
            if w == 1:
                balance += bet_size * payout
            else:
                balance -= bet_size

            if balance > peak:
                peak = balance

            dd = (peak - balance) / peak
            if dd > max_dd:
                max_dd = dd

            if balance <= 0:
                break

        ends.append(balance)
        max_drawdowns.append(max_dd)

    return {
        "median_end": np.median(ends),
        "mean_end": np.mean(ends),
        "ruin_prob": sum(1 for x in ends if x <= 0) / n_sims,
        "dd_50_prob": sum(1 for x in max_drawdowns if x >= 0.5) / n_sims,
        "max_drawdown_avg": np.mean(max_drawdowns),
    }


# Scenario 1: The Grinder (1:1, 55% WR)
stats_1 = simulate_paths(0.55, 1.0, 100)

# Scenario 2: The Longshot (1:5, 18.33% WR)
stats_5 = simulate_paths(0.1833, 5.0, 100)

print("| Metric | 1:1 Grinder (55% WR) | 1:5 Longshot (18.3% WR) |")
print("| :--- | :--- | :--- |")
print("| **EV per bet** | +$10 | +$10 |")
print(
    f"| **Median Balance** | ${stats_1['median_end']:,.0f} | ${stats_5['median_end']:,.0f} |"
)
print(
    f"| **Risk of Ruin** | {stats_1['ruin_prob'] * 100:.1f}% | {stats_5['ruin_prob'] * 100:.1f}% |"
)
print(
    f"| **Chance of >50% Drawdown** | {stats_1['dd_50_prob'] * 100:.1f}% | {stats_5['dd_50_prob'] * 100:.1f}% |"
)
print(
    f"| **Avg Max Drawdown** | {stats_1['max_drawdown_avg'] * 100:.1f}% | {stats_5['max_drawdown_avg'] * 100:.1f}% |"
)
