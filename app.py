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
        st.markdown("""
<head>
    <meta property="og:title" content="혁이의 통합 자산 관제소">
    <meta property="og:description" content="실시간 포트폴리오 모니터링 시스템">
    <meta property="og:image" content="https://github.com/heily11223/-/blob/main/bg.jpg?raw=true">
</head>
""", unsafe_allow_html=True)

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

import pandas as pd

# 1. 방금 복사한 구글 시트 링크를 아래 따옴표 안에 붙여넣으세요.
sheet_url = "https://docs.google.com/spreadsheets/d/1PQN3ef9KmynpP-P9GhBHdCVFXXto3_bG5HON8uLHaYE/edit?usp=sharing"

# 2. 파이썬이 읽을 수 있는 CSV 다운로드 링크로 자동 변환하는 꼼수입니다.
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

# 3. 구글 시트 데이터를 불러와서 포트폴리오 구조로 조립하는 함수 (강력 방어 로직 추가)
@st.cache_data(ttl=60)
def load_portfolio_from_gsheet(url):
    df = pd.read_csv(url)
    df = df.fillna(0) # 🛡️ 방어 1: 빈칸(NaN)이 있으면 무조건 0으로 채움
    
    p_data = {"US_Stocks": {}, "KR_Stocks": {}, "Cash": {}}
    
    for _, row in df.iterrows():
        category = str(row['분류']).strip().upper()
        if category == '0' or category == '': continue # 빈 줄 건너뛰기
        
        ticker = str(row['종목코드']).strip()
        name = str(row['종목명']).strip()
        
        # 🛡️ 방어 2: 숫자에 콤마(,)가 섞여있어도 강제로 제거하고 숫자로 변환
        try:
            shares = float(str(row['보유량']).replace(',', '').strip())
        except:
            shares = 0.0
            
        try:
            price = float(str(row['평단가']).replace(',', '').strip())
        except:
            price = 0.0
            
        # 🛡️ 방어 3: 평단가가 0원이면 이후 수익률 계산 시 0으로 나누기 에러가 나므로 아주 작은 값으로 대체
        if price == 0 and category != 'CASH': 
            price = 0.0001
        
        if category == 'US':
            p_data["US_Stocks"][ticker] = {"shares": shares, "avg_price": price, "color": "highlight", "title": name}
        elif category == 'KR':
            p_data["KR_Stocks"][ticker] = {"name": name, "shares": shares, "avg_price": price, "ticker": "KR_STOCK", "color": "highlight-kr"}
        elif category == 'CASH':
            p_data["Cash"][f"{ticker}_CASH"] = {"name": name, "amount": shares, "currency": ticker}
            
    return p_data
# 조립 완료된 데이터를 기존 시스템에 장착
portfolio = load_portfolio_from_gsheet(csv_url)

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
total_invested_krw = 0  # ★ 총 매입 원금을 담을 그릇 추가
pie_data = []

cards_html = '<div class="card-grid">'

# 미국 주식 처리
if "US_Stocks" in portfolio:
    for ticker, info in portfolio["US_Stocks"].items():
        current_price = get_us_price(ticker, info["avg_price"])
        current_value_usd = current_price * info["shares"]
        current_value_krw = current_value_usd * usd_krw_rate
        
        total_asset_krw += current_value_krw
        total_invested_krw += (info["avg_price"] * info["shares"] * usd_krw_rate) # ★ 원금 더하기
        
        yield_pct = ((current_price - info["avg_price"]) / info["avg_price"]) * 100 if info["avg_price"] > 0 else 0
        yield_color = "#FF3366" if yield_pct < 0 else "#00FF66" 
        yield_sign = "+" if yield_pct > 0 else ""
        
        pie_data.append({"종목명": info["title"], "평가액": current_value_krw})
        
        cards_html += f"""<div class="cyber-card">
<div class="badge"><span class="dot dot-us"></span>US 직투</div>
<div class="card-ticker">{ticker}</div>
<div class="card-title" style="color: #00E5FF;">{info["title"]}</div>
<div class="card-price">평단가 : ${info["avg_price"]:,.2f} &nbsp;|&nbsp; 현재가 : ${current_price:,.2f}</div>
<div class="card-price">보유량 : {info["shares"]}주 / <span class="{info.get('color', 'highlight')}">₩{int(current_value_krw):,}</span> <span style="color:{yield_color}; font-weight:800; font-size:14px; margin-left:8px; text-shadow: 0px 1px 3px rgba(0,0,0,0.8);">{yield_sign}{yield_pct:.2f}%</span></div>
</div>"""

# 한국 주식 처리
if "KR_Stocks" in portfolio:
    for ticker, info in portfolio["KR_Stocks"].items():
        current_price = get_kr_price(ticker, info["avg_price"])
        current_value_krw = current_price * info["shares"]
        
        total_asset_krw += current_value_krw
        total_invested_krw += (info["avg_price"] * info["shares"]) # ★ 원금 더하기
        
        yield_pct = ((current_price - info["avg_price"]) / info["avg_price"]) * 100 if info["avg_price"] > 0 else 0
        yield_color = "#FF3366" if yield_pct < 0 else "#00FF66"
        yield_sign = "+" if yield_pct > 0 else ""
        
        pie_data.append({"종목명": info["name"], "평가액": current_value_krw})
        
        cards_html += f"""<div class="cyber-card">
<div class="badge"><span class="dot dot-kr"></span>{info["ticker"]}</div>
<div class="card-ticker">{ticker}</div>
<div class="card-title" style="color: #00FF66;">{info["name"]}</div>
<div class="card-price">평단가 : ₩{info["avg_price"]:,.0f} &nbsp;|&nbsp; 현재가 : ₩{current_price:,.0f}</div>
<div class="card-price">보유량 : {info["shares"]}주 / <span class="{info.get('color', 'highlight-kr')}">₩{int(current_value_krw):,}</span> <span style="color:{yield_color}; font-weight:800; font-size:14px; margin-left:8px; text-shadow: 0px 1px 3px rgba(0,0,0,0.8);">{yield_sign}{yield_pct:.2f}%</span></div>
</div>"""

# 현금 자산 처리 로직
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
        total_invested_krw += current_value_krw # ★ 현금은 원금=평가액 동일하므로 그대로 더함
        
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

# ★ 추가: 건실청년에게 후원하기 버튼 (클릭 시 계좌번호 자동 복사)
# ★ 추가: 건실청년에게 후원하기 버튼 (아이프레임 보안 우회 버전)
import streamlit.components.v1 as components
components.html(
    """
    <div style="text-align: center; margin-bottom: 15px;">
        <button onclick="copyAccount()" 
            style="
                background: linear-gradient(45deg, #FF9F00, #FF3366);
                color: white; 
                border: none; 
                padding: 12px 35px; 
                border-radius: 8px; 
                font-family: 'Pretendard', sans-serif;
                font-size: 16px; 
                font-weight: 900; 
                cursor: pointer; 
                box-shadow: 0px 4px 15px rgba(255, 159, 0, 0.3);
                transition: all 0.3s ease;
                width: 100%;
                max-width: 320px;
                letter-spacing: -0.5px;
            "
            onmouseover="this.style.transform='scale(1.03)'; this.style.boxShadow='0px 6px 20px rgba(255, 51, 102, 0.5)';"
            onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0px 4px 15px rgba(255, 159, 0, 0.3)';"
        >
            💰 건실청년에게 후원하기
        </button>
    </div>

    <script>
        function copyAccount() {
            // 눈에 보이지 않는 임시 텍스트 입력창을 만듭니다.
            var tempInput = document.createElement('input');
            tempInput.value = '토스뱅크 1000-8439-7555'; // ★ 여기에 본인 계좌번호 입력
            document.body.appendChild(tempInput);
            
            // 임시 창의 텍스트를 선택하고 강제 복사 명령을 내립니다. (구형/모바일 브라우저 호환)
            tempInput.select();
            tempInput.setSelectionRange(0, 99999); 
            
            try {
                document.execCommand('copy');
                alert('⚡ 건실청년의 계좌번호가 복사되었습니다!\\n(토스뱅크 1000-8439-7555)');
            } catch (err) {
                alert('복사 권한이 차단되었습니다. 수동으로 복사해주세요: 토스뱅크 1000-8439-7555');
            }
            
            // 임시 창을 다시 지웁니다.
            document.body.removeChild(tempInput);
        }
    </script>
    """,
    height=85
)

# ★ 총 수익률 및 손익 계산 로직
total_pnl = total_asset_krw - total_invested_krw
total_yield_pct = (total_pnl / total_invested_krw) * 100 if total_invested_krw > 0 else 0
pnl_color = "#FF3366" if total_pnl < 0 else "#00FF66"  # 마이너스면 핑크, 플러스면 네온그린
pnl_sign = "+" if total_pnl > 0 else ""

# 총 자산 요약 (높이와 여백을 압축하여 공간 확보)
st.markdown(f"""
<div style="background-color:rgba(14, 17, 23, 0.2); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); border:1px solid rgba(31, 35, 51, 0.5); border-radius:8px; padding:20px; text-align:center; margin-bottom:20px; box-shadow: 0px 10px 30px rgba(0,0,0,0.5);">
    <div style="color:#a0a6b5; font-size:14px; font-weight:600; margin-bottom:5px; text-shadow: 0px 2px 4px rgba(0,0,0,0.8);">TOTAL ASSET (KRW)</div>
    <div style="color:#ffffff; font-size:36px; font-weight:900; letter-spacing:-1px; text-shadow: 0px 4px 15px rgba(0,0,0,1);">₩{int(total_asset_krw):,}</div>
    <div style="color:{pnl_color}; font-size:16px; font-weight:700; margin-top:5px; text-shadow: 0px 2px 5px rgba(0,0,0,0.8);">({pnl_sign}{int(total_pnl):,} &nbsp; {pnl_sign}{total_yield_pct:.2f}%)</div>
    <div style="color:#a0a6b5; font-size:12px; margin-top:10px; text-shadow: 0px 1px 3px rgba(0,0,0,0.8);">적용 환율 : ₩{usd_krw_rate:,.2f}</div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 📈 자산 성장 히스토리 (Total Asset 바로 아래로 이동)
# ==========================================
history_csv_url = "https://raw.githubusercontent.com/heily11223/-/main/history.csv"

@st.cache_data(ttl=60)
def load_history(url):
    try:
        df = pd.read_csv(url)
        return df
    except:
        return pd.DataFrame(columns=["날짜", "총자산"])

df_history = load_history(history_csv_url)

if not df_history.empty and len(df_history) > 0:
    st.markdown('<h3 style="color:white; font-size:16px; margin-bottom:10px; text-shadow: 0px 4px 10px rgba(0,0,0,0.9);">📈 자산 성장 추이</h3>', unsafe_allow_html=True)
    
    dates = pd.to_datetime(df_history['날짜'])
    df_history['날짜_표시'] = dates.dt.month.astype(str) + "." + dates.dt.day.astype(str)
    df_history['총자산(만원)'] = (df_history['총자산'] / 10000).astype(int)
    
    fig_line = px.line(df_history, x='날짜_표시', y='총자산(만원)', markers=True)
    
    fig_line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='Pretendard'), 
        margin=dict(t=10, b=10, l=10, r=10), # 좌우 여백을 최소화
        xaxis=dict(
            showgrid=False, 
            color='#8C92A4', 
            title='', 
            type='category',
            fixedrange=True,
            tickfont=dict(size=11) # 모바일용으로 X축 글자 크기 축소
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(45, 49, 66, 0.3)', 
            color='#8C92A4',
            title='', 
            fixedrange=True,
            side='right',          # ★ 핵심: 세로축 숫자를 주식 앱처럼 우측으로 이동!
            ticksuffix='만',       # 공간 절약을 위해 '만원' 대신 '만'으로 축약
            tickfont=dict(size=11) # 모바일용으로 Y축 글자 크기 축소
        ),
        hovermode="x unified",
        height=220, # 모바일에서 한눈에 들어오는 황금비율 높이
        showlegend=False
    )
    
    fig_line.update_traces(
        line=dict(color='#00E5FF', width=3),
        marker=dict(size=8, color='#00FF66', line=dict(width=2, color='#ffffff')),
        hovertemplate='%{y:,}만원' # 터치했을 때는 '만원'까지 풀로 보여줌
    )
    
    st.markdown('<div style="border: 1px solid rgba(31, 35, 51, 0.5); border-radius: 8px; padding: 15px 5px; margin-bottom: 25px; background-color: rgba(14, 17, 23, 0.4); box-shadow: 0px 4px 15px rgba(0,0,0,0.3); backdrop-filter: blur(10px);">', unsafe_allow_html=True)
    
    st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
# ==========================================
# 레이아웃 나누기 (계좌별 상세 & 포트폴리오 비중)
col_cards, col_chart = st.columns([1.8, 1])

# ... (이후 기존 코드 유지) ...
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
