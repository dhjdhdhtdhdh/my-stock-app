import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="오씨의 주식 공부 - 완결본", layout="wide")

# 2. 상단 시장 지수(Index) 섹션
@st.cache_data(ttl=600)
def get_market_indices():
    indices = {
        "KOSPI": "^KS11", 
        "KOSDAQ": "^KQ11", 
        "S&P 500": "^GSPC", 
        "나스닥": "^IXIC", 
        "필라델피아 반도체": "^SOX"
    }
    idx_data = []
    for name, ticker in indices.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) < 2: continue
            curr, prev = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
            idx_data.append({"지수명": name, "현재가": f"{curr:,.2f}", "등락률": ((curr - prev) / prev) * 100})
        except: continue
    return idx_data

st.title("오씨의 주식 공부 📈")
idx_list = get_market_indices()
if idx_list:
    cols = st.columns(len(idx_list))
    for i, idx in enumerate(idx_list):
        with cols[i]:
            st.metric(label=idx['지수명'], value=idx['현재가'], delta=f"{idx['등락률']:.2f}%")

st.divider()

# 3. 분석 Remark 생성 로직 (오승진 님 기준 반영)
def get_remark(per, pbr, roe):
    reasons = []
    # PER: 10~15배 이하 저평가, 30배 이상 성장주
    if 0 < per <= 15: reasons.append("저PER(저평가)")
    elif per >= 30: reasons.append("성장주(고PER)")
    
    # PBR: 1배 미만 자산가치 우수
    if 0 < pbr <= 1: reasons.append("자산가치 우수")
    
    # ROE: 10% 이상 우량 기업
    if roe >= 10: reasons.append("수익성(ROE) 우량")
    elif roe < 0: reasons.append("적자 주의")
    
    return " / ".join(reasons) if reasons else "모멘텀 관찰"

# 4. 초광역 섹터 맵 데이터 수집 (섹터별 10개)
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
    "🪙 가상자산 & 핀테크": {
        "비트코인(BTC)": "BTC-USD", "이더리움(ETH)": "ETH-USD", "코인베이스": "COIN",
        "마이크로스트래티지": "MSTR", "우리기술투자": "041190.KQ", "한화투자증권": "003530.KS",
        "Block": "SQ", "PayPal": "PYPL", "Robinhood": "HOOD", "갤럭시디지털": "GLXY.TO"
    },
    "📈 주요 지수 ETF": {
        "KODEX 레버리지": "122630.KS", "KODEX 인버스": "114800.KS", "KODEX 200": "069500.KS",
        "TQQQ": "TQQQ", "SQQQ": "SQQQ", "SOXL": "SOXL", "SCHD": "SCHD", "JEPI": "JEPI", "QLD": "QLD", "QQQ": "QQQ"
    }
}

@st.cache_data(ttl=300)
def fetch_sector_data(stocks):
    data_list = []
    for name, ticker in stocks.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2mo")
            if hist.empty: continue
            
            info = t.info
            curr, prev = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
            
            # 지표 추출 (여러 필드 시도로 누락 방지)
            per = info.get('trailingPE') or info.get('forwardPE') or 0
            pbr = info.get('priceToBook') or 0
            roe = (info.get('returnOnEquity') or 0) * 100
            
            data_list.append({
                "명칭": name, "1M 차트": hist['Close'].tail(20).tolist(),
                "현재가": curr, "거래량": hist['Volume'].iloc[-1],
                "1일 전": ((curr - prev) / prev) * 100,
                "1주 전": ((curr - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100,
                "1개월 전": ((curr - hist['Close'].iloc[-21]) / hist['Close'].iloc[-21]) * 100,
                "PER": round(per, 1) if per > 0 else "-",
                "PBR": round(pbr, 1) if pbr > 0 else "-",
                "ROE": round(roe, 1) if roe != 0 else "-",
                "Remark": get_remark(per, pbr, roe),
                "ticker": ticker
            })
        except: continue
    return data_list

def color_returns(val):
    if isinstance(val, (int, float)):
        color = '#e63946' if val > 0 else '#1d3557' if val < 0 else '#333'
        return f'color: {color}; font-weight: bold'
    return ''

# 5. 메인 화면 출력
for section, stocks in MONITOR_MAP.items():
    st.markdown(f"### {section}")
    raw_data = fetch_sector_data(stocks)
    if raw_data:
        df = pd.DataFrame(raw_data)
        # 포맷팅
        df['거래량_표시'] = df['거래량'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")
        df['현재가_표시'] = df.apply(lambda x: f"₩{x['현재가']:,.0f}" if any(ext in x['ticker'] for ext in [".KS", ".KQ"]) else f"${x['현재가']:,.2f}", axis=1)
        
        display_df = df[['명칭', '1M 차트', '현재가_표시', '거래량_표시', '1일 전', '1주 전', '1개월 전', 'PER', 'PBR', 'ROE', 'Remark']]
        
        # 스타일링 적용
        styled_df = display_df.style.map(color_returns, subset=['1일 전', '1주 전', '1개월 전']).format({
            '1일 전': '{:+.2f}%', '1주 전': '{:+.2f}%', '1개월 전': '{:+.2f}%'
        })
        
        st.dataframe(
            styled_df, 
            column_config={"1M 차트": st.column_config.LineChartColumn("최근 흐름", width="small")}, 
            hide_index=True, 
            use_container_width=True
        )

st.divider()
st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 가치 기준: PER 15↓, PBR 1↓, ROE 10%↑")
