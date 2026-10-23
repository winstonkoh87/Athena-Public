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
