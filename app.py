import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="오씨의 주식 공부", layout="wide")

# 2. 상단 헤더 및 시장 정보
col_title, col_info = st.columns([2, 1])
with col_title:
    st.title("오씨의 주식 공부 📊")
    st.caption("초광역 섹터 모니터링 - 거래량 및 모멘텀 분석")

with col_info:
    st.info(f"""
    🇰🇷 **K-Market:** 09:00 - 15:30 | 🇺🇸 **U.S. Market:** 22:30 - 05:00
    """)

# 3. 섹터 구성 (이전 섹터 리스트 유지)
MONITOR_MAP = {
    "💾 반도체 & 소부장": {
        "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "한미반도체": "042700.KS", 
        "리노공업": "058470.KQ", "HPSP": "403870.KQ", "가온칩스": "399720.KQ", "NVDA": "NVDA", "TSMC": "TSM"
    },
    "🔋 2차전지 & 리튬": {
        "LG엔솔": "373220.KS", "에코프로": "086520.KQ", "포스코홀딩스": "005490.KS", 
        "에코프로비엠": "247540.KQ", "엘앤에프": "066970.KQ", "테슬라": "TSLA", "리튬아메리카스": "LAC"
    },
    "🦾 로봇 & AI & 우주": {
        "레인보우로보틱스": "272210.KQ", "두산로보틱스": "454910.KS", "마이크로소프트": "MSFT",
        "팔란티어": "PLTR", "한화에어로스페이스": "012450.KS", "IONQ": "IONQ"
    },
    "🪙 가상자산 & 핀테크": {
        "비트코인(BTC)": "BTC-USD", "코인베이스": "COIN", "마이크로스트래티지": "MSTR",
        "우리기술투자": "041190.KQ", "한화투자증권": "003530.KS"
    },
    "📈 주요 ETF & 지수": {
        "KODEX 레버리지": "122630.KS", "KODEX 인버스": "114800.KS", "TQQQ": "TQQQ", 
        "SOXL": "SOXL", "SCHD": "SCHD"
    }
}

# 4. 데이터 수집 및 색상 함수
@st.cache_data(ttl=300)
def fetch_data(companies):
    data_list = []
    for name, ticker in companies.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2mo")
            if hist.empty: continue
            curr = hist['Close'].iloc[-1]
            vol = hist['Volume'].iloc[-1]
            p_1d, p_1w, p_1m = hist['Close'].iloc[-2], hist['Close'].iloc[-6], hist['Close'].iloc[-21]
            data_list.append({
                "명칭": name, "1M 차트": hist['Close'].tail(20).tolist(),
                "현재가": curr, "거래량": vol,
                "1일 전": ((curr - p_1d) / p_1d) * 100, 
                "1주 전": ((curr - p_1w) / p_1w) * 100,
                "1개월 전": ((curr - p_1m) / p_1m) * 100, "ticker": ticker
            })
        except: continue
    return data_list

@st.cache_data(ttl=60)
def get_naver_quant():
    url = "https://finance.naver.com/sise/sise_quant.naver"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        df_list = pd.read_html(res.text, encoding='euc-kr')
        for df in df_list:
            if '종목명' in df.columns and len(df) > 10:
                df = df.dropna(subset=['종목명'])
                return df[['종목명', '현재가', '등락률', '거래량']].head(10)
    except: return None

def color_returns(val):
    color = '#e63946' if val > 0 else '#1d3557' if val < 0 else '#333'
    return f'color: {color}; font-weight: bold'

# 5. 화면 출력
st.markdown("### 🔥 K-Market 실시간 거래량 TOP 10")
quant_df = get_naver_quant()
if quant_df is not None:
    st.table(quant_df)
else:
    st.warning("실시간 랭킹 데이터를 불러올 수 없습니다. 잠시 후 새로고침 하세요.")

for section, stocks in MONITOR_MAP.items():
    st.markdown(f"### {section}")
    raw_data = fetch_data(stocks)
    if raw_data:
        df = pd.DataFrame(raw_data)
        
        # 포맷팅: 거래량 추가
        df['거래량_표시'] = df['거래량'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")
        df['현재가_표시'] = df.apply(lambda x: f"₩{x['현재가']:,.0f}" if any(ext in x['ticker'] for ext in [".KS", ".KQ"]) else f"${x['현재가']:,.2f}", axis=1)
        
        # 표시용 DF 구성
        display_df = df[['명칭', '1M 차트', '현재가_표시', '거래량_표시', '1일 전', '1주 전', '1개월 전']]
        
        # 스타일링
        styled_df = display_df.style.map(color_returns, subset=['1일 전', '1주 전', '1개월 전']).format({
            '1일 전': '{:+.2f}%', '1주 전': '{:+.2f}%', '1개월 전': '{:+.2f}%'
        })
        
        st.dataframe(
            styled_df, 
            column_config={
                "1M 차트": st.column_config.LineChartColumn("최근 흐름", width="small"),
                "현재가_표시": "현재가",
                "거래량_표시": "거래량"
            }, 
            hide_index=True, 
            use_container_width=True
        )

st.divider()
st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 오씨의 주식 공부")
