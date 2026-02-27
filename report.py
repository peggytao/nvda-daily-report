import yfinance as yf
import feedparser
from datetime import datetime

# ---------- 1️⃣ Stock Data ----------
ticker = yf.Ticker("NVDA")
hist = ticker.history(period="60d")  # last 60 days
price = hist["Close"].iloc[-1]
pe_ratio = ticker.info.get("trailingPE", "N/A")
eps = ticker.info.get("trailingEps", "N/A")
market_cap = ticker.info.get("marketCap", "N/A")

def format_number(num):
    if num in [None, "N/A"]:
        return "N/A"
    if num >= 1_000_000_000_000:
        return f"${num/1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    return f"${num}"

market_cap_fmt = format_number(market_cap)

# ---------- 2️⃣ Moving Averages ----------
ma20 = hist["Close"].rolling(20).mean().iloc[-1]
ma50 = hist["Close"].rolling(50).mean().iloc[-1]

# ---------- 3️⃣ Rule-based Recommendation ----------
recommendation = "HOLD"
rec_class = "hold"
reason = ""

if price > ma20 and price > ma50 and pe_ratio != "N/A" and pe_ratio < 50:
    recommendation = "BUY"
    rec_class = "buy"
    reason = "Price above MA20 & MA50; valuation reasonable."
elif price < ma20 or price < ma50 or (pe_ratio != "N/A" and pe_ratio > 60):
    recommendation = "SELL"
    rec_class = "sell"
    reason = "Price below moving averages or overvalued."

# ---------- 4️⃣ Fetch Latest News ----------
rss_url = "https://finance.yahoo.com/rss/headline?s=NVDA"
feed = feedparser.parse(rss_url)
headlines = [entry.title for entry in feed.entries[:5]]
headlines_text = "\n".join(f"- {h}" for h in headlines)

# ---------- 5️⃣ Generate HTML ----------
today = datetime.now().strftime("%Y-%m-%d")
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NVDA Daily Report</title>
<style>
body {{ font-family: Arial; background:#f4f6f9; margin:20px; }}
.card {{ background:white; padding:25px; border-radius:12px; margin-bottom:20px; }}
h1, h2 {{ margin:0 0 10px 0; }}
.metric {{ margin-bottom:10px; }}
.recommendation {{ font-size:28px; font-weight:bold; padding:10px; border-radius:8px; text-align:center; margin-top:15px; }}
.buy {{ background-color: #e6f9ec; color: #0a8a34; }}
.hold {{ background-color: #fff7e6; color: #b7791f; }}
.sell {{ background-color: #fde8e8; color: #c53030; }}
.analysis-text {{ margin-top:10px; line-height:1.6; white-space: pre-line; }}
.footer {{ font-size:12px; color:#888; text-align:center; margin-top:30px; }}
</style>
</head>
<body>

<div class="card">
<h1>NVDA Daily Stock Report</h1>
<p><strong>Date:</strong> {today}</p>
<div class="metric"><strong>Price:</strong> ${price:.2f}</div>
<div class="metric"><strong>PE Ratio:</strong> {pe_ratio}</div>
<div class="metric"><strong>EPS:</strong> {eps}</div>
<div class="metric"><strong>Market Cap:</strong> {market_cap_fmt}</div>

<div class="recommendation {rec_class}">{recommendation}</div>
<p>{reason}</p>
</div>

<div class="card">
<h2>Latest News</h2>
<div class="analysis-text">{headlines_text}</div>
</div>

<div class="footer">
Disclaimer: This report is automatically generated for educational purposes only and does not constitute financial advice.
</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("NVDA daily report generated successfully.")
