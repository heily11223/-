import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
import plotly.express as px
import base64
import os

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="건실청년의 통합 자산 관리", 
    page_icon="⚡", 
    layout="wide"
)

# ==========================================
# 🖼️ 씹덕 감성 배경화면 주입 함수
def add_bg_from_local(image_file):
    # 폴더에 bg.jpg 파일이 있는지 확인 후 작동 (없으면 뻗지 않고 기본 테마 유지)
    if os.path.exists(image_file):
        with open(image_file, "rb") as file:
            encoded_string = base64.b64encode(file.read())
        
        st.markdown(
        f"""
        <style>
        .stApp {{
            /* 배경 위에 얇은 검은색 필터(0.6)를 씌워 글씨 가독성 확보 */
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                              url(data:image/{"jpg"};base64,{encoded_string.decode()});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
        )
    else:
        st.markdown("""<style>.stApp {background-color: #08090C; background-image: linear-gradient(#12141c 1px, transparent 1px), linear-gradient(90deg, #12141c 1px, transparent 1px); background-size: 40px 40px;}</style>""", unsafe_allow_html=True)

# 배경화면 적용 (확장자가 png라면 bg.png로 수정하세요)
add_bg_from_local('bg.png')

# ==========================================
# 🎨 프리텐다드 폰트 및 사이버펑크 투명 UI 커스텀 CSS 주입
custom_css = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* --- 🌟 사이버펑크 투명 카드 UI --- */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-top: 10px;
}

.cyber-card {
    /* 배경 60% 불투명도 + 블러 효과로 캐릭터가 은은하게 비침 */
    background-color: rgba(14, 17, 23, 0.6) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(31, 35, 51, 0.8);
    border-radius: 8px;
    padding: 24px;
    position: relative;
    transition: all 0.3s ease;
}

.cyber-card:hover {
    border-color: #00E5FF;
    box-shadow: 0px 0px 20px rgba(0, 229, 255, 0.15);
    transform: translateY(-2px);
    background-color: rgba(20, 22, 30, 0.7) !important;
}

.cyber-card::before { content: ''; position: absolute; top: -1px; left: -1px; width: 10px; height: 10px; border-top: 2px solid transparent; border-left: 2px solid transparent; transition: 0.3s;}
.cyber-card:hover::before { border-color: #00E5FF; }

.badge {
    display: inline-block;
    padding: 4px 10px;
    background-color: rgba(26, 28, 35, 0.8);
    border: 1px solid #2d3142;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    color: #a0a6b5;
    margin-bottom: 12px;
}
.dot { height: 6px; width: 6px; border-radius: 50%; display: inline-block; margin-right: 6px; vertical-align: middle; }
.dot-us { background-color: #00E5FF; }
.dot-kr { background-color: #00FF66; }
.dot-cash { background-color: #FF9F00; }
.highlight-cash { color: #FF9F00; font-weight: 700; font-size: 15px;}

.card-ticker { color: #8C92A4; font-size: 12px; font-weight: 600; letter-spacing: 1px; margin-bottom: 4px; text-shadow: 0px 2px 4px rgba(0,0,0,0.8); }
.card-title { color: #ffffff; font-size: 22px; font-weight: 800; margin-bottom: 15px; text-shadow: 0px 2px 6px rgba(0,0,0,0.8); }
.card-price { color: #E0E4EB; font-size: 13px; font-weight: 500; margin-bottom: 4px; text-shadow: 0px 1px 3px rgba(0,0,0,0.8); }
.highlight { color: #00E5FF; font-weight: 700; font-size: 15px;}
.highlight-kr { color: #00FF66; font-weight: 700; font-size: 15px;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ==========================================

st.markdown('<h1 style="color:white; font-weight:900; letter-spacing:-1px; text-shadow: 0px 4px 15px rgba(0,0,0,0.9);">⚡ 건실청년의 삶</h1>', unsafe_allow_html=True)

# 2. 내 보유 자산 수동 입력 (평단가 기준)
portfolio = {
    "US_Stocks": {
        "MSFU": {"shares": 115, "avg_price": 32.35, "color": "highlight", "title": "마이크로소프트 2X"},
        "METU": {"shares": 150, "avg_price": 25.01, "color": "highlight", "title": "메타 2X"},
        "LMT": {"shares": 5, "avg_price": 515.19, "color": "highlight", "title": "록히드마틴"}
    },
    "KR_Stocks": {
        "438910": {"name": "미국나스닥100레버리지(합성 H)", "shares": 0, "avg_price": 10000, "ticker": "ISA KODEX", "color": "highlight-kr"},
        "411060": {"name": "KRX 금현물", "shares": 0, "avg_price": 13000, "ticker": "SAFE ASSET", "color": "highlight-kr"}
    },
    "Cash": {
        "USD_CASH": {"name": "달러 현금 (예수금)", "amount": 25108.0, "currency": "USD"},  
        "KRW_CASH": {"name": "원화 현금 (CMA/파킹)", "amount": 8180000, "currency": "KRW"} 
    }
}

# 3. 실시간 가격 가져오기 로직
@st.cache_data(ttl=600)
def get_exchange_rate():
    try:
        krw_usd = yf.Ticker("KRW=X").history(period="1d")
        return float(krw_usd['Close'].iloc[0])
    except:
        return 1350.0 

@st.cache_data(ttl=600)
def get_us_price(ticker, fallback_price):
    try:
        df = yf.Ticker(ticker).history(period="5d")
        if df.empty or 'Close' not in df.columns: return fallback_price
        return float(df['Close'].iloc[-1])
    except:
        return fallback_price

@st.cache_data(ttl=600)
def get_kr_price(ticker, fallback_price):
    try:
        df = fdr.DataReader(ticker)
        if df.empty or 'Close' not in df.columns: return fallback_price
        return int(df['Close'].iloc[-1])
    except:
        return fallback_price

# --- 연산 및 HTML 카드 생성 ---
usd_krw_rate = get_exchange_rate()
total_asset_krw = 0
pie_data = []

cards_html = '<div class="card-grid">'

# 미국 주식 처리
for ticker, info in portfolio["US_Stocks"].items():
    current_price = get_us_price(ticker, info["avg_price"])
    current_value_usd = current_price * info["shares"]
    current_value_krw = current_value_usd * usd_krw_rate
    total_asset_krw += current_value_krw
    
    yield_pct = ((current_price - info["avg_price"]) / info["avg_price"]) * 100
    yield_color = "#FF3366" if yield_pct < 0 else "#00FF66" 
    yield_sign = "+" if yield_pct > 0 else ""
    
    pie_data.append({"종목명": info["title"], "평가액": current_value_krw})
    
    cards_html += f"""<div class="cyber-card">
<div class="badge"><span class="dot dot-us"></span>US 직투</div>
<div class="card-ticker">{ticker}</div>
<div class="card-title" style="color: #00E5FF;">{info["title"]}</div>
<div class="card-price">평단가 : ${info["avg_price"]:,.2f} &nbsp;|&nbsp; 현재가 : ${current_price:,.2f}</div>
<div class="card-price">보유량 : {info["shares"]}주 / <span class="{info['color']}">₩{int(current_value_krw):,}</span> <span style="color:{yield_color}; font-weight:800; font-size:14px; margin-left:8px; text-shadow: 0px 1px 3px rgba(0,0,0,0.8);">{yield_sign}{yield_pct:.2f}%</span></div>
</div>"""

# 한국 주식 처리
for ticker, info in portfolio["KR_Stocks"].items():
    current_price = get_kr_price(ticker, info["avg_price"])
    current_value_krw = current_price * info["shares"]
    total_asset_krw += current_value_krw
    
    yield_pct = ((current_price - info["avg_price"]) / info["avg_price"]) * 100
    yield_color = "#FF3366" if yield_pct < 0 else "#00FF66"
    yield_sign = "+" if yield_pct > 0 else ""
    
    pie_data.append({"종목명": info["name"], "평가액": current_value_krw})
    
    cards_html += f"""<div class="cyber-card">
<div class="badge"><span class="dot dot-kr"></span>{info["ticker"]}</div>
<div class="card-ticker">{ticker}</div>
<div class="card-title" style="color: #00FF66;">{info["name"]}</div>
<div class="card-price">평단가 : ₩{info["avg_price"]:,.0f} &nbsp;|&nbsp; 현재가 : ₩{current_price:,.0f}</div>
<div class="card-price">보유량 : {info["shares"]}주 / <span class="{info['color']}">₩{int(current_value_krw):,}</span> <span style="color:{yield_color}; font-weight:800; font-size:14px; margin-left:8px; text-shadow: 0px 1px 3px rgba(0,0,0,0.8);">{yield_sign}{yield_pct:.2f}%</span></div>
</div>"""

if "Cash" in portfolio:
    for cash_id, info in portfolio["Cash"].items():
        amount = info["amount"]
        if info["currency"] == "USD":
            current_value_krw = amount * usd_krw_rate
            price_str = f"${amount:,.2f}"
            badge_html = '<div class="badge"><span class="dot dot-us"></span>US 현금</div>'
            title_color = "#00E5FF"
        else:
            current_value_krw = amount
            price_str = f"₩{amount:,}"
            badge_html = '<div class="badge"><span class="dot dot-cash"></span>KRW 현금</div>'
            title_color = "#FF9F00"
        
        total_asset_krw += current_value_krw
        pie_data.append({"종목명": info["name"], "평가액": current_value_krw})
        
        cards_html += f"""<div class="cyber-card">
{badge_html}
<div class="card-ticker">{info["currency"]} CASH</div>
<div class="card-title" style="color: {title_color};">{info["name"]}</div>
<div class="card-price">보유 금액 : {price_str}</div>
<div class="card-price">원화 평가액 : <span class="highlight-cash" style="color:{title_color}">₩{int(current_value_krw):,}</span></div>
</div>"""

cards_html += '</div>'
df_pie = pd.DataFrame(pie_data)

# --- 화면 출력 ---
st.markdown("<br>", unsafe_allow_html=True)

# 총 자산 요약 (완전 투명 + 텍스트 그림자 강화)
st.markdown(f"""
<div style="background-color:rgba(14, 17, 23, 0.2); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); border:1px solid rgba(31, 35, 51, 0.5); border-radius:8px; padding:30px; text-align:center; margin-bottom:30px; box-shadow: 0px 10px 30px rgba(0,0,0,0.5);">
    <div style="color:#a0a6b5; font-size:16px; font-weight:600; margin-bottom:10px; text-shadow: 0px 2px 4px rgba(0,0,0,0.8);">TOTAL ASSET (KRW)</div>
    <div style="color:#ffffff; font-size:42px; font-weight:900; letter-spacing:-1px; text-shadow: 0px 4px 15px rgba(0,0,0,1);">₩{int(total_asset_krw):,}</div>
    <div style="color:#a0a6b5; font-size:13px; margin-top:10px; text-shadow: 0px 1px 3px rgba(0,0,0,0.8);">적용 환율 : ₩{usd_krw_rate:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# 레이아웃 나누기
col_cards, col_chart = st.columns([1.8, 1])

with col_cards:
    st.markdown('<h3 style="color:white; font-size:18px; margin-bottom:10px; text-shadow: 0px 4px 10px rgba(0,0,0,0.9);">01 &nbsp; 계좌별 종목 상세</h3>', unsafe_allow_html=True)
    st.markdown(cards_html, unsafe_allow_html=True)

with col_chart:
    st.markdown('<h3 style="color:white; font-size:18px; margin-bottom:10px; text-shadow: 0px 4px 10px rgba(0,0,0,0.9);">02 &nbsp; 포트폴리오 비중</h3>', unsafe_allow_html=True)
    
    fig = px.pie(df_pie, values='평가액', names='종목명', hole=0.5)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='Pretendard', size=14),
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=False 
    )
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(colors=['#00E5FF', '#00FF66', '#FF9F00', '#FF3366', '#9D00FF'], line=dict(color='rgba(14, 17, 23, 0.8)', width=2))
    )
    st.plotly_chart(fig, use_container_width=True)
