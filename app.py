import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="오씨의 주식 공부", layout="wide")

# 2. 실시간 네이버 데이터 수집 함수 (보안 강화)
@st.cache_data(ttl=60)
def get_naver_quant():
    # 네이버 금융 거래량 상위 페이지
    url = "https://finance.naver.com/sise/sise_quant.naver"
    
    # 세션을 사용하여 연결 유지 및 브라우저 위장 강화
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://finance.naver.com/'
    }
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        # 만약 lxml에서 에러가 난다면 'html5lib'으로 엔진 변경 시도
        df_list = pd.read_html(response.text, encoding='euc-kr', flavor='lxml')
        
        for df in df_list:
            # 거래량 상위 테이블은 보통 컬럼 수가 많고 '종목명'이 포함됨
            if '종목명' in df.columns and len(df) > 50:
                # 불필요한 빈 행 제거 및 상위 10개 추출
                df = df.dropna(subset=['종목명']).reset_index(drop=True)
                res_df = df[['종목명', '현재가', '등락률', '거래량']].head(10)
                # 등락률 텍스트 정리 (상한/하한 등의 글자 제거)
                res_df['등락률'] = res_df['등락률'].astype(str).str.replace('상한', '').str.replace('하한', '').str.strip()
                return res_df
            
    except Exception as e:
        # 에러 로그 출력 (디버깅용)
        print(f"Error fetching Naver data: {e}")
        return None
    return None
# 네이버 실패 시 카카오, 삼성전자 등 주요 대형주 실시간 정보로 대체 출력
              quant_df = fetch_data(major_tickers) # 기존에 만든 fetch_data 함수 재활용
# 3. 레이아웃: 제목 및 시장 정보 (에러 발생 지점 수정)
col_title, col_info = st.columns([2, 1])
with col_title:
    st.title("오씨의 주식 공부 📈")
    st.caption("글로벌 테크·반도체·AI·에너지 - 초광역 섹터 모멘텀 감시")

with col_info:
    st.info(f"🇰🇷 K-Market: 09:00 - 15:30 | 🇺🇸 U.S. Market: 22:30 - 05:00")

# 4. 실시간 거래량 TOP 10 출력
st.markdown("### 🔥 K-Market 실시간 거래량 TOP 10")
with st.spinner("실시간 데이터를 가져오는 중..."):
    quant_df = get_naver_quant()

if quant_df is not None:
    st.dataframe(quant_df, use_container_width=True, hide_index=True)
else:
    st.warning("실시간 랭킹 데이터를 일시적으로 불러올 수 없습니다. GitHub의 requirements.txt를 확인해 주세요.")

# 5. 초광역 섹터 맵 구성 (섹터별 10개)
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

# 6. 데이터 수집 및 스타일 함수
def color_returns(val):
    color = '#e63946' if val > 0 else '#1d3557' if val < 0 else '#333'
    return f'color: {color}; font-weight: bold'

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

# 7. 섹터별 대시보드 출력
for section, stocks in MONITOR_MAP.items():
    st.markdown(f"### {section}")
    raw_data = fetch_data(stocks)
    if raw_data:
        df = pd.DataFrame(raw_data)
        df['거래량_표시'] = df['거래량'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")
        df['현재가_표시'] = df.apply(lambda x: f"₩{x['현재가']:,.0f}" if any(ext in x['ticker'] for ext in [".KS", ".KQ"]) else f"${x['현재가']:,.2f}", axis=1)
        
        display_df = df[['명칭', '1M 차트', '현재가_표시', '거래량_표시', '1일 전', '1주 전', '1개월 전']]
        styled_df = display_df.style.map(color_returns, subset=['1일 전', '1주 전', '1개월 전']).format({'1일 전': '{:+.2f}%', '1주 전': '{:+.2f}%', '1개월 전': '{:+.2f}%'})
        
        st.dataframe(styled_df, column_config={"1M 차트": st.column_config.LineChartColumn("최근 흐름", width="small")}, hide_index=True, use_container_width=True)

st.divider()
st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 오씨의 주식 공부")
