from sqlalchemy import select
from datetime import datetime
from app.memory.db import SessionLocal
from app.memory.models import DailyMetrics, Signal
from app.utils.time_utils import get_today_date


def format_rank_change(rank_change):
    if rank_change is None:
        return "🆕"
    elif rank_change > 0:
        return f"🔼 +{rank_change}"
    elif rank_change < 0:
        return f"🔽 {rank_change}"
    else:
        return "⏺ 0"


def format_score_change(score_change):
    if score_change is None:
        return ""
    elif score_change > 0:
        return f"(+{round(score_change,2)})"
    elif score_change < 0:
        return f"({round(score_change,2)})"
    else:
        return "(0)"


def generate_daily_report():
    db = SessionLocal()
    today = get_today_date()

    metrics = db.execute(
        select(DailyMetrics).where(DailyMetrics.date == today)
    ).scalars().all()

    signals = db.execute(
        select(Signal).where(Signal.date == today)
    ).scalars().all()

    db.close()

    if not metrics:
        return "⚠ No data available for today."

    signal_map = {s.stock_symbol: s for s in signals}

    metrics.sort(key=lambda x: x.rank)

    report = []
    report.append("📈 *Autonomous Financial Decision Intelligence System*")
    report.append(f"📅 Date: {today}\n")

    buy_count = 0
    wait_count = 0
    dont_count = 0

    for m in metrics:
        s = signal_map.get(m.stock_symbol)

        signal = s.signal if s else "N/A"
        confidence = f"{int(s.confidence)}%" if s and s.confidence else "N/A"

        if signal == "BUY":
            buy_count += 1
            signal_icon = "🟢 BUY"
        elif signal == "WAIT":
            wait_count += 1
            signal_icon = "🟡 WAIT"
        else:
            dont_count += 1
            signal_icon = "🔴 DONT_BUY"

        movement = format_rank_change(m.rank_change)
        score_shift = format_score_change(m.score_change)
        signal_shift = s.signal_change if s else ""

        line = (
            f"*#{m.rank}* {m.stock_symbol} ({m.category}) {movement}\n"
            f"Score: {round(m.score,2)} {score_shift} | "
            f"Signal: {signal_icon} | "
            f"Shift: {signal_shift} | "
            f"Conf: {confidence}\n"
        )

        report.append(line)

    report.append("\n📊 *Summary*")
    report.append(f"🟢 BUY: {buy_count}")
    report.append(f"🟡 WAIT: {wait_count}")
    report.append(f"🔴 DONT_BUY: {dont_count}")

    return "\n".join(report)