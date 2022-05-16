
#imports 
import streamlit as st #for webapp
import yfinance as yf #information on stocks
import pandas as pd #display dataframe 
import cufflinks as cf #for plots 
import datetime #for query 

# App title
st.markdown('''
# Simple Stock/Crypto Price App
''')
st.write('---')

# Sidebar
st.sidebar.subheader('Time period')
start_date = st.sidebar.date_input("Start date", datetime.date(2020, 1, 1))
end_date = st.sidebar.date_input("End date", datetime.date(2022, 1, 31))

# Retrieving data
st.title("Enter symbol: ")
tickerSymbol = st.text_input("Example: AMD, TWTR, AAPL, TSLA, FB, BTC-USD, ETH-USD")
tickerData = yf.Ticker(tickerSymbol)
tickerDf = tickerData.history(period='1d', start=start_date, end=end_date) #get the historical prices for this ticker

# Ticker information
stock_logo = '<img src=%s>' % tickerData.info['logo_url']
st.markdown(stock_logo, unsafe_allow_html=True)

if "longName" in tickerData.info:
    stock_name = tickerData.info['longName']
    st.header('**%s**' % stock_name)
else:
    if "shortName" in tickerData.info:
        stock_name = tickerData.info['shortName'] #for crypto
        st.header('**%s**' % stock_name)


if "longBusinessSummary" in tickerData.info:
    stock_summary = tickerData.info['longBusinessSummary']
    st.write(stock_summary)
else:
    if "description" in tickerData.info:
        stock_summary = tickerData.info['description'] #for crypto
        st.write(stock_summary)

# Ticker data
st.header('**Ticker data**')
st.write(tickerDf)

# Bollinger bands
st.header('**Bollinger Bands**')
qf=cf.QuantFig(tickerDf,title='First Quant Figure',legend='top',name='GS')
qf.add_bollinger_bands()
fig = qf.iplot(asFigure=True)
st.plotly_chart(fig)

####
st.write('---')
st.header('** Raw Data**')
st.write(tickerData.info)