import yfinance as yf
import feedparser
from datetime import datetime

# 1️⃣ Fetch NVDA stock data
ticker = yf.Ticker("NVDA")
hist = ticker.history(period="60d")  # last 60 days
price = hist["Close"].iloc[-1]
pe_ratio = ticker.info.get("trailingPE", None)
eps = ticker.info.get("trailingEps", None)
market_cap = ticker.info.get("marketCap", None)

# 2️⃣ Simple moving averages (MA20 and MA50)
ma20 = hist["Close"].rolling(window=20).mean().iloc[-1]
ma50 = hist["Close"].rolling(window=50).mean().iloc[-1]

# 3️⃣ Rule-based recommendation
recommendation = "HOLD"
reason = ""

if price > ma20 and price > ma50 and pe_ratio and pe_ratio < 50:
    recommendation = "BUY"
    reason = "Price above MA20 and MA50; valuation reasonable."
elif price < ma20 or price < ma50 or (pe_ratio and pe_ratio > 60):
    recommendation = "SELL"
    reason = "Price below moving averages or overvalued."
else:
    recommendation = "HOLD"
    reason = "Mixed signals; maintain current position."

# 4️⃣ Fetch latest news from RSS (Yahoo Finance)
rss_url = "https://finance.yahoo.com/rss/headline?s=NVDA"
feed = feedparser.parse(rss_url)
headlines = [entry.title for entry in feed.entries[:5]]

# 5️⃣ Generate HTML report
today = datetime.now().strftime("%Y-%m-%d")
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<title>NVDA Daily Report</title>
<style>
body {{ font-family: Arial; background:#f4f6f9; margin:20px; }}
.card {{ background:white; padding:20px; border-radius:12px; margin-bottom:20px; }}
.recommendation {{ font-size:28px; font-weight:bold; margin-top:15px; }}
.buy {{ color:green; }}
.hold {{ color:orange; }}
.sell {{ color:red; }}
</style>
</head>
<body>
<div class="card">
<h1>NVDA Daily Report - {today}</h1>
<p><strong>Price:</strong> ${price:.2f}</p>
<p><strong>PE Ratio:</strong> {pe_ratio}</p>
<p><strong>EPS:</strong> {eps}</p>
<p><strong>Market Cap:</strong> {market_cap}</p>
<div class="recommendation {recommendation.lower()}">
Recommendation: {recommendation}
</div>
<p>{reason}</p>
</div>
<div class="card">
<h2>Latest News</h2>
<ul>
{''.join([f'<li>{h}</li>' for h in headlines])}
</ul>
</div>
<div class="card" style="font-size:12px;">
Disclaimer: This is an automated report for educational purposes only.
</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("NVDA free daily report generated successfully.")
