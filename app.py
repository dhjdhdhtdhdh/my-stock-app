import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="오씨의 주식 공부", layout="wide")

# 2. 실시간 네이버 데이터 수집 함수 (강화 버전)
@st.cache_data(ttl=60)
def get_naver_quant():
    url = "https://finance.naver.com/sise/sise_quant.naver"
    # 브라우저인 것처럼 속이는 헤더 (보안 우회)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Referer': 'https://finance.naver.com/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # lxml 엔진을 사용하여 모든 테이블을 읽어옴
        df_list = pd.read_html(response.text, encoding='euc-kr', flavor='lxml')
        
        for df in df_list:
            # '종목명' 컬럼이 있고 데이터가 충분한 테이블 찾기
            if '종목명' in df.columns and len(df) > 50:
                df = df.dropna(subset=['종목명'])
                # 필요한 컬럼만 추출 및 정리
                res_df = df[['종목명', '현재가', '등락률', '거래량']].head(10).reset_index(drop=True)
                # 등락률 등에 붙은 불필요한 문자 제거
                res_df['등락률'] = res_df['등락률'].astype(str).str.replace('상한', '').str.replace('하한', '').str.strip()
                return res_df
    except Exception as e:
        return None
    return None

# 3. 화면 출력 부분 (이전 코드의 상단에 배치하세요)
st.title("오씨의 주식 공부 📈")
st.markdown("### 🔥 K-Market 실시간 거래량 TOP 10")

with st.spinner("실시간 랭킹 정보를 가져오는 중..."):
    quant_df = get_naver_quant()
with col_info:
    st.info(f"🇰🇷 K-Market: 09:00 - 15:30 | 🇺🇸 U.S. Market: 22:30 - 05:00")

if quant_df is not None:
    # 표를 더 깔끔하게 보기 위해 st.table 대신 st.dataframe 사용
    st.dataframe(
        quant_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("⚠️ 실시간 데이터를 불러올 수 없습니다. GitHub의 requirements.txt에 'lxml'이 포함되어 있는지 확인하거나 잠시 후 다시 시도해 주세요.")

# 이후 기존의 섹터별 MONITOR_MAP 출력 코드를 이어 붙이시면 됩니다.


# 3. 초광역 섹터 맵 (섹터별 10개 종목 구성)
MONITOR_MAP = {
    "💾 반도체 및 소부장 (K-Stock)": {
        "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "한미반도체": "042700.KS", 
        "리노공업": "058470.KQ", "HPSP": "403870.KQ", "가온칩스": "399720.KQ", 
        "이오테크닉스": "039030.KQ", "제주반도체": "080220.KQ", "주성엔지니어링": "036930.KQ", "원익IPS": "240810.KQ"
    },
    "🌐 글로벌 Tech & AI (U.S. Stock)": {
        "NVIDIA": "NVDA", "Apple": "AAPL", "Microsoft": "MSFT", "Alphabet(Google)": "GOOGL",
        "Amazon": "AMZN", "Meta": "META", "Tesla": "TSLA", "Broadcom": "AVGO", 
        "AMD": "AMD", "Palantir": "PLTR"
    },
    "🔋 2차전지 & 소재": {
        "LG에너지솔루션": "373220.KS", "에코프로": "086520.KQ", "에코프로비엠": "247540.KQ",
        "포스코홀딩스": "005490.KS", "포스코퓨처엠": "003670.KS", "엘앤에프": "066970.KQ", 
        "삼성SDI": "006400.KS", "금양": "001570.KS", "엔켐": "348370.KQ", "나노신소재": "121600.KQ"
    },
    "🤖 AI·로봇·우주항공": {
        "레인보우로보틱스": "272210.KQ", "두산로보틱스": "454910.KS", "뉴로메카": "348340.KQ",
        "한화에어로스페이스": "012450.KS", "LIG넥스원": "079550.KS", "한국항공우주": "047810.KS",
        "현대로템": "064350.KS", "IONQ": "IONQ", "Joby Aviation": "JOBY", "Intuitive Machines": "LUNR"
    },
    "💊 바이오 & 헬스케어": {
        "삼성바이오로직스": "207940.KS", "셀트리온": "068270.KS", "알테오젠": "196170.KQ",
        "HLB": "028300.KQ", "유한양행": "000100.KS", "한미약품": "128940.KS", 
        "SK바이오팜": "326030.KS", "Eli Lilly": "LLY", "Novo Nordisk": "NVO", "Vertex": "VRTX"
    },
    "☀️ 에너지 & 원자재 & 인프라": {
        "한화솔루션": "009830.KS", "씨에스윈드": "112610.KS", "두산에너빌리티": "034020.KS",
        "HD현대중공업": "329180.KS", "금(Gold)": "GC=F", "구리": "HG=F", 
        "천연가스": "NG=F", "WTI유": "CL=F", "리튬아메리카스": "LAC", "Freeport-McMoRan": "FCX"
    },
    "🪙 가상자산 & 핀테크": {
        "비트코인(BTC)": "BTC-USD", "이더리움(ETH)": "ETH-USD", "코인베이스": "COIN",
        "마이크로스트래티지": "MSTR", "우리기술투자": "041190.KQ", "한화투자증권": "003530.KS",
        "Block(Square)": "SQ", "PayPal": "PYPL", "Robinhood": "HOOD", "갤럭시디지털": "GLXY.TO"
    },
    "📈 주요 지수 ETF (Market)": {
        "KODEX 레버리지": "122630.KS", "KODEX 인버스": "114800.KS", "KODEX 200": "069500.KS",
        "TQQQ": "TQQQ", "SQQQ": "SQQQ", "SOXL": "SOXL", 
        "SOXS": "SOXS", "SCHD": "SCHD", "JEPI": "JEPI", "TSLY": "TSLY"
    }
}

# 4. 데이터 처리 로직
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
    st.warning("실시간 랭킹 데이터를 일시적으로 불러올 수 없습니다.")

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
