import datetime
import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.express as px


st.set_page_config(
    page_title="Likelion AI School 주가 일별시세 App",
    page_icon="📈",
    layout="wide",
)

st.sidebar.header('검색어를 선택해 주세요.')

# Sidebar - year
thisyear = datetime.datetime.today().year
selected_year = st.sidebar.selectbox('Year', list(reversed(range(2010, thisyear+1))))

# Sidebar - ticker
unique_ticker = ["GOOGL", "AMD", "TSLA", "NVDA", "XOM"]
tickerSymbol = st.sidebar.selectbox('Ticker', unique_ticker)

# Sidebar - display_chart
display_chart = ["시세표", "종가", "거래량", "전일비"]
selected_chart = st.sidebar.multiselect('display chart', display_chart, display_chart)

# get data on this ticker
tickerDf = fdr.DataReader(tickerSymbol, str(selected_year))

st.write(f"""
# {tickerSymbol} 주식 일별 시세 📈
* 왼쪽에서 항목을 선택해 주세요.
""")


if "시세표" in selected_chart:
    st.write("## 시세표")
    st.dataframe(tickerDf)

if "종가" in selected_chart:   
    st.write("## 종가")
    px_close = px.line(tickerDf[["Close"]])
    px_close

if "거래량" in selected_chart:  
    st.write("## 거래량")
    px_volumne = px.bar(tickerDf[["Volume"]])
    px_volumne