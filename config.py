import os

# Only load dotenv in local development
if os.getenv("RAILWAY_ENVIRONMENT") is None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

# Fixed stocks you want to track
CORE_STOCKS = [
    "TCS.NS",
    "INFY.NS",
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "LT.NS",
    "SBIN.NS",
    "ITC.NS",
    "BHARTIARTL.NS",
    "HINDUNILVR.NS"
]

# Broader NSE universe for gainers calculation
NIFTY_50_LIST = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS",
    "BHARTIARTL.NS", "LT.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BRITANNIA.NS",
    "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "INDUSINDBK.NS", "JSWSTEEL.NS",
    "KOTAKBANK.NS", "MARUTI.NS", "M&M.NS", "NESTLEIND.NS",
    "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "SBILIFE.NS",
    "SHREECEM.NS", "SUNPHARMA.NS", "TATACONSUM.NS", "TATAMOTORS.NS",
    "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS",
    "UPL.NS", "WIPRO.NS", "ADANIENT.NS", "ADANIPORTS.NS",
    "APOLLOHOSP.NS", "BAJAJ-AUTO.NS"
]

HISTORICAL_DAYS = 500

# ===============================
# TELEGRAM CONFIG
# ===============================
TELEGRAM_TOKEN = "8685634743:AAHnXj3MjiG11iPWLXgQoG9J_2285mVPj_0"
TELEGRAM_CHAT_ID = "1435145197"

# ===============================
# EMAIL CONFIG (GMAIL EXAMPLE)
# ===============================
EMAIL_SENDER = "csk738931@gmail.com"
EMAIL_PASSWORD = "rwubokqpuxqnbleg"
EMAIL_RECEIVER = "klaussiriusremus@gmail.com"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587