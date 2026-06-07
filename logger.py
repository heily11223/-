import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr
from datetime import datetime
import os

# 1. 구글 시트 주소 (★본인 시트 링크로 변경 필수)
# ✅ 새로 넣을 부분 (본인 시트 ID와 방금 찾은 자산 탭의 gid 숫자를 넣으세요!)
csv_url = "https://docs.google.com/spreadsheets/d/1PQN3ef9KmynpP-P9GhBHdCVFXXto3_bG5HON8uLHaYE/export?format=csv&gid=0"
# 2. 데이터 및 가격 로드 함수
def load_portfolio(url):
    df = pd.read_csv(url).fillna(0)
    p_data = {"US_Stocks": {}, "KR_Stocks": {}, "Cash": {}}
    for _, row in df.iterrows():
        category = str(row['분류']).strip().upper()
        if category in ['0', '']: continue
        ticker = str(row['종목코드']).strip()
        
        try: shares = float(str(row['보유량']).replace(',', '').strip())
        except: shares = 0.0
            
        try: price = float(str(row['평단가']).replace(',', '').strip())
        except: price = 0.0
            
        if category == 'US': p_data["US_Stocks"][ticker] = {"shares": shares}
        elif category == 'KR': p_data["KR_Stocks"][ticker] = {"shares": shares}
        elif category == 'CASH': p_data["Cash"][f"{ticker}_CASH"] = {"amount": shares, "currency": ticker}
    return p_data

# 3. 실시간 가격 계산 로직
portfolio = load_portfolio(csv_url)
total_asset_krw = 0

try: usd_krw_rate = float(yf.Ticker("KRW=X").history(period="1d")['Close'].iloc[0])
except: usd_krw_rate = 1350.0

if "US_Stocks" in portfolio:
    for ticker, info in portfolio["US_Stocks"].items():
        try: price = float(yf.Ticker(ticker).history(period="5d")['Close'].iloc[-1])
        except: price = 0.0
        total_asset_krw += price * info["shares"] * usd_krw_rate

if "KR_Stocks" in portfolio:
    for ticker, info in portfolio["KR_Stocks"].items():
        try: price = int(fdr.DataReader(ticker)['Close'].iloc[-1])
        except: price = 0
        total_asset_krw += price * info["shares"]

if "Cash" in portfolio:
    for cash_id, info in portfolio["Cash"].items():
        if info["currency"] == "USD": total_asset_krw += info["amount"] * usd_krw_rate
        else: total_asset_krw += info["amount"]

# 4. CSV 파일에 기록하기
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
