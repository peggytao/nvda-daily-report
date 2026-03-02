import os
from datetime import datetime

import feedparser
import yfinance as yf

def format_number(num):
    if num in [None, "N/A"]:
        return "N/A"
    if num >= 1_000_000_000_000:
        return f"${num/1_000_000_000_000:.2f}T"
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    if num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    return f"${num}"

def get_stock_snapshot():
    ticker = yf.Ticker("NVDA")
    hist = ticker.history(period="60d")

    if hist.empty:
        raise RuntimeError("No NVDA price history returned from yfinance")

    price = float(hist["Close"].iloc[-1])
    pe_ratio = ticker.info.get("trailingPE", "N/A")
    eps = ticker.info.get("trailingEps", "N/A")
    market_cap = ticker.info.get("marketCap", "N/A")

    ma20 = float(hist["Close"].rolling(20).mean().iloc[-1])
    ma50 = float(hist["Close"].rolling(50).mean().iloc[-1])

    recommendation = "HOLD"
    rec_class = "hold"
    reason = "Price action and valuation are mixed today."

    if price > ma20 and price > ma50 and pe_ratio != "N/A" and pe_ratio < 50:
        recommendation = "BUY"
        rec_class = "buy"
        reason = "Price above MA20 & MA50; valuation reasonable."
    elif price < ma20 or price < ma50 or (pe_ratio != "N/A" and pe_ratio > 60):
        recommendation = "SELL"
        rec_class = "sell"
        reason = "Price below moving averages or overvalued."

    return {
        "price": f"${price:.2f}",
        "pe_ratio": pe_ratio,
        "eps": eps,
        "market_cap": format_number(market_cap),
        "recommendation": recommendation,
        "rec_class": rec_class,
        "reason": reason,
    }


def get_headlines():
    rss_url = "https://finance.yahoo.com/rss/headline?s=NVDA"
    feed = feedparser.parse(rss_url)
    headlines = [entry.title for entry in feed.entries[:5]]
    return "\n".join(f"- {h}" for h in headlines) or "No headlines available right now."


def render_html(today, snapshot, headlines_text):
    return f"""

<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>NVDA Daily Report</title>
<style>
body {{ font-family: Arial; background:#f4f6f9; margin:20px; }}
.card {{ background:white; padding:25px; border-radius:12px; margin-bottom:20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
h1, h2 {{ margin:0 0 10px 0; }}
.metric {{ margin-bottom:10px; }}
.recommendation {{ font-size:28px; font-weight:bold; padding:10px; border-radius:8px; text-align:center; margin-top:15px; }}
.buy {{ background-color: #e6f9ec; color: #0a8a34; }}
.hold {{ background-color: #fff7e6; color: #b7791f; }}
.sell {{ background-color: #fde8e8; color: #c53030; }}
.analysis-text {{ margin-top:10px; line-height:1.6; white-space: pre-line; }}
.footer {{ font-size:12px; color:#666; text-align:center; margin-top:30px; }}
</style>
</head>
<body>

<div class=\"card\">
<h1>NVDA Daily Stock Report</h1>
<p><strong>Date:</strong> <span id="report-date">{today}</span></p>
<div class=\"metric\"><strong>Price:</strong> {snapshot['price']}</div>
<div class=\"metric\"><strong>PE Ratio:</strong> {snapshot['pe_ratio']}</div>
<div class=\"metric\"><strong>EPS:</strong> {snapshot['eps']}</div>
<div class=\"metric\"><strong>Market Cap:</strong> {snapshot['market_cap']}</div>
<div class=\"recommendation {snapshot['rec_class']}\">{snapshot['recommendation']}</div>
<p>{snapshot['reason']}</p>
</div>

<div class=\"card\">
<h2>Latest News</h2>
<div class=\"analysis-text\">{headlines_text}</div>
</div>

<div class=\"footer\">
Disclaimer: This report is automatically generated for educational purposes only and does not constitute financial advice.
</div>

<script>
const dateEl = document.getElementById("report-date");
if (dateEl) {{
  dateEl.textContent = new Date().toISOString().slice(0, 10);
}}
</script>

</body>
</html>
"""

def main():
    today = datetime.now().strftime("%Y-%m-%d")

    snapshot = {
        "price": "N/A",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "market_cap": "N/A",
        "recommendation": "HOLD",
        "rec_class": "hold",
        "reason": "Live market data is being refreshed. Please check back shortly.",
    }

    try:
        snapshot = get_stock_snapshot()
    except Exception as exc:
        print(f"Stock data fetch failed: {exc}")

    try:
        headlines_text = get_headlines()
    except Exception as exc:
        print(f"News fetch failed: {exc}")
        headlines_text = "No headlines available right now."

    html_content = render_html(today, snapshot, headlines_text)

    os.makedirs("report", exist_ok=True)
    for output_path in ["index.html", "report/index.html"]:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(html_content)

    print("NVDA daily report generated successfully.")


if __name__ == "__main__":
    main()
    
