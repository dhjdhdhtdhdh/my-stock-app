import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="오씨의 주식 공부 - 마스터 대시보드", layout="wide")

# 2. 상단 레이아웃: 제목 및 시장 지수(Index)
st.title("오씨의 주식 공부 📈")

# 주요 지수 정보 가져오기
@st.cache_data(ttl=600)
def get_market_indices():
    indices = {"KOSPI": "^KS11", "KOSDAQ": "^KQ11", "S&P 500": "^GSPC", "나스닥": "^IXIC", "필라델피아 반도체": "^SOX"}
    idx_data = []
    for name, ticker in indices.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            curr = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change = ((curr - prev) / prev) * 100
            idx_data.append({"지수명": name, "현재가": f"{curr:,.2f}", "등락률": change})
        except: continue
    return idx_data

idx_list = get_market_indices()
if idx_list:
    cols = st.columns(len(idx_list))
    for i, idx in enumerate(idx_list):
        with cols[i]:
            st.metric(label=idx['지수명'], value=idx['현재가'], delta=f"{idx['등락률']:.2f}%")

st.divider()

# 3. 초광역 섹터 맵 (섹터별 10개 종목 고정)
MONITOR_MAP = {
    "💾 반도체 및 소부장 (K-Stock)": {
        "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "한미반도체": "042700.KS", 
        "리노공업": "058470.KQ", "HPSP": "403870.KQ", "가온칩스": "399720.KQ", 
        "이오테크닉스": "039030.KQ", "제주반도체": "080220.KQ", "주성엔지니어링": "036930.KQ", "원익IPS": "240810.KQ"
    },
    "🌐 글로벌 Tech & AI (U.S. Stock)": {
        "NVIDIA": "NVDA", "Apple": "AAPL", "Microsoft": "MSFT", "Alphabet": "GOOGL",
        "Amazon": "AMZN", "Meta": "META", "Tesla": "TSLA", "Broadcom": "AVGO", 
        "AMD": "AMD", "Palantir": "PLTR"
    },
    "🔋 2차전지 & 소재": {
        "LG엔솔": "373220.KS", "에코프로": "086520.KQ", "에코프로비엠": "247540.KQ",
        "포스코홀딩스": "005490.KS", "포스코퓨처엠": "003670.KS", "삼성SDI": "006400.KS", 
        "엘앤에프": "066970.KQ", "금양": "001570.KS", "엔켐": "348370.KQ", "나노신소재": "121600.KQ"
    },
    "🦾 AI·로봇·우주항공": {
        "레인보우로보틱스": "272210.KQ", "두산로보틱스": "454910.KS", "뉴로메카": "348340.KQ",
        "한화에어로": "012450.KS", "LIG넥스원": "079550.KS", "한국항공우주": "047810.KS",
        "현대로템": "064350.KS", "IONQ": "IONQ", "Joby": "JOBY", "LUNR": "LUNR"
    },
    "💊 바이오 & 헬스케어": {
        "삼성바이오": "207940.KS", "셀트리온": "068270.KS", "알테오젠": "196170.KQ",
        "HLB": "028300.KQ", "유한양행": "000100.KS", "한미약품": "128940.KS", 
        "SK바이오팜": "326030.KS", "Eli Lilly": "LLY", "Novo Nordisk": "NVO", "Vertex": "VRTX"
    },
    "📈 주요 지수 ETF": {
        "KODEX 레버리지": "122630.KS", "KODEX 인버스": "114800.KS", "KODEX 200": "069500.KS",
        "TQQQ": "TQQQ", "SQQQ": "SQQQ", "SOXL": "SOXL", "SCHD": "SCHD", "JEPI": "JEPI", "QLD": "QLD", "QQQ": "QQQ"
    }
}

# 4. 데이터 수집 및 가치 분석 함수
def color_returns(val):
    color = '#e63946' if val > 0 else '#1d3557' if val < 0 else '#333'
    return f'color: {color}; font-weight: bold'

@st.cache_data(ttl=300)
def fetch_all_data(sector_map):
    all_data = []
    for section, stocks in sector_map.items():
        for name, ticker in stocks.items():
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="2mo")
                if hist.empty: continue
                
                info = t.info
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                
                all_data.append({
                    "섹터": section,
                    "명칭": name,
                    "1M 차트": hist['Close'].tail(20).tolist(),
                    "현재가": curr,
                    "거래량": hist['Volume'].iloc[-1],
                    "1일 전": ((curr - prev) / prev) * 100,
                    "1주 전": ((curr - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100,
                    "1개월 전": ((curr - hist['Close'].iloc[-21]) / hist['Close'].iloc[-21]) * 100,
                    "PER": info.get('trailingPE', 0),
                    "PBR": info.get('priceToBook', 0),
                    "ROE": info.get('returnOnEquity', 0) * 100,
                    "ticker": ticker
                })
            except: continue
    return pd.DataFrame(all_data)

# 5. 데이터 처리 및 출력
with st.spinner("전 섹터 데이터 동기화 중..."):
    full_df = fetch_all_data(MONITOR_MAP)

if not full_df.empty:
    # 5-1. 내부 데이터 기반 실시간 거래량 TOP 10 (가치 지표 포함)
    st.markdown("### 🔥 감시 종목 내 실시간 거래량 TOP 10")
    top_10 = full_df.sort_values(by='거래량', ascending=False).head(10).copy()
    top_10['현재가_표시'] = top_10.apply(lambda x: f"₩{x['현재가']:,.0f}" if any(ext in x['ticker'] for ext in [".KS", ".KQ"]) else f"${x['현재가']:,.2f}", axis=1)
    
    st.dataframe(
        top_10[['명칭', '현재가_표시', '1일 전', 'PER', 'PBR', 'ROE']].style.map(color_returns, subset=['1일 전']),
        hide_index=True, use_container_width=True
    )

    # 5-2. 초광역 섹터 맵 (섹터별 10개 고정 출력)
    for section in MONITOR_MAP.keys():
        st.markdown(f"### {section}")
        sector_df = full_df[full_df['섹터'] == section].copy()
        if not sector_df.empty:
            sector_df['거래량_표시'] = sector_df['거래량'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")
            sector_df['현재가_표시'] = sector_df.apply(lambda x: f"₩{x['현재가']:,.0f}" if any(ext in x['ticker'] for ext in [".KS", ".KQ"]) else f"${x['현재가']:,.2f}", axis=1)
            
            display_df = sector_df[['명칭', '1M 차트', '현재가_표시', '거래량_표시', '1일 전', '1주 전', '1개월 전']]
            styled_df = display_df.style.map(color_returns, subset=['1일 전', '1주 전', '1개월 전']).format({'1일 전': '{:+.2f}%', '1주 전': '{:+.2f}%', '1개월 전': '{:+.2f}%'})
            
            st.dataframe(styled_df, column_config={"1M 차트": st.column_config.LineChartColumn("최근 흐름", width="small")}, hide_index=True, use_container_width=True)

st.divider()
st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 오씨의 주식 공부 (Index & 가치지표 통합본)")
