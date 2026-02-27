import yfinance as yf
import requests
import os
from datetime import datetime
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1️⃣ Fetch NVDA data
ticker = yf.Ticker("NVDA")
hist = ticker.history(period="1d")

price = hist["Close"].iloc[-1]
info = ticker.info

pe_ratio = info.get("trailingPE", "N/A")
market_cap = info.get("marketCap", "N/A")
eps = info.get("trailingEps", "N/A")

# 2️⃣ Get recent news headlines
news_items = ticker.news[:5]
headlines = []

for item in news_items:
    headlines.append(item.get("title", ""))

news_text = "\n".join(headlines)

# 3️⃣ Ask AI for analysis
prompt = f"""
You are a professional financial analyst.

Analyze NVIDIA (NVDA) using the following data:

Price: {price}
PE Ratio: {pe_ratio}
EPS: {eps}
Market Cap: {market_cap}

Recent News Headlines:
{news_text}

Provide:
1. Short professional analysis (3-5 paragraphs)
2. Clear final recommendation: BUY, HOLD, or SELL
3. Confidence level (Low / Moderate / High)

Be objective and balanced.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.4,
)

analysis = response.choices[0].message.content

# 4️⃣ Generate HTML
today = datetime.now().strftime("%Y-%m-%d")

html_content = f"""
<!DOCTYPE html>
<html>
<head>
<title>NVDA Daily AI Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    background-color: #f4f6f8;
}}
.card {{
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}}
</style>
</head>
<body>
<div class="card">
<h1>NVDA Daily AI Stock Report</h1>
<p><strong>Date:</strong> {today}</p>

<h2>Market Data</h2>
<p><strong>Price:</strong> ${price:.2f}</p>
<p><strong>PE Ratio:</strong> {pe_ratio}</p>
<p><strong>EPS:</strong> {eps}</p>
<p><strong>Market Cap:</strong> {market_cap}</p>

<h2>AI Analysis</h2>
<p>{analysis.replace(chr(10), "<br>")}</p>

<hr>
<p style="font-size:12px;">
Disclaimer: This AI-generated report is for educational purposes only and does not constitute financial advice.
</p>
</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("AI-powered NVDA report generated successfully.")
