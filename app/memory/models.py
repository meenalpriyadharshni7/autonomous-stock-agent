from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    Boolean,
    Text,
    DateTime,
    UniqueConstraint,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


# =========================================================
# DAILY METRICS TABLE
# Stores computed indicators + ranking per stock per day
# =========================================================
class DailyMetrics(Base):
    __tablename__ = "daily_metrics"

    id = Column(Integer, primary_key=True, index=True)

    stock_symbol = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    category = Column(String(20))  # CORE or GAINER

    close_price = Column(Float, nullable=False)

    rsi = Column(Float)
    ma20 = Column(Float)
    ma50 = Column(Float)
    volatility = Column(Float)

    momentum_7d = Column(Float)
    momentum_30d = Column(Float)

    score = Column(Float)
    score_change = Column(Float)

    rank = Column(Integer)
    rank_change = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("stock_symbol", "date", name="uix_stock_date"),
    )


# =========================================================
# SIGNAL TABLE
# Stores decision classification per stock per day
# =========================================================
class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)

    stock_symbol = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    signal = Column(String(20), nullable=False)  # BUY / WAIT / DONT_BUY
    signal_change = Column(String(50))

    confidence = Column(Float)
    reason_tags = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("stock_symbol", "date", name="uix_signal_stock_date"),
    )


# =========================================================
# SIGNAL PERFORMANCE TABLE
# Tracks 5-day forward evaluation
# =========================================================
class SignalPerformance(Base):
    __tablename__ = "signal_performance"

    id = Column(Integer, primary_key=True, index=True)

    stock_symbol = Column(String(20), nullable=False, index=True)

    signal_date = Column(Date, nullable=False)
    evaluation_date = Column(Date, nullable=False)

    signal_type = Column(String(20))  # BUY / WAIT / DONT_BUY

    entry_price = Column(Float)
    exit_price = Column(Float)

    return_after_5d = Column(Float)
    correct_prediction = Column(Boolean)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "stock_symbol",
            "signal_date",
            name="uix_performance_stock_signal_date"
        ),
    )


# =========================================================
# EXECUTION LOG TABLE
# Tracks daily run success/failure
# =========================================================
class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)

    execution_time = Column(DateTime(timezone=True), server_default=func.now())

    status = Column(String(20))  # SUCCESS / FAILURE
    message = Column(Text)