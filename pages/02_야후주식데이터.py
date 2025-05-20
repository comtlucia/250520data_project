import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📈 글로벌 시가총액 Top 10 기업 주가 변화 (최근 1년)")

# 시가총액 기준 글로벌 Top 10 기업 (2025년 기준 예상)
top10_tickers = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Saudi Aramco (2222.SR)": "2222.SR",
    "Alphabet (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Nvidia (NVDA)": "NVDA",
    "Berkshire Hathaway (BRK-B)": "BRK-B",
    "Meta Platforms (META)": "META",
    "TSMC (TSM)": "TSM",
    "Tesla (TSLA)": "TSLA"
}

# 기간 설정
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# 여러 주식 정보 가져오기
@st.cache_data
def fetch_data(ticker):
    df = yf.download(ticker, start=start_date, end=end_date)
    df["Symbol"] = ticker
    return df

# 데이터 취합
price_data = []
for name, ticker in top10_tickers.items():
    df = fetch_data(ticker)
    df["Name"] = name
    price_data.append(df)

# 병합
all_data = pd.concat(price_data)
all_data.reset_index(inplace=True)

# 사용자 선택
selected_names = st.multiselect("📌 표시할 기업을 선택하세요", options=list(top10_tickers.keys()), default=list(top10_tickers.keys())[:5])

# 시각화
fig = go.Figure()
for name in selected_names:
    company_df = all_data[all_data["Name"] == name]
    fig.add_trace(go.Scatter(x=company_df["Date"], y=company_df["Close"], mode='lines', name=name))

fig.update_layout(
    title="최근 1년간 주가 변화 (종가 기준)",
    xaxis_title="날짜",
    yaxis_title="종가 (USD or 현지 통화)",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

