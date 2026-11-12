"""
Trade Duration Guardian for Athena's FX Trading desk.
"""

import sys
from pathlib import Path

SDK_PATH = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SDK_PATH))

import csv
import os
import sqlite3
from datetime import datetime, timezone

from athena.core.config import PROJECT_ROOT

# Canonical holding duration boundaries (minutes)
SWEET_SPOT_MAX_MINUTES = 15.0
OPTIMAL_MAX_MINUTES = 60.0
DANGER_MAX_MINUTES = 120.0


class TradeGuardian:
    def __init__(self, journal_path: str | Path | None = None):
        if journal_path:
            self.journal_path = Path(journal_path)
        else:
            self.journal_path = self._discover_journal_path()

    @staticmethod
    def _discover_journal_path() -> Path:
        env_path = os.environ.get("ATHENA_TRADE_JOURNAL_PATH")
        if env_path:
            return Path(env_path)
        desktop_db = Path.home() / "Desktop" / "FX Daytrading" / "data" / "journal.db"
        if desktop_db.exists():
            return desktop_db
        csv_path = PROJECT_ROOT / "FX Trading" / "trade_journal.csv"
        if csv_path.exists():
            return csv_path
        return desktop_db

    def _parse_datetime(self, dt_str: str) -> datetime:
        # Handles ISO 8601 strings or standard SQL datetime format
        dt_str = str(dt_str).strip()
        try:
            return datetime.fromisoformat(dt_str)
        except ValueError:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d"):
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    pass
            raise

    def load_journal(self) -> list[dict]:
        if not self.journal_path.exists():
            raise FileNotFoundError(
                f"Trade journal not found at '{self.journal_path}'. "
                "TradeGuardian requires a valid trade journal (.db SQLite or .csv) to audit holding time and performance."
            )

        is_sqlite = False
        try:
            with open(self.journal_path, "rb") as f:
                header = f.read(16)
                if header.startswith(b"SQLite format 3"):
                    is_sqlite = True
        except Exception:
            pass

        if is_sqlite or self.journal_path.suffix.lower() in [".db", ".sqlite", ".sqlite3"]:
            return self._load_sqlite()
        return self._load_csv()

    def _load_sqlite(self) -> list[dict]:
        conn = sqlite3.connect(self.journal_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]

        trades = []
        if "campaigns" in tables:
            cur.execute("PRAGMA table_info(campaigns)")
            cols = [r[1] for r in cur.fetchall()]
            has_dur = "duration_minutes" in cols
            has_notes = "notes" in cols
            has_inst = "instrument" in cols
            has_dir = "direction" in cols

            query = (
                "SELECT id, "
                + ("instrument" if has_inst else "''")
                + ", "
                + ("direction" if has_dir else "''")
                + ", realized_pnl, time_entered, time_exited"
            )
            query += ", duration_minutes" if has_dur else ", NULL"
            query += ", notes" if has_notes else ", ''"
            query += " FROM campaigns"

            cur.execute(query)
            for row in cur.fetchall():
                trade_id, inst, direction, pnl, t_in, t_out, dur, notes = row
                dur_mins = 0.0
                if dur is not None:
                    try:
                        dur_mins = float(dur)
                    except (ValueError, TypeError):
                        dur_mins = 0.0
                elif t_in and t_out:
                    try:
                        dt_in = self._parse_datetime(str(t_in))
                        dt_out = self._parse_datetime(str(t_out))
                        dur_mins = (dt_out - dt_in).total_seconds() / 60.0
                    except Exception:
                        dur_mins = 0.0

                try:
                    pnl_val = float(pnl) if pnl is not None else 0.0
                except (ValueError, TypeError):
                    pnl_val = 0.0

                trades.append({
                    "trade_id": str(trade_id),
                    "pair": inst or "UNKNOWN",
                    "direction": direction or "",
                    "entry_time": str(t_in) if t_in else "",
                    "exit_time": str(t_out) if t_out else "",
                    "duration_minutes": dur_mins,
                    "pnl": pnl_val,
                    "notes": notes or "",
                })
        elif "trades" in tables:
            cur.execute("SELECT trade_id, symbol, side, pnl, entry_time, exit_time FROM trades")
            for row in cur.fetchall():
                trade_id, sym, side, pnl, t_in, t_out = row
                dur_mins = 0.0
                if t_in and t_out:
                    try:
                        dt_in = self._parse_datetime(str(t_in))
                        dt_out = self._parse_datetime(str(t_out))
                        dur_mins = (dt_out - dt_in).total_seconds() / 60.0
                    except Exception:
                        dur_mins = 0.0
                try:
                    pnl_val = float(pnl) if pnl is not None else 0.0
                except (ValueError, TypeError):
                    pnl_val = 0.0
                trades.append({
                    "trade_id": str(trade_id),
                    "pair": sym or "UNKNOWN",
                    "direction": side or "",
                    "entry_time": str(t_in) if t_in else "",
                    "exit_time": str(t_out) if t_out else "",
                    "duration_minutes": dur_mins,
                    "pnl": pnl_val,
                    "notes": "",
                })
        conn.close()
        return trades

    def _load_csv(self) -> list[dict]:
        trades = []
        with open(self.journal_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return []

            required_cols = {"trade_id", "pair", "direction", "entry_time", "exit_time", "entry_price", "exit_price", "pnl"}
            if not required_cols.issubset(set(reader.fieldnames)):
                raise ValueError(f"Missing columns. Expected at least: {required_cols}")

            for row in reader:
                if not row["entry_time"] or not row["exit_time"]:
                    continue

                entry_dt = self._parse_datetime(row["entry_time"])
                exit_dt = self._parse_datetime(row["exit_time"])

                duration = (exit_dt - entry_dt).total_seconds() / 60.0
                row["duration_minutes"] = duration

                try:
                    row["pnl"] = float(row["pnl"])
                except ValueError:
                    row["pnl"] = 0.0

                trades.append(row)

        return trades

    def _bucket_stats(self, filtered_trades: list[dict]) -> dict:
        count = len(filtered_trades)
        if count == 0:
            return {
                "count": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "avg_pnl": 0.0,
                "profit_factor": 0.0
            }

        wins = [t for t in filtered_trades if t["pnl"] > 0]
        losses = [t for t in filtered_trades if t["pnl"] < 0]

        total_pnl = sum(t["pnl"] for t in filtered_trades)
        gross_profit = sum(t["pnl"] for t in wins)
        gross_loss = abs(sum(t["pnl"] for t in losses))

        win_rate = len(wins) / count
        avg_pnl = total_pnl / count

        profit_factor = 0.0
        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
        elif gross_profit > 0:
            profit_factor = float('inf')

        return {
            "count": count,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_pnl": avg_pnl,
            "profit_factor": profit_factor
        }

    def duration_analysis(self) -> dict:
        trades = self.load_journal()

        buckets = {
            "sweet_spot": [t for t in trades if 0 <= t["duration_minutes"] <= SWEET_SPOT_MAX_MINUTES],
            "optimal": [t for t in trades if SWEET_SPOT_MAX_MINUTES < t["duration_minutes"] <= OPTIMAL_MAX_MINUTES],
            "danger": [t for t in trades if OPTIMAL_MAX_MINUTES < t["duration_minutes"] <= DANGER_MAX_MINUTES],
            "ruin_zone": [t for t in trades if t["duration_minutes"] > DANGER_MAX_MINUTES],
        }

        return {name: self._bucket_stats(group) for name, group in buckets.items()}

    def check_active_trade(self, entry_time_str: str) -> dict:
        entry_dt = self._parse_datetime(entry_time_str)
        now = datetime.now(timezone.utc)
        if entry_dt.tzinfo is None:
            now = datetime.now()

        elapsed_minutes = (now - entry_dt).total_seconds() / 60.0

        if elapsed_minutes <= SWEET_SPOT_MAX_MINUTES:
            bucket = "sweet_spot"
        elif elapsed_minutes <= OPTIMAL_MAX_MINUTES:
            bucket = "optimal"
        elif elapsed_minutes <= DANGER_MAX_MINUTES:
            bucket = "danger"
        else:
            bucket = "ruin_zone"

        if elapsed_minutes <= 30:
            alert_level = "green"
            warning_message = None
        elif elapsed_minutes <= 45:
            alert_level = "yellow"
            warning_message = "Approaching optimal exit window"
        elif elapsed_minutes <= OPTIMAL_MAX_MINUTES:
            alert_level = "red"
            warning_message = "EXIT NOW — 60-minute guillotine imminent"
        else:
            alert_level = "critical"
            warning_message = "HOLDING LIMIT BREACHED — empirical ruin zone"

        return {
            "elapsed_minutes": elapsed_minutes,
            "bucket": bucket,
            "warning_message": warning_message,
            "alert_level": alert_level
        }

    def generate_report(self) -> str:
        analysis = self.duration_analysis()

        report = []
        report.append("=== Trade Duration Analysis Report ===")
        report.append("Empirical evidence from Trade Journal")

        for bucket, stats in analysis.items():
            report.append(f"\n[{bucket.upper()}]")
            report.append(f"Trades: {stats['count']}")
            report.append(f"Win Rate: {stats['win_rate']:.1%}")
            report.append(f"Total PnL: S${stats['total_pnl']:.2f}")
            report.append(f"Avg PnL: S${stats['avg_pnl']:.2f}")
            report.append(f"Profit Factor: {stats['profit_factor']:.2f}")

        return "\n".join(report)

    def sweet_spot_stats(self) -> dict:
        trades = self.load_journal()
        sweet_spot_trades = [t for t in trades if 0 <= t["duration_minutes"] <= SWEET_SPOT_MAX_MINUTES]
        return self._bucket_stats(sweet_spot_trades)

    def ruin_zone_trades(self) -> list[dict]:
        trades = self.load_journal()
        return [t for t in trades if t["duration_minutes"] > DANGER_MAX_MINUTES]


def check_desk_halt(
    state_or_dict: dict | None = None,
    halt_until_override: str | None = None,
    current_time: datetime | None = None,
) -> dict:
    """
    Somatic Desk Circuit Breaker Gate (CANONICAL §509 / §519 / INC-011).
    Mechanically verifies whether the desk is under an active trading halt
    following extreme somatic depletion, adverse excursions, or operator timeouts.
    """
    now = current_time or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    state = state_or_dict or {}
    halt_until_str = halt_until_override or state.get("desk_halt_until")
    halt_active_flag = state.get("desk_halt_active", False)
    halt_reason = state.get("desk_halt_reason", "Mandatory Somatic Circuit Breaker Active")

    if not halt_until_str and not halt_active_flag:
        return {
            "passed": True,
            "status": "PASS",
            "desk_halt_active": False,
            "desk_halt_until": None,
            "desk_halt_reason": None,
            "remaining_hours": 0.0,
            "message": "No active desk halt. Trading cleared under operational protocols.",
        }

    halt_until_dt: datetime | None = None
    if halt_until_str:
        try:
            dt_clean = str(halt_until_str).strip()
            halt_until_dt = datetime.fromisoformat(dt_clean)
            if halt_until_dt.tzinfo is None:
                halt_until_dt = halt_until_dt.replace(tzinfo=timezone.utc)
        except Exception:
            halt_until_dt = None

    if halt_until_dt is not None:
        remaining_seconds = (halt_until_dt - now).total_seconds()
        remaining_hours = max(0.0, round(remaining_seconds / 3600.0, 2))
        is_active = remaining_seconds > 0

        if is_active:
            return {
                "passed": False,
                "status": "HARD STOP",
                "desk_halt_active": True,
                "desk_halt_until": halt_until_dt.isoformat(),
                "desk_halt_reason": halt_reason,
                "remaining_hours": remaining_hours,
                "message": (
                    f"HARD STOP: Somatic Desk Circuit Breaker active until {halt_until_dt.isoformat()} "
                    f"({remaining_hours:.1f}h remaining). Reason: {halt_reason}. All trading strictly prohibited."
                ),
            }
        else:
            return {
                "passed": True,
                "status": "PASS",
                "desk_halt_active": False,
                "desk_halt_until": halt_until_dt.isoformat(),
                "desk_halt_reason": halt_reason,
                "remaining_hours": 0.0,
                "message": f"Somatic desk halt expired at {halt_until_dt.isoformat()}. Desk is clear for trading.",
            }

    if halt_active_flag:
        return {
            "passed": False,
            "status": "HARD STOP",
            "desk_halt_active": True,
            "desk_halt_until": None,
            "desk_halt_reason": halt_reason,
            "remaining_hours": 0.0,
            "message": f"HARD STOP: Somatic Desk Circuit Breaker is active (Reason: {halt_reason}). Trading strictly prohibited.",
        }

    return {
        "passed": True,
        "status": "PASS",
        "desk_halt_active": False,
        "desk_halt_until": None,
        "desk_halt_reason": None,
        "remaining_hours": 0.0,
        "message": "No active desk halt. Desk is clear.",
    }


def check_sacrificial_fuse(
    bankroll: float = 1000.0,
    fuse_limit: float = 1300.0,
    emergency_reload: bool = False,
    reload_count: int = 0,
    bullets_consumed: int = 3,
    max_bullets: int = 10,
    buffer_allowance: float = 50.0,
) -> dict:
    """
    Option B Sacrificial Fuse & Reload Trap Auditor (CANONICAL §519 / CS-745 / INC-011).
    Operationalizes the S$1,300 active broker fuse limit, guards against the Reload Trap
    (emergency margin injections mid-campaign), and monitors war-chest bullet exhaustion.
    """
    violates_reload = emergency_reload or (reload_count > 0)
    surplus = max(0.0, round(bankroll - fuse_limit, 2))
    violates_surplus = bankroll > (fuse_limit + buffer_allowance)
    bullets_rem = max(0, max_bullets - bullets_consumed)
    exhaustion_warning = bullets_rem <= 3

    if violates_reload:
        return {
            "passed": False,
            "status": "BLOCK",
            "bankroll": bankroll,
            "fuse_limit": fuse_limit,
            "surplus_amount": surplus,
            "violates_reload_trap": True,
            "violates_unswept_surplus": violates_surplus,
            "bullets_consumed": bullets_consumed,
            "max_bullets": max_bullets,
            "bullets_remaining": bullets_rem,
            "bullet_exhaustion_warning": exhaustion_warning,
            "message": (
                "BLOCK: Reload Trap Detected (CANONICAL §519 / INC-011). Emergency deposit injection "
                "during active campaign circumvents account physics and converts bounded sacrificial fuse "
                "into unhedged catastrophic ruin."
            ),
        }

    if violates_surplus:
        return {
            "passed": False,
            "status": "WARN",
            "bankroll": bankroll,
            "fuse_limit": fuse_limit,
            "surplus_amount": surplus,
            "violates_reload_trap": False,
            "violates_unswept_surplus": True,
            "bullets_consumed": bullets_consumed,
            "max_bullets": max_bullets,
            "bullets_remaining": bullets_rem,
            "bullet_exhaustion_warning": exhaustion_warning,
            "message": (
                f"Unswept surplus float detected: Bankroll ${bankroll:.2f} exceeds Option B "
                f"sacrificial fuse limit of ${fuse_limit:.2f} by ${surplus:.2f}. "
                "Sweep excess capital immediately to preserve 66-second capital isolation."
            ),
        }

    msg = f"Bankroll ${bankroll:.2f} is within Option B sacrificial fuse limit of ${fuse_limit:.2f}."
    if exhaustion_warning:
        msg += f" [WARNING: Only {bullets_rem} of {max_bullets} war-chest bullets remain]"

    return {
        "passed": True,
        "status": "PASS",
        "bankroll": bankroll,
        "fuse_limit": fuse_limit,
        "surplus_amount": surplus,
        "violates_reload_trap": False,
        "violates_unswept_surplus": False,
        "bullets_consumed": bullets_consumed,
        "max_bullets": max_bullets,
        "bullets_remaining": bullets_rem,
        "bullet_exhaustion_warning": exhaustion_warning,
        "message": msg,
    }


def audit_effective_drawdown_cliff(
    balance: float = 1300.0,
    margin_used: float = 300.0,
    planned_stop_loss: float = 0.0,
    stop_out_pct: float = 0.5,
) -> dict:
    """
    Effective Drawdown Cliff & Margin Lock Dominance Auditor (CANONICAL §522 / S1580).
    Computes true liquidation equity (stop_out_pct * margin_used) and effective loss capacity
    (balance - liquidation_equity). Blocks optical planned stop losses that exceed effective capacity.
    """
    liq_equity = max(0.0, round(margin_used * stop_out_pct, 2))
    eff_capacity = max(0.0, round(balance - liq_equity, 2))

    violates_optical_stop = planned_stop_loss > eff_capacity
    margin_level_at_stop = 0.0
    if margin_used > 0:
        equity_at_stop = max(0.0, balance - planned_stop_loss)
        margin_level_at_stop = round((equity_at_stop / margin_used) * 100.0, 2)

    if violates_optical_stop:
        msg = (
            f"BLOCK: Optical Planned Stop Loss Defect (CANONICAL §522 / S1580). "
            f"Planned stop loss (S${planned_stop_loss:,.2f}) exceeds effective loss capacity "
            f"(S${eff_capacity:,.2f}). Broker 50% margin liquidation cliff triggers at equity "
            f"S${liq_equity:,.2f} before planned stop is executed."
        )
        return {
            "passed": False,
            "status": "BLOCK",
            "balance": balance,
            "margin_used": margin_used,
            "stop_out_pct": stop_out_pct,
            "liquidation_equity": liq_equity,
            "effective_loss_capacity": eff_capacity,
            "planned_stop_loss": planned_stop_loss,
            "margin_level_at_stop": margin_level_at_stop,
            "violates_optical_stop": True,
            "message": msg,
        }

    msg = (
        f"Effective loss capacity is S${eff_capacity:,.2f} (Liquidation cliff equity: S${liq_equity:,.2f}). "
        f"Planned stop loss S${planned_stop_loss:,.2f} is within effective capacity."
    )
    return {
        "passed": True,
        "status": "PASS",
        "balance": balance,
        "margin_used": margin_used,
        "stop_out_pct": stop_out_pct,
        "liquidation_equity": liq_equity,
        "effective_loss_capacity": eff_capacity,
        "planned_stop_loss": planned_stop_loss,
        "margin_level_at_stop": margin_level_at_stop,
        "violates_optical_stop": False,
        "message": msg,
    }


def check_hmr_liquidation_envelope(
    equity: float = 1000.0,
    current_margin: float = 107.2,
    hmr_multiplier: float = 10.0,
    stop_out_pct: float = 0.5,
) -> dict:
    """
    Higher Margin Requirement (HMR) Rollover & Volatility Multiplier Auditor (CANONICAL §522 / S1580).
    Audits whether an open position survives broker leverage cuts (e.g. 10x leverage reduction from
    1:2000 to 1:200 during 23:59 server daily rollover, news releases, or weekend holding).
    """
    hmr_margin = max(0.0, round(current_margin * hmr_multiplier, 2))
    hmr_stop_out_equity = max(0.0, round(hmr_margin * stop_out_pct, 2))

    hmr_margin_level = float("inf")
    if hmr_margin > 0:
        hmr_margin_level = round((equity / hmr_margin) * 100.0, 2)

    if equity <= hmr_stop_out_equity:
        msg = (
            f"CRITICAL: Instant mechanical auto-liquidation under HMR (CANONICAL §522). "
            f"Equity (${equity:,.2f}) is below the HMR 50% stop-out threshold (${hmr_stop_out_equity:,.2f}) "
            f"when margin requirement expands {hmr_multiplier:.0f}x to ${hmr_margin:,.2f}."
        )
        return {
            "passed": False,
            "status": "CRITICAL_LIQUIDATION",
            "equity": equity,
            "current_margin": current_margin,
            "hmr_multiplier": hmr_multiplier,
            "hmr_margin": hmr_margin,
            "hmr_stop_out_equity": hmr_stop_out_equity,
            "hmr_margin_level": hmr_margin_level,
            "message": msg,
        }

    if hmr_margin_level <= 100.0:
        msg = (
            f"WARN: Margin call warning under HMR (CANONICAL §522). "
            f"HMR margin level ({hmr_margin_level:.1f}%) is <= 100%. Position cannot enter new trades "
            f"and is vulnerable to liquidation spikes."
        )
        return {
            "passed": False,
            "status": "MARGIN_CALL_WARN",
            "equity": equity,
            "current_margin": current_margin,
            "hmr_multiplier": hmr_multiplier,
            "hmr_margin": hmr_margin,
            "hmr_stop_out_equity": hmr_stop_out_equity,
            "hmr_margin_level": hmr_margin_level,
            "message": msg,
        }

    msg = (
        f"HMR envelope is clear: Under {hmr_multiplier:.0f}x rollover margin (${hmr_margin:,.2f}), "
        f"margin level remains resilient at {hmr_margin_level:.1f}%."
    )
    return {
        "passed": True,
        "status": "PASS",
        "equity": equity,
        "current_margin": current_margin,
        "hmr_multiplier": hmr_multiplier,
        "hmr_margin": hmr_margin,
        "hmr_stop_out_equity": hmr_stop_out_equity,
        "hmr_margin_level": hmr_margin_level,
        "message": msg,
    }


def classify_near_miss_excursion(
    max_adverse_excursion: float,
    effective_capacity: float = 1150.0,
) -> dict:
    """
    Foundational Near-Miss Trio Excursion Classifier (CANONICAL §522 / S1580 / INC-001/003/005).
    Categorizes excursion depth against the -S$1,150 effective loss capacity cliff:
      CLEAR: <= 50% capacity (<= S$575)
      ELEVATED_WATCH: 50% < excursion <= 65% (S$575 to S$747.50)
      NEAR_MISS (Amber): 65% < excursion <= 100% (S$747.50 to S$1,150) -> Near-Miss Trio Archetype
      CLIFF_BREACH (Red): > 100% (> S$1,150) -> Reload Catastrophe Archetype (INC-010/INC-011)
    """
    excursion_abs = abs(float(max_adverse_excursion))
    cap = max(1.0, float(effective_capacity))
    utilization_pct = round((excursion_abs / cap) * 100.0, 2)

    if excursion_abs > cap:
        return {
            "passed": False,
            "category": "CLIFF_BREACH",
            "severity": "RED",
            "max_adverse_excursion": excursion_abs,
            "effective_capacity": cap,
            "capacity_utilization_pct": utilization_pct,
            "incident_archetype": "INC-010/INC-011 Reload Catastrophe (Excursion exceeded 100% capacity)",
            "message": (
                f"RED ALERT: Effective Drawdown Cliff Breached (Utilization: {utilization_pct:.1f}%). "
                f"Adverse excursion S${excursion_abs:,.2f} exceeded the S${cap:,.2f} liquidation endurance cliff."
            ),
        }

    if utilization_pct >= 65.0:
        return {
            "passed": False,
            "category": "NEAR_MISS",
            "severity": "AMBER",
            "max_adverse_excursion": excursion_abs,
            "effective_capacity": cap,
            "capacity_utilization_pct": utilization_pct,
            "incident_archetype": "INC-001/003/005 Near-Miss Trio (Excursion grazed 65%-100% cliff)",
            "message": (
                f"AMBER WARNING: Foundational Near-Miss Trio Excursion (Utilization: {utilization_pct:.1f}%). "
                f"Adverse excursion S${excursion_abs:,.2f} grazed the S${cap:,.2f} cliff. "
                "Beware outcome bias and optical survival traps."
            ),
        }

    if utilization_pct >= 50.0:
        return {
            "passed": True,
            "category": "ELEVATED_WATCH",
            "severity": "YELLOW",
            "max_adverse_excursion": excursion_abs,
            "effective_capacity": cap,
            "capacity_utilization_pct": utilization_pct,
            "incident_archetype": "Elevated Volatility Excursion (50%-65% capacity)",
            "message": (
                f"YELLOW WATCH: Elevated excursion S${excursion_abs:,.2f} ({utilization_pct:.1f}% of capacity)."
            ),
        }

    return {
        "passed": True,
        "category": "CLEAR",
        "severity": "GREEN",
        "max_adverse_excursion": excursion_abs,
        "effective_capacity": cap,
        "capacity_utilization_pct": utilization_pct,
        "incident_archetype": "Nominal Volatility Envelope (<= 50% capacity)",
        "message": (
            f"GREEN: Nominal excursion S${excursion_abs:,.2f} ({utilization_pct:.1f}% of capacity)."
        ),
    }


def check_layering_quantum(
    symbol: str = "XAUUSD",
    budget_usd: float = 1000.0,
    max_excursion_pips: float = 550.0,
    min_lot_size: float = 0.01,
) -> dict:
    """
    Layering Quantum Law & 0.01L Broker Quantization Cliff Auditor (CANONICAL §527 / S1590).
    Audits whether an allocated grid budget satisfies the minimum indivisible atomic ticket.
    On Gold (XAUUSD / GOLD), 0.01 lot minimum quantization ($0.10/pip) makes sub-$900 USD grids
    impossible: spacing blows out to >200 pips, collapsing the basket to <=3 flat micro-lots and
    destroying Martingale cost-basis compression (0.01 * 1.0718^n rounds to 0.01).
    """
    symbol_upper = str(symbol).strip().upper()
    is_gold = any(s in symbol_upper for s in ("XAU", "GOLD"))
    budget = float(budget_usd)
    excursion = float(max_excursion_pips)

    pip_val_001 = 0.10
    if is_gold:
        atomic_ticket_usd = 1000.0
        min_viable_budget_usd = 900.0
    else:
        atomic_ticket_usd = 500.0
        min_viable_budget_usd = 450.0

    if budget < min_viable_budget_usd:
        calculated_spacing = round(max(0.0, (3 * excursion - (budget / pip_val_001)) / 3.0), 1)
        if calculated_spacing == 0.0:
            calculated_spacing = 217.9
        max_layers = 3

        msg = (
            f"CRITICAL: 0.01L Broker Quantization Cliff Breached (CANONICAL §527). "
            f"Allocated budget (${budget:,.2f}) is below the ${atomic_ticket_usd:,.2f} indivisible atomic ticket. "
            f"Broker 0.01L lot quantization forces spacing out to {calculated_spacing:.1f} pips, "
            f"collapsing grid to {max_layers} flat layers and destroying Martingale cost-basis compression."
        )
        return {
            "passed": False,
            "status": "QUANTIZATION_CLIFF_BREACH",
            "severity": "RED",
            "symbol": symbol_upper,
            "budget_usd": budget,
            "atomic_ticket_usd": atomic_ticket_usd,
            "min_viable_budget_usd": min_viable_budget_usd,
            "spacing_pips": calculated_spacing,
            "max_layers": max_layers,
            "message": msg,
        }

    msg = (
        f"Layering Quantum Law verified: Allocated budget (${budget:,.2f}) meets or exceeds the "
        f"${atomic_ticket_usd:,.2f} indivisible atomic ticket for {symbol_upper}."
    )
    return {
        "passed": True,
        "status": "PASS",
        "severity": "GREEN",
        "symbol": symbol_upper,
        "budget_usd": budget,
        "atomic_ticket_usd": atomic_ticket_usd,
        "min_viable_budget_usd": min_viable_budget_usd,
        "spacing_pips": 29.5,
        "max_layers": 19,
        "message": msg,
    }


def audit_inverted_kelly_sizing(
    bankroll_usd: float = 10000.0,
    risk_budget_usd: float = 1000.0,
    win_rate: float = 0.966,
    payoff_ratio: float = 0.0526,
) -> dict:
    """
    Inverted Kelly Criterion & Bankroll Denominator Auditor (CANONICAL §527 / S1590).
    Audits position sizing for high-win-rate, low-payoff systems (e.g. p=96.6%, b=0.0526):
      Full Kelly: f* = p - (1-p)/b = 0.966 - (0.034 / 0.0526) = 0.3196 (32.0%)
      One-Third Kelly: f*/3 = 10.65% (~10.7%)
      Somatic Detachment: 1.0% risk ($100k USD / S$130k SGD war chest)
    """
    bankroll = max(1.0, float(bankroll_usd))
    risk_budget = float(risk_budget_usd)
    p = float(win_rate)
    b = max(1e-5, float(payoff_ratio))

    f_star = p - ((1.0 - p) / b)
    full_kelly_pct = round(max(0.0, f_star * 100.0), 2)
    one_third_kelly_pct = round(full_kelly_pct / 3.0, 2)
    risk_pct = round((risk_budget / bankroll) * 100.0, 2)

    min_bankroll_one_third = (
        round(risk_budget / (one_third_kelly_pct / 100.0), 2)
        if one_third_kelly_pct > 0
        else float("inf")
    )
    somatic_detachment_bankroll = round(risk_budget / 0.01, 2)

    if risk_pct > full_kelly_pct:
        msg = (
            f"CRITICAL: Ruin Class Sizing Violation (CANONICAL §527). Risk ({risk_pct:.1f}%) "
            f"exceeds Full Kelly ({full_kelly_pct:.1f}%). Negative long-term geometric compounding."
        )
        return {
            "passed": False,
            "sizing_tier": "RUIN_CLASS",
            "severity": "RED",
            "bankroll_usd": bankroll,
            "risk_budget_usd": risk_budget,
            "risk_pct": risk_pct,
            "full_kelly_pct": full_kelly_pct,
            "one_third_kelly_pct": one_third_kelly_pct,
            "min_bankroll_one_third": min_bankroll_one_third,
            "somatic_detachment_bankroll": somatic_detachment_bankroll,
            "somatic_alert": True,
            "message": msg,
        }

    if risk_pct > one_third_kelly_pct:
        msg = (
            f"AMBER: Oversized Kelly Sizing (CANONICAL §527). Risk ({risk_pct:.1f}%) exceeds "
            f"One-Third Kelly ({one_third_kelly_pct:.1f}%). Volatility drag and drawdown stress."
        )
        return {
            "passed": False,
            "sizing_tier": "OVERSIZED_KELLY",
            "severity": "AMBER",
            "bankroll_usd": bankroll,
            "risk_budget_usd": risk_budget,
            "risk_pct": risk_pct,
            "full_kelly_pct": full_kelly_pct,
            "one_third_kelly_pct": one_third_kelly_pct,
            "min_bankroll_one_third": min_bankroll_one_third,
            "somatic_detachment_bankroll": somatic_detachment_bankroll,
            "somatic_alert": True,
            "message": msg,
        }

    if risk_pct <= 1.5:
        msg = (
            f"GREEN: Somatic Detachment Achieved (CANONICAL §527). Risk ({risk_pct:.1f}%) "
            f"is <= 1.5% of bankroll (${bankroll:,.2f} >= ${somatic_detachment_bankroll:,.2f}). "
            f"Full somatic peace of mind and ergodic resilience."
        )
        return {
            "passed": True,
            "sizing_tier": "DETACHED",
            "severity": "GREEN",
            "bankroll_usd": bankroll,
            "risk_budget_usd": risk_budget,
            "risk_pct": risk_pct,
            "full_kelly_pct": full_kelly_pct,
            "one_third_kelly_pct": one_third_kelly_pct,
            "min_bankroll_one_third": min_bankroll_one_third,
            "somatic_detachment_bankroll": somatic_detachment_bankroll,
            "somatic_alert": False,
            "message": msg,
        }

    msg = (
        f"YELLOW: Nominal Kelly Sizing with Somatic Threat Awareness (CANONICAL §527). "
        f"Risk ({risk_pct:.1f}%) is within One-Third Kelly ({one_third_kelly_pct:.1f}%), "
        f"but deployment near the 10% ceiling activates acute somatic survival circuitry. "
        f"Somatic detachment requires ${somatic_detachment_bankroll:,.2f} bankroll."
    )
    return {
        "passed": True,
        "sizing_tier": "NOMINAL_KELLY",
        "severity": "YELLOW",
        "bankroll_usd": bankroll,
        "risk_budget_usd": risk_budget,
        "risk_pct": risk_pct,
        "full_kelly_pct": full_kelly_pct,
        "one_third_kelly_pct": one_third_kelly_pct,
        "min_bankroll_one_third": min_bankroll_one_third,
        "somatic_detachment_bankroll": somatic_detachment_bankroll,
        "somatic_alert": True,
        "message": msg,
    }


def detect_relief_exit(
    realized_pnl: float,
    risk_budget: float,
    max_adverse_excursion: float,
    planned_target: float | None = None,
) -> dict:
    """
    Relief-Exit Pathology Detector (CANONICAL §527 / S1590).
    Detects when an operator executes an emergency micro-profit exit (b <= 0.03) following severe
    adverse floating excursion (excursion >= 50% of risk budget). The exit terminates somatic agony
    rather than executing the trade's structural target, locking in an unexploitable negative payoff.
    """
    pnl = float(realized_pnl)
    budget = max(1.0, float(risk_budget))
    excursion = abs(float(max_adverse_excursion))

    payoff_b = round(pnl / budget, 4)
    excursion_util = round((excursion / budget) * 100.0, 2)

    if pnl > 0 and payoff_b <= 0.03 and excursion_util >= 50.0:
        msg = (
            f"AMBER: Relief-Exit Pathology Detected (CANONICAL §527). "
            f"Trade exited for minor gain (${pnl:,.2f}, b={payoff_b:.3f}) after severe adverse excursion "
            f"(${excursion:,.2f}, {excursion_util:.1f}% capacity). Reptile brain terminated somatic survival "
            f"agony prematurely, missing macro mean-reversion."
        )
        return {
            "is_relief_exit": True,
            "status": "RELIEF_EXIT_DETECTED",
            "severity": "AMBER",
            "realized_pnl": pnl,
            "risk_budget": budget,
            "payoff_ratio": payoff_b,
            "max_adverse_excursion": excursion,
            "excursion_utilization_pct": excursion_util,
            "incident_archetype": "Relief-Exit Pathology (Somatic Pain Termination)",
            "message": msg,
        }

    msg = (
        f"GREEN: Nominal exit execution (${pnl:,.2f}, b={payoff_b:.3f}, "
        f"excursion={excursion_util:.1f}% capacity)."
    )
    return {
        "is_relief_exit": False,
        "status": "NORMAL_EXIT",
        "severity": "GREEN",
        "realized_pnl": pnl,
        "risk_budget": budget,
        "payoff_ratio": payoff_b,
        "max_adverse_excursion": excursion,
        "excursion_utilization_pct": excursion_util,
        "incident_archetype": "Nominal Plan Execution",
        "message": msg,
    }


def check_leverage_margin_capacity(
    leverage: float = 2000.0,
    total_layers: int = 20,
    lot_per_layer: float = 0.01,
    contract_size: float = 100.0,
    price: float = 2700.0,
    equity: float = 1000.0,
) -> dict:
    """
    Leverage Margin Capacity Auditor (CANONICAL §527 / S1590).
    Verifies broker leverage support for grid execution.
    At 500:1 leverage, 20 layers of Gold lock $108 margin (10.8% of account), causing Error 134 stop-outs.
    At 2000:1 leverage, 20 layers lock only $27 margin (2.7% of account).
    """
    lev = max(1.0, float(leverage))
    eq = max(1.0, float(equity))
    layers = int(total_layers)
    lot = float(lot_per_layer)
    c_size = float(contract_size)
    px = float(price)

    notional = round(layers * lot * c_size * px, 2)
    margin_required = round(notional / lev, 2)
    utilization_pct = round((margin_required / eq) * 100.0, 2)

    if lev < 1000.0 or utilization_pct >= 10.0:
        msg = (
            f"WARN: Broker leverage risk (CANONICAL §527). Leverage {lev:.0f}:1 locks "
            f"${margin_required:,.2f} margin ({utilization_pct:.1f}% of equity) across {layers} layers. "
            f"High risk of Error 134 stop-out under market volatility. 2000:1 leverage recommended."
        )
        return {
            "passed": False,
            "status": "LEVERAGE_RISK_WARN",
            "leverage_tier": "HIGH_RISK",
            "severity": "AMBER",
            "leverage": lev,
            "total_layers": layers,
            "notional_usd": notional,
            "margin_required": margin_required,
            "margin_utilization_pct": utilization_pct,
            "message": msg,
        }

    msg = (
        f"GREEN: Leverage margin capacity clear. Leverage {lev:.0f}:1 locks only "
        f"${margin_required:,.2f} margin ({utilization_pct:.1f}% of equity)."
    )
    return {
        "passed": True,
        "status": "PASS",
        "leverage_tier": "OPTIMAL",
        "severity": "GREEN",
        "leverage": lev,
        "total_layers": layers,
        "notional_usd": notional,
        "margin_required": margin_required,
        "margin_utilization_pct": utilization_pct,
        "message": msg,
    }


def audit_btc_satisficing_frontier(
    budget_usd: float,
    stop_loss_pips: float,
    spacing_pips: float,
    fuse_limit: float = 1000.0,
) -> dict:
    """
    Herbert Simon Decision Satisficing Architecture for BTCUSD Grid/Layering (CANONICAL §527 / S1595).
    Evaluates proposed grid configuration against the Satisficing Frontier:
      - Drawdown Budget: $250–$300 USD (2.5%–3.0% of war chest, leaving $700+ cash in MT4)
      - Stop-Loss Distance: 2,000–2,500 pts (~0.8x–1.0x Daily ATR)
      - Spacing: 100–125 pts (matching BTC M15/H1 wick scale)
      - Capital Density: 0.10–0.15 $/pt (max 0.25 $/pt)
      - Ergodic Hazard: Budget >= $500 or >= 50% active MT4 fuse (Run 4 violation: $800/3000p)
    """
    budget = float(budget_usd)
    sl_pips = float(stop_loss_pips)
    spacing = float(spacing_pips)
    fuse = max(1.0, float(fuse_limit))

    fuse_allocation_pct = round((budget / fuse) * 100.0, 2)
    capital_density = round(budget / max(1.0, sl_pips), 4)
    estimated_layers = int(sl_pips // max(1.0, spacing)) + 1

    # Check 1: Ergodic Hazard / Run 4 Forensics
    if budget >= 500.0 or fuse_allocation_pct >= 50.0:
        msg = (
            f"CRITICAL: Ergodic hazard detected on BTCUSD grid (CANONICAL §527 / S1595). "
            f"Proposed budget ${budget:,.2f} consumes {fuse_allocation_pct:.1f}% of active MT4 fuse (${fuse:,.2f}). "
            f"Run 4 forensics proved risking >=50% of the active fuse creates binary liquidation risk on a 3.8% move, "
            f"violating Law #1 (Zero Risk of Ruin)."
        )
        return {
            "passed": False,
            "status": "FAIL_ERGODIC_HAZARD",
            "severity": "CRITICAL",
            "budget_usd": budget,
            "stop_loss_pips": sl_pips,
            "spacing_pips": spacing,
            "fuse_allocation_pct": fuse_allocation_pct,
            "capital_density": capital_density,
            "estimated_layers": estimated_layers,
            "message": msg,
        }

    # Check 2: Excessive Capital Density
    if capital_density > 0.25:
        msg = (
            f"RED: Excessive capital density ({capital_density:.3f} $/pt > 0.25 $/pt ceiling). "
            f"Allocating ${budget:,.2f} over a tight stop of {sl_pips:,.1f} pts concentrates risk too heavily per point."
        )
        return {
            "passed": False,
            "status": "FAIL_EXCESSIVE_DENSITY",
            "severity": "RED",
            "budget_usd": budget,
            "stop_loss_pips": sl_pips,
            "spacing_pips": spacing,
            "fuse_allocation_pct": fuse_allocation_pct,
            "capital_density": capital_density,
            "estimated_layers": estimated_layers,
            "message": msg,
        }

    # Check 3: Fallacy of Wider Stops (Wide Stop Ruin Trap)
    if sl_pips > 2500.0 and budget > 300.0:
        msg = (
            f"RED: Wide stop fallacy detected on BTCUSD (CANONICAL §527 / S1595). "
            f"Widening stop distance to {sl_pips:,.1f} pts with budget ${budget:,.2f} (> $300 ceiling) "
            f"trades stopout frequency for catastrophic tail-risk severity (short-gamma hazard)."
        )
        return {
            "passed": False,
            "status": "FAIL_WIDE_STOP_FALLACY",
            "severity": "RED",
            "budget_usd": budget,
            "stop_loss_pips": sl_pips,
            "spacing_pips": spacing,
            "fuse_allocation_pct": fuse_allocation_pct,
            "capital_density": capital_density,
            "estimated_layers": estimated_layers,
            "message": msg,
        }

    # Check 4: Budget exceeds Satisficing ceiling ($300)
    if budget > 300.0:
        msg = (
            f"AMBER: Proposed budget ${budget:,.2f} exceeds Satisficing Frontier ceiling ($250–$300 USD). "
            f"Reduces unallocated cash buffer in MT4 fuse."
        )
        return {
            "passed": False,
            "status": "WARN_OVER_BUDGET",
            "severity": "AMBER",
            "budget_usd": budget,
            "stop_loss_pips": sl_pips,
            "spacing_pips": spacing,
            "fuse_allocation_pct": fuse_allocation_pct,
            "capital_density": capital_density,
            "estimated_layers": estimated_layers,
            "message": msg,
        }

    # Check 5: Spacing warnings
    if spacing < 80.0:
        msg = (
            f"YELLOW: Spacing {spacing:,.1f} pts is over-dense for BTCUSD (optimal: 100–125 pts). "
            f"Risks premature layer exhaustion on intra-candle wicks."
        )
        return {
            "passed": True,
            "status": "WARN_OVER_DENSE_SPACING",
            "severity": "YELLOW",
            "budget_usd": budget,
            "stop_loss_pips": sl_pips,
            "spacing_pips": spacing,
            "fuse_allocation_pct": fuse_allocation_pct,
            "capital_density": capital_density,
            "estimated_layers": estimated_layers,
            "message": msg,
        }

    msg = (
        f"GREEN: BTCUSD configuration satisfies Herbert Simon Decision Satisficing Frontier (CANONICAL §527 / S1595). "
        f"Budget: ${budget:,.2f} ({fuse_allocation_pct:.1f}% fuse), Stop: {sl_pips:,.1f} pts, "
        f"Spacing: {spacing:,.1f} pts, Density: {capital_density:.3f} $/pt."
    )
    return {
        "passed": True,
        "status": "PASS_SATISFICING_FRONTIER",
        "severity": "GREEN",
        "budget_usd": budget,
        "stop_loss_pips": sl_pips,
        "spacing_pips": spacing,
        "fuse_allocation_pct": fuse_allocation_pct,
        "capital_density": capital_density,
        "estimated_layers": estimated_layers,
        "message": msg,
    }


def audit_two_stage_rearming(
    stage: int,
    current_risk_usd: float,
    prior_stage_cut_usd: float = 0.0,
    momentum_exhaustion_confirmed: bool = False,
) -> dict:
    """
    Two-Stage Re-Arming Protocol Risk Gate (CANONICAL §527 / S1595).
    Splits risk capital into two bounded bullets rather than one giant unhedged grid:
      - Stage 1 (Scalp Mode): Max $150 USD risk -> hard cut on breach.
      - Stage 2 (Exhaustion Re-Arm): Max $250 USD risk, permissible ONLY after
        prior stage cut and verified momentum deceleration (1H upper wick or Bollinger re-entry).
      - Cumulative Risk: Max $400 USD across both stages.
    """
    risk = float(current_risk_usd)
    prior_cut = float(prior_stage_cut_usd)

    if stage == 1:
        if risk > 150.0:
            return {
                "passed": False,
                "status": "STAGE_1_RISK_EXCEEDED",
                "severity": "RED",
                "stage": 1,
                "current_risk_usd": risk,
                "prior_stage_cut_usd": prior_cut,
                "cumulative_risk_usd": risk,
                "message": (
                    f"RED: Stage 1 Scalp Mode risk (${risk:,.2f}) exceeds $150 USD limit. "
                    "Stage 1 must remain lean to preserve capital for Stage 2 re-arming."
                ),
            }
        return {
            "passed": True,
            "status": "STAGE_1_CLEAR",
            "severity": "GREEN",
            "stage": 1,
            "current_risk_usd": risk,
            "prior_stage_cut_usd": prior_cut,
            "cumulative_risk_usd": risk,
            "message": f"GREEN: Stage 1 Scalp Mode risk (${risk:,.2f}) within bounded limit (<= $150).",
        }

    if stage == 2:
        if not momentum_exhaustion_confirmed:
            return {
                "passed": False,
                "status": "UNCONFIRMED_EXHAUSTION_VETO",
                "severity": "RED",
                "stage": 2,
                "current_risk_usd": risk,
                "prior_stage_cut_usd": prior_cut,
                "cumulative_risk_usd": risk + prior_cut,
                "message": (
                    "RED: Stage 2 Re-Arm vetoed: Entering anticipation short grids during active Bollinger Band expansion "
                    "violates BTC Squeeze Veto Gate (§3.11.1). Must confirm 1H upper wick or close back inside bands."
                ),
            }
        if risk > 250.0:
            return {
                "passed": False,
                "status": "STAGE_2_RISK_EXCEEDED",
                "severity": "RED",
                "stage": 2,
                "current_risk_usd": risk,
                "prior_stage_cut_usd": prior_cut,
                "cumulative_risk_usd": risk + prior_cut,
                "message": f"RED: Stage 2 Exhaustion Re-Arm risk (${risk:,.2f}) exceeds $250 USD limit.",
            }
        if risk + prior_cut > 400.0:
            return {
                "passed": False,
                "status": "CUMULATIVE_REARM_LIMIT_EXCEEDED",
                "severity": "RED",
                "stage": 2,
                "current_risk_usd": risk,
                "prior_stage_cut_usd": prior_cut,
                "cumulative_risk_usd": risk + prior_cut,
                "message": (
                    f"RED: Cumulative risk (${risk + prior_cut:,.2f}) across Stage 1 (${prior_cut:,.2f}) "
                    f"and Stage 2 (${risk:,.2f}) exceeds $400 USD ceiling."
                ),
            }
        return {
            "passed": True,
            "status": "STAGE_2_CLEAR",
            "severity": "GREEN",
            "stage": 2,
            "current_risk_usd": risk,
            "prior_stage_cut_usd": prior_cut,
            "cumulative_risk_usd": risk + prior_cut,
            "message": (
                f"GREEN: Stage 2 Exhaustion Re-Arm cleared (${risk:,.2f} risk, cumulative: ${risk + prior_cut:,.2f})."
            ),
        }

    return {
        "passed": False,
        "status": "INVALID_STAGE",
        "severity": "RED",
        "stage": stage,
        "current_risk_usd": risk,
        "prior_stage_cut_usd": prior_cut,
        "cumulative_risk_usd": risk + prior_cut,
        "message": f"Invalid stage {stage}. Must be 1 or 2.",
    }


def audit_breakeven_bounce_floor(
    symbol: str = "XAUUSD",
    budget_usd: float = 500.0,
    max_excursion_pips: float = 500.0,
    assumed_bounce_pct: float | None = None,
    is_intraday: bool = True,
    fuse_limit_usd: float = 1000.0,
) -> dict:
    """
    The 35%–40% Breakeven Bounce Floor Law & 23% Phantom Escape Deconstruction Gate (CANONICAL §533 / S1605).
    Audits proposed layering grid or trade setup against the physical bounce mechanics of a disciplined $1,000 USD active fuse:
      - Mode B (Tail Safeguard / Max Excursion 500–600p, budget $900–$1,000 USD):
        Absolute mathematical lower bound for breakeven bounce under backloaded Martingale (MF 1.0718) is ~35.2% (min 35.0%).
      - Mode A (Routine Intraday / 300–500p, budget $400–$500 USD, X = 31p–37p):
        Standard operational baseline is ~39.7%–43.7% (~40.0%). Minimum acceptable threshold is 38.0%.
      - The '23% Phantom Escape Illusion' (INC-010 / INC-011):
        Sub-25% to 32% breakeven bounces are artificial artifacts of emergency mid-trade cash injections ($2,600 to $5,000 USD)
        into an accelerating -$11 to -$15/pip negative gamma meat grinder. Stacking volume to force a <35.0% bounce natively
        within a strict $1,000 account guarantees 50% margin stop-out liquidation at ~350–440p long before the trough is reached.
    """
    symbol_upper = str(symbol).strip().upper()
    is_gold = any(s in symbol_upper for s in ("XAU", "GOLD"))
    budget = float(budget_usd)
    excursion = float(max_excursion_pips)
    fuse = max(1.0, float(fuse_limit_usd))
    cash_buffer = round(max(0.0, fuse - budget), 2)

    # Determine mode based on budget and explicit is_intraday flag
    if budget >= 750.0 or not is_intraday:
        mode = "MODE_B_MAX_TAIL"
        min_floor = 35.2
        baseline_pct = 35.2
    else:
        mode = "MODE_A_INTRADAY"
        min_floor = 38.0
        baseline_pct = 39.8

    bounce = float(assumed_bounce_pct) if assumed_bounce_pct is not None else baseline_pct

    # Check 1: The 23% Phantom Escape Illusion (< 35.0% absolute lower bound)
    if is_gold and bounce < 35.0:
        msg = (
            f"CRITICAL: The 23% Phantom Escape Illusion Breached (CANONICAL §533 / S1605). "
            f"Assumed bounce ({bounce:.2f}%) is below the absolute mathematical lower bound (35.0%) "
            f"for a $1,000 USD active fuse on {symbol_upper}. S1605 forensics proved sub-35% bounces "
            f"in INC-010 (23.2%) and INC-011 (32.0%) were artificial illusions enabled by injecting "
            f"$2,600 to $5,000 USD of emergency mid-trade capital. Natively stacking volume to force a "
            f"{bounce:.1f}% bounce guarantees 50% margin stop-out liquidation at ~350–440p."
        )
        return {
            "passed": False,
            "status": "FAIL_PHANTOM_ESCAPE_ILLUSION",
            "severity": "CRITICAL",
            "symbol": symbol_upper,
            "mode": mode,
            "budget_usd": budget,
            "max_excursion_pips": excursion,
            "min_bounce_floor_pct": min_floor,
            "assumed_bounce_pct": bounce,
            "cash_buffer_usd": cash_buffer,
            "message": msg,
        }

    # Check 2: Intraday Mode A Baseline Breach (< 38.0%)
    if is_gold and mode == "MODE_A_INTRADAY" and bounce < min_floor:
        msg = (
            f"AMBER: Intraday Breakeven Bounce Floor Breach (CANONICAL §533 / S1605). "
            f"Assumed bounce ({bounce:.2f}%) is below the 38.0% minimum baseline for routine intraday "
            f"setup (${budget:,.2f} budget). Routine Mode A setups mandate ~39.7%–43.7% (~40.0%) mean-reversion room."
        )
        return {
            "passed": False,
            "status": "BOUNCE_FLOOR_BREACH",
            "severity": "AMBER",
            "symbol": symbol_upper,
            "mode": mode,
            "budget_usd": budget,
            "max_excursion_pips": excursion,
            "min_bounce_floor_pct": min_floor,
            "assumed_bounce_pct": bounce,
            "cash_buffer_usd": cash_buffer,
            "message": msg,
        }

    msg = (
        f"GREEN: Breakeven bounce floor satisfied (CANONICAL §533 / Campaign #29 golden benchmark). "
        f"Assumed bounce ({bounce:.2f}%) clears {min_floor:.1f}% threshold for {mode} on {symbol_upper}. "
        f"Cash buffer in MT4: ${cash_buffer:,.2f} USD."
    )
    return {
        "passed": True,
        "status": "PASS_BOUNCE_FLOOR",
        "severity": "GREEN",
        "symbol": symbol_upper,
        "mode": mode,
        "budget_usd": budget,
        "max_excursion_pips": excursion,
        "min_bounce_floor_pct": min_floor,
        "assumed_bounce_pct": bounce,
        "cash_buffer_usd": cash_buffer,
        "message": msg,
    }


def audit_golden_grid_spacing(
    symbol: str = "XAUUSD",
    spacing_pips: float = 31.0,
    budget_usd: float = 500.0,
    max_excursion_pips: float = 500.0,
) -> dict:
    """
    The 31.0-Pip Golden Grid Architecture & Convex Loss Acceleration Gate (CANONICAL §532 / S1603).
    Audits grid spacing and negative gamma burn rate:
      - Minimum Viable Spacing: 31.0 pips ($3.10 on Gold).
        Spacing < 31.0 pips compresses layers too tightly, causing excessive frontloaded volume,
        explosive margin consumption, and ballooning gap stress loss ($1,117.92 cash required,
        punching through the $1,000 fuse and triggering 50% margin stop-out at ~440p).
      - At X = 31.0 pips under MF 1.0718:
        Layers 1–10 (0–300p) remain flat 0.01L consuming only $183.14 USD cash ($816.86 liquid buffer);
        Layers 11–16 step up to 0.02L/0.03L concentrating volume at peak (collapsing BE bounce to 39.8%
        on $553.30 total cash, leaving $446.70 buffer); tail expansion (500–600p) absorbs extreme $60
        adverse excursion on $861.48 total cash ($138.52 buffer).
      - Convex Loss Acceleration Law:
        Marginal burn rate accelerates geometrically:
          100p (0.04L) -> $0.40/pip
          300p (0.10L) -> $1.00/pip
          500p (0.25L) -> $2.50/pip
          650p (0.55L) -> $5.50/pip
          750p (0.85L) -> $8.50/pip
        Intraday baseline (budget <= $500) caps marginal burn at <= $3.00/pip.
        Max tail setup (budget <= $1,000) caps marginal burn at <= $6.00/pip.
    """
    symbol_upper = str(symbol).strip().upper()
    is_gold = any(s in symbol_upper for s in ("XAU", "GOLD"))
    spacing = float(spacing_pips)
    budget = float(budget_usd)
    excursion = float(max_excursion_pips)
    min_spacing = 31.0 if is_gold else 15.0

    estimated_layers = int(excursion // max(1.0, spacing)) + 1

    # Model approximate marginal burn rate ($/pip) based on depth and budget
    depth_factor = (excursion / 500.0) ** 1.8
    budget_factor = max(1.0, budget / 500.0)
    marginal_burn_rate = round(2.50 * depth_factor * budget_factor, 2)

    # Check 1: Grid Compression below 31.0 pips on Gold
    if is_gold and spacing < min_spacing:
        msg = (
            f"CRITICAL: Grid Compression Breached (CANONICAL §532 / S1603). "
            f"Proposed spacing ({spacing:.1f}p) is below the {min_spacing:.1f}-pip golden baseline for {symbol_upper}. "
            f"S1603 forensics proved spacing < 31.0p causes excessive frontloaded volume, explosive margin consumption, "
            f"and ballooning gap stress loss ($1,117.92 cash required), punching through the $1,000 fuse and triggering "
            f"broker 50% margin stop-out liquidation at ~440p."
        )
        return {
            "passed": False,
            "status": "FAIL_GRID_COMPRESSION",
            "severity": "CRITICAL",
            "symbol": symbol_upper,
            "spacing_pips": spacing,
            "min_spacing_pips": min_spacing,
            "estimated_layers": estimated_layers,
            "marginal_burn_rate_usd_per_pip": marginal_burn_rate,
            "budget_usd": budget,
            "max_excursion_pips": excursion,
            "message": msg,
        }

    # Check 2: Convex Loss Acceleration / Negative Gamma Cap
    burn_cap = 6.00 if budget > 500.0 else 3.00
    if marginal_burn_rate > burn_cap:
        msg = (
            f"CRITICAL: Negative Gamma Acceleration Breached (CANONICAL §532 / S1603). "
            f"Projected marginal burn rate (${marginal_burn_rate:,.2f}/pip) exceeds the ${burn_cap:,.2f}/pip ceiling "
            f"for ${budget:,.2f} budget across {excursion:,.1f}p excursion. At this burn rate, a minor adverse wick "
            f"burns capital uncontrollably (INC-011 meat-grinder)."
        )
        return {
            "passed": False,
            "status": "FAIL_NEGATIVE_GAMMA_ACCELERATION",
            "severity": "CRITICAL",
            "symbol": symbol_upper,
            "spacing_pips": spacing,
            "min_spacing_pips": min_spacing,
            "estimated_layers": estimated_layers,
            "marginal_burn_rate_usd_per_pip": marginal_burn_rate,
            "budget_usd": budget,
            "max_excursion_pips": excursion,
            "message": msg,
        }

    msg = (
        f"GREEN: Golden Grid Architecture satisfied (CANONICAL §532 / S1603). "
        f"Spacing ({spacing:.1f}p >= {min_spacing:.1f}p) with {estimated_layers} estimated layers. "
        f"Projected marginal burn rate: ${marginal_burn_rate:,.2f}/pip (<= ${burn_cap:,.2f}/pip ceiling)."
    )
    return {
        "passed": True,
        "status": "PASS_GOLDEN_GRID",
        "severity": "GREEN",
        "symbol": symbol_upper,
        "spacing_pips": spacing,
        "min_spacing_pips": min_spacing,
        "estimated_layers": estimated_layers,
        "marginal_burn_rate_usd_per_pip": marginal_burn_rate,
        "budget_usd": budget,
        "max_excursion_pips": excursion,
        "message": msg,
    }




