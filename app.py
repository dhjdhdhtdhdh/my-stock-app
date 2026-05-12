import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="오씨의 주식 공부", layout="wide")

# 2. 상단 헤더 및 시장 정보
col_title, col_info = st.columns([2, 1])
with col_title:
    st.title("오씨의 주식 공부 📈")
    st.caption("KOSPI & NASDAQ 실시간 모멘텀 트래킹 (거래량 Top 10)")

with col_info:
    st.info(f"""
    🕒 **KOSPI (한국):** 09:00 - 15:30 KST  
    🕒 **NASDAQ (미국):** 22:30 - 05:00 KST (서머타임 적용)    """)

# 3. 섹터별 종목 리스트
SECTOR_MAP = {
    "💾 반도체": {
        "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "한미반도체": "042700.KS", 
        "DB하이텍": "000990.KS", "리노공업": "058470.KQ", "원익IPS": "240810.KQ", 
        "HPSP": "403870.KQ", "고영": "098460.KQ", "주성엔지니어링": "036930.KQ", "이오테크닉스": "039030.KQ"
    },
    "🚗 자동차 & 전장": {
        "현대차": "005380.KS", "기아": "000270.KS", "현대모비스": "012330.KS", 
        "현대오토에버": "307950.KS", "HL만도": "204320.KS", "현대위아": "011210.KS", 
        "에스엘": "005850.KS", "서연이화": "200880.KS", "화신": "010690.KS", "성우하이텍": "015750.KQ"
    },
    "🔋 2차전지": {
        "LG에너지솔루션": "373220.KS", "POSCO홀딩스": "005490.KS", "삼성SDI": "006400.KS", 
        "LG화학": "051910.KS", "에코프로비엠": "247540.KQ", "에코프로": "086520.KQ", 
        "포스코퓨처엠": "003670.KS", "엘앤에프": "066970.KQ", "SK이노베이션": "096770.KS", "엔켐": "348370.KQ"
    },
    "🌐 글로벌 Tech": {
        "Apple": "AAPL", "Microsoft": "MSFT", "Google": "GOOGL", "Amazon": "AMZN", 
        "Meta": "META", "Tesla": "TSLA", "Broadcom": "AVGO", "Qualcomm": "QCOM", 
        "Netflix": "NFLX", "Adobe": "ADBE"
    },
    "🤖 AI (소프트웨어/HW)": {
        "NVIDIA": "NVDA", "AMD": "AMD", "Palantir": "PLTR", "C3.ai": "AI", 
        "SoundHound AI": "SOUN", "BigBear.ai": "BBAI", "Synopsys": "SNPS", 
        "Cadence": "CDNS", "Super Micro Computer": "SMCI", "ARM": "ARM"
    },
    "🚀 New Tech (양자/로봇/우주)": {
        "IONQ": "IONQ", "Joby Aviation": "JOBY", "Lockheed Martin": "LMT", 
        "Intuitive Machines": "LUNR", "레인보우로보틱스": "272210.KQ", "두산로보틱스": "454910.KS",
        "Rigetti Computing": "RGTI", "Quantum Computing": "QUBT", "현대로템": "064350.KS", "뉴로메카": "348340.KQ"
    }
}

# 4. 데이터 수집 함수
@st.cache_data(ttl=300)
def fetch_sector_metrics(companies):
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
                "기업명": name,
                "1M 차트": hist['Close'].tail(20).tolist(),
                "현재가": curr,
                "거래량": vol,
                "1일 전": ((curr - p_1d) / p_1d) * 100,
                "1주 전": ((curr - p_1w) / p_1w) * 100,
                "1개월 전": ((curr - p_1m) / p_1m) * 100,
                "ticker": ticker
            })
        except: continue
    return data_list

# 💡 등락률 색상 지정 함수
def color_returns(val):
    if val > 0: color = '#e63946' # 빨간색
    elif val < 0: color = '#000080' # 파란색
    else: color = '#333'
    return f'color: {color}; font-weight: bold'

# 5. 대시보드 출력
for sector_name, companies in SECTOR_MAP.items():
    st.markdown(f"### {sector_name}")
    
    with st.spinner(f"{sector_name} 분석 중..."):
        raw_data = fetch_sector_metrics(companies)
        top_10 = sorted(raw_data, key=lambda x: x['거래량'], reverse=True)[:10]
        
        if top_10:
            df = pd.DataFrame(top_10)
            
            # 포맷팅 준비
            df['거래량_표시'] = df['거래량'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")
            df['현재가_표시'] = df.apply(lambda x: f"₩{x['현재가']:,.0f}" if ".KS" in x['ticker'] or ".KQ" in x['ticker'] else f"${x['현재가']:,.2f}", axis=1)

            # 표시용 데이터프레임 구성
            display_df = df[['기업명', '1M 차트', '현재가_표시', '거래량_표시', '1일 전', '1주 전', '1개월 전']]
            
            # 색상 및 숫자 포맷 적용 (Pandas 2.1.0+ 버전 대응)
            styled_df = display_df.style.map(color_returns, subset=['1일 전', '1주 전', '1개월 전']).format({'1일 전': '{:+.2f}%', '1주 전': '{:+.2f}%', '1개월 전': '{:+.2f}%'})

            # 데이터프레임 출력 (이 부분의 들여쓰기가 styled_df와 같아야 합니다)
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
        else:
            st.warning(f"{sector_name} 데이터를 불러올 수 없습니다.")

st.divider()
st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 오씨의 주식 공부")
