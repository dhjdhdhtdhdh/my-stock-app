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
    st.title("오씨의 주식 공부 📈")
    st.caption("반도체·ETF·코인·광물 - 글로벌 자산 실시간 모니터링")

with col_info:
    st.info(f"""
    🇰🇷 **KOSPI/KOSDAQ:** 09:00 - 15:30  
    🇺🇸 **NASDAQ/NYSE:** 22:30 - 05:00 (서머타임)
    """)

# 3. 고정 감시 종목 리스트 (정교화된 섹터)
MONITOR_MAP = {
    "💾 국내 반도체 및 소부장": {
        "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "한미반도체": "042700.KS", 
        "DB하이텍": "000990.KS", "리노공업": "058470.KQ", "HPSP": "403870.KQ", 
        "가온칩스": "399720.KQ", "제주반도체": "080220.KQ"
    },
    "🌐 글로벌 Tech & AI": {
        "NVIDIA": "NVDA", "Apple": "AAPL", "Microsoft": "MSFT", "Tesla": "TSLA",
        "AMD": "AMD", "Broadcom": "AVGO", "ASML": "ASML", "TSMC": "TSM"
    },
    "📊 주요 ETF (지수 및 레버리지)": {
        "KODEX 200": "069500.KS", "KODEX 레버리지": "122630.KS", "KODEX 200선물인버스2X": "252670.KS",
        "TQQQ (나스닥 3배)": "TQQQ", "SOXL (반도체 3배)": "SOXL", "SQQQ (나스닥 인버스)": "SQQQ",
        "SCHD (배당성장)": "SCHD"
    },
    "💎 광물 & 코인 (원자재/암호화폐)": {
        "포스코홀딩스(리튬)": "005490.KS", "에코프로(소재)": "086520.KQ", "비트코인(BTC-USD)": "BTC-USD",
        "Coinbase(코인거래소)": "COIN", "MicroStrategy(비트코인)": "MSTR", "금(Gold)": "GC=F",
        "구리(Copper)": "HG=F", "리튬 아메리카스": "LAC"
    }
}

# 4. 데이터 수집 및 스타일 함수
@st.cache_data(ttl=300)
def fetch_data(companies):
    data_list = []
    for name, ticker in companies.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2mo")
            if hist.empty or len(hist) < 21: continue
            curr = hist['Close'].iloc[-1]
            vol = hist['Volume'].iloc[-1]
            p_1d, p_1w, p_1m = hist['Close'].iloc[-2], hist['Close'].iloc[-6], hist['Close'].iloc[-21]
            data_list.append({
                "명칭": name, "1M 차트": hist['Close'].tail(20).tolist(),
                "현재가": curr, "거래량": vol,
                "1일 전": ((curr - p_1d) / p_1d) * 100, "1주 전": ((curr - p_1w) / p_1w) * 100,
                "1개월 전": ((curr - p_1m) / p_1m) * 100, "ticker": ticker
            })
        except: continue
    return data_list

@st.cache_data(ttl=60)
def get_naver_quant(): # 네이버 실시간 거래량 상위
    try:
        url = "https://finance.naver.com/sise/sise_quant.naver"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        df = pd.read_html(res.text, encoding='euc-kr')[1].dropna(subset=['종목명'])
        return df[['종목명', '현재가', '등락률', '거래량']].head(10)
    except: return None

def color_returns(val):
    color = '#e63946' if val > 0 else '#1d3557' if val < 0 else '#333'
    return f'color: {color}; font-weight: bold'

# 5. 화면 출력
# 5-1. 실시간 급등/거래량 상위 (네이버 데이터)
st.markdown("### 🔥 국내 시장 실시간 거래량 TOP 10")
quant_df = get_naver_quant()
if quant_df is not None:
    st.dataframe(quant_df, use_container_width=True, hide_index=True)
else:
    st.write("실시간 데이터를 불러올 수 없습니다.")

# 5-2. 섹터별 상세 모니터링
for section, stocks in MONITOR_MAP.items():
    st.markdown(f"### {section}")
    raw_data = fetch_data(stocks)
    if raw_data:
        df = pd.DataFrame(raw_data)
        df['현재가_표시'] = df.apply(lambda x: f"₩{x['현재가']:,.0f}" if any(ext in x['ticker'] for ext in [".KS", ".KQ"]) else f"${x['현재가']:,.2f}" if "USD" not in x['ticker'] else f"${x['현재가']:,.0f}", axis=1)
        df['거래량_표시'] = df['거래량'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")
        
        display_df = df[['명칭', '1M 차트', '현재가_표시', '거래량_표시', '1일 전', '1주 전', '1개월 전']]
        styled_df = display_df.style.map(color_returns, subset=['1일 전', '1주 전', '1개월 전']).format({'1일 전': '{:+.2f}%', '1주 전': '{:+.2f}%', '1개월 전': '{:+.2f}%'})
        
        st.dataframe(styled_df, column_config={"1M 차트": st.column_config.LineChartColumn("최근 흐름", width="small")}, hide_index=True, use_container_width=True)

st.divider()
st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 오씨의 주식 공부")
