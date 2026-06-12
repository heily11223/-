import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr
import requests
import re
from datetime import datetime
import os

# 1. 구글 시트 주소 (★본인 시트 링크)
csv_url = "https://docs.google.com/spreadsheets/d/1PQN3ef9KmynpP-P9GhBHdCVFXXto3_bG5HON8uLHaYE/export?format=csv&gid=0"

# 2. 데이터 및 평단가 로드 함수 (유령 행 방어벽 추가)
def load_portfolio(url):
    df = pd.read_csv(url).fillna(0)
    p_data = {"US_Stocks": {}, "KR_Stocks": {}, "Cash": {}}
    for _, row in df.iterrows():
        category = str(row['분류']).strip().upper()
        ticker = str(row['종목코드']).strip()
        
        # 🛡️ 유령 행 방어: 빈칸이거나 0이면 건너뜀
        if category in ['0', '', 'NAN', 'NONE'] or ticker in ['0', '', 'NAN', 'NONE']: 
            continue
        
        try: shares = float(str(row['보유량']).replace(',', '').strip())
        except: shares = 0.0
            
        try: price = float(str(row['평단가']).replace(',', '').strip())
        except: price = 0.0
            
        if category == 'US': p_data["US_Stocks"][ticker] = {"shares": shares, "avg_price": price}
        elif category == 'KR': p_data["KR_Stocks"][ticker] = {"shares": shares, "avg_price": price}
        elif category == 'CASH': p_data["Cash"][f"{ticker}_CASH"] = {"amount": shares, "currency": ticker}
    return p_data

# 3. 안전한 가격 추출 함수들 (데이터 누락 & 금현물 방어)
def get_us_price(ticker, fallback_price):
    try:
        df = yf.Ticker(ticker).history(period="5d")
        if df.empty or 'Close' not in df.columns: return fallback_price
        closed_series = df['Close'].dropna()
        if closed_series.empty: return fallback_price
        return float(closed_series.iloc[-1])
    except:
        return fallback_price

def get_kr_price(ticker, fallback_price):
    # 🌟 특수 센서: 금현물(M04020000) 네이버 강제 추출
    if ticker == 'M04020000':
        try:
            url = "https://finance.naver.com/marketindex/"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get(url, headers=headers, timeout=5)
            res.encoding = 'euc-kr'
            match = re.search(r'국내 금.*?<span class="value">([\d,\.]+)</span>', res.text, re.DOTALL)
            if match:
                return int(float(match.group(1).replace(',', '')))
        except:
            return fallback_price
            
    # 일반 한국 주식
    try:
        df = fdr.DataReader(ticker)
        if df.empty or 'Close' not in df.columns: return fallback_price
        closed_series = df['Close'].dropna()
        if closed_series.empty: return fallback_price
        return int(closed_series.iloc[-1])
    except:
        return fallback_price

# ====================================================
# 4. 실시간 총자산 계산 로직
# ====================================================
portfolio = load_portfolio(csv_url)
total_asset_krw = 0

# 스마트 환율 백업 로직
try:
    usd_krw_rate = float(yf.Ticker("KRW=X").history(period="7d")['Close'].dropna().iloc[-1])
except:
    try:
        usd_krw_rate = float(fdr.DataReader('USD/KRW')['Close'].dropna().iloc[-1])
    except:
        usd_krw_rate = 1380.0

if "US_Stocks" in portfolio:
    for ticker, info in portfolio["US_Stocks"].items():
        current_price = get_us_price(ticker, info["avg_price"])
        total_asset_krw += current_price * info["shares"] * usd_krw_rate

if "KR_Stocks" in portfolio:
    for ticker, info in portfolio["KR_Stocks"].items():
        current_price = get_kr_price(ticker, info["avg_price"])
        total_asset_krw += current_price * info["shares"]

if "Cash" in portfolio:
    for cash_id, info in portfolio["Cash"].items():
        if info["currency"] == "USD": total_asset_krw += info["amount"] * usd_krw_rate
        else: total_asset_krw += info["amount"]

# ====================================================
# 5. CSV 파일에 기록하기
# ====================================================
today_str = datetime.now().strftime("%Y-%m-%d")
new_data = pd.DataFrame({"날짜": [today_str], "총자산": [int(total_asset_krw)]})

file_name = "history.csv"
if os.path.exists(file_name):
    history_df = pd.read_csv(file_name)
    history_df = pd.concat([history_df, new_data], ignore_index=True)
else:
    history_df = new_data

# 같은 날짜에 여러 번 돌면 중복되지 않게 마지막 기록만 남김
history_df = history_df.drop_duplicates(subset=['날짜'], keep='last')
history_df.to_csv(file_name, index=False)
print(f"✅ {today_str} 자동 기록 완료: {int(total_asset_krw)}원")
