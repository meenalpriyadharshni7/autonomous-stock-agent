# 🚀 Autonomous Financial Decision Intelligence System

An institutional-grade AI-driven stock intelligence engine that:

- Detects market regime
- Generates ranked stock signals
- Evaluates historical performance
- Performs portfolio backtesting
- Computes rolling strategy accuracy
- Sends daily Telegram & Email reports
- Runs autonomously on cloud infrastructure

---

## 📊 Core Capabilities

### 1️⃣ Market Regime Detection
- Trend classification (Bullish / Bearish / Neutral)
- Volatility regime detection
- Momentum state analysis

### 2️⃣ Multi-Factor Stock Scoring
Weighted scoring model combining:
- Momentum (7D / 30D)
- Moving average alignment
- RSI health
- Volume confirmation
- Volatility penalty
- Acceleration bonus
- Breakout detection

Score range: **0 – 100 (bounded & normalized)**

---

### 3️⃣ Institutional Ranking Engine
- Risk-adjusted scoring
- Volatility regime adjustment
- Breakout bonus
- Acceleration bonus
- Top-N allocation logic

---

### 4️⃣ Signal Engine
Signal types:
- STRONG_BUY
- BUY
- HOLD
- AVOID

Confidence adjusted using:
- Rolling accuracy
- Market regime
- Strategy expectancy
- Market breadth

---

### 5️⃣ Accuracy Tracking (365-Day Rolling)
- 5-day forward performance evaluation
- Idempotent evaluation (no duplicate inserts)
- Cloud-safe rolling window
- Holiday-safe computation
- Stored in persistent database

---

### 6️⃣ Portfolio Backtesting Engine
Includes:
- Capital allocation scaling
- Stop-loss protection
- Slippage modeling
- Brokerage cost modeling
- Max position cap
- Daily drawdown guard
- Exposure adjustment by regime

Outputs:
- Total Return %
- Sharpe Ratio
- Max Drawdown %
- Final Capital

---

### 7️⃣ Autonomous Reporting
Daily report includes:
- Market regime
- Rolling accuracy
- Expectancy
- Market breadth
- Portfolio metrics
- Top 5 ranked stocks
- All generated signals

Delivery:
- Telegram Bot
- Email

---

### 8️⃣ Holiday-Aware Execution
- Detects NSE holidays & weekends
- Runs in report-only mode when market closed
- Does not insert new data on holidays
- Maintains rolling intelligence continuity

---

## 🧠 Architecture Overview

Data Fetch → Indicator Engine → Scoring Engine → Ranking Engine
↓ ↓ ↓ ↓
Regime Engine → Signal Engine → Confidence Adjustment
↓
Backtesting Engine
↓
Accuracy Tracker
↓
Report Builder → Telegram + Email


---

## 🗄 Database Tables

- `DailyMetrics`
- `Signal`
- `SignalPerformance`
- `ExecutionLog`

Designed for:
- Idempotent writes
- Cloud persistence
- Restart safety

---

## ⚙️ Technologies Used

- Python 3.12
- SQLAlchemy
- yFinance
- pandas / numpy
- pandas_market_calendars
- SMTP (Email)
- Telegram Bot API
- Railway (Cloud Deployment)

---

## ☁️ Cloud Deployment

Designed for:
- Railway deployment
- Cron-based scheduled execution
- PostgreSQL persistence
- Environment variable configuration

Runs fully autonomous with no manual intervention.

---

## 🔐 Environment Variables Required

EMAIL_SENDER=
EMAIL_PASSWORD=
EMAIL_RECEIVER=
SMTP_SERVER=
SMTP_PORT=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=


---

## 📈 Strategy Philosophy

This system is built on:

- Regime awareness
- Risk-first capital allocation
- Statistical validation over intuition
- Rolling performance monitoring
- Institutional backtesting standards

---

## 🛡 Production Safety Features

- Duplicate run protection
- Holiday guard
- Idempotent evaluations
- Database transaction safety
- Failure logging
- Notification on crash

---

## 🔮 Future Improvements

- Regime-specific accuracy tracking
- Separate BUY vs SELL precision
- Confidence calibration curve
- Dynamic capital scaling by expectancy
- Multi-timeframe integration
- Reinforcement-learning signal adjustment

---

## 📌 Disclaimer

This project is for research and educational purposes only.
It does not constitute financial advice.
Trading involves risk.

---

## 👤 Author

Built as an autonomous AI financial intelligence system.
