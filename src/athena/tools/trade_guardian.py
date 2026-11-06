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


