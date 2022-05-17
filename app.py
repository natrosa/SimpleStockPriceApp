
#imports 
import streamlit as st #for webapp
import yfinance as yf #information on stocks
import pandas as pd #display dataframe 
import cufflinks as cf #for plots 
import datetime #for query 

#for forecasting
from datetime import date
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
import plotly
from plotly import graph_objs as go

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


#Forecasting 
st.header('**Forecasting with Prophet**')
n_years = st.slider('Years of prediction:', 1, 4)
period = n_years * 365

@st.cache
def load_data_forecasting(ticker):
    data = yf.download(ticker, start_date, end_date)
    data.reset_index(inplace=True)
    return data

	
data_load_state = st.text('Loading data...')
data = load_data_forecasting(tickerSymbol)
data_load_state.text('Loading data... done!')

st.subheader('Raw data')
st.write(data.tail())

# Plot Raw data
trace_open = go.Scatter(
    x = data["Date"],
    y = data["Open"],
    mode = 'lines',
    name="Open"
)

trace_high = go.Scatter(
    x = data["Date"],
    y = data["High"],
    mode = 'lines',
    name="High"
)

trace_low = go.Scatter(
    x = data["Date"],
    y = data["Low"],
    mode = 'lines',
    name="Low"
)

trace_close = go.Scatter(
    x = data["Date"],
    y = data["Close"],
    mode = 'lines',
    name="Close"
)

data_traces = [trace_open,trace_high,trace_low,trace_close]
layout = go.Layout(title="Stock Price",xaxis_rangeslider_visible=True)
fig = go.Figure(data=data_traces,layout=layout)
st.plotly_chart(fig)


trace_volume = go.Scatter(
    x = data["Date"],
    y = data["Volume"],
    mode = 'lines',
    name="Volume"
)

data_volume = [trace_volume]
layout_volume = go.Layout(title="Volume",xaxis_rangeslider_visible=True)
fig_volume = go.Figure(data=data_volume,layout=layout_volume)
st.plotly_chart(fig_volume)

# Predict forecast with Prophet.
df_train = data[['Date','Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

df_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

trace_open = go.Scatter(
    x = df_forecast["ds"],
    y = df_forecast["yhat"],
    mode = 'lines',
    name="Forecast"
)

trace_high = go.Scatter(
    x = df_forecast["ds"],
    y = df_forecast["yhat_upper"],
    mode = 'lines',
    fill = "tonexty", 
    line = {"color": "#57b8ff"}, 
    name="Higher uncertainty interval"
)

trace_low = go.Scatter(
    x = df_forecast["ds"],
    y = df_forecast["yhat_lower"],
    mode = 'lines',
    fill = "tonexty", 
    line = {"color": "#57b8ff"}, 
    name="Lower uncertainty interval"
)


trace_close = go.Scatter(
    x = df_train["ds"],
    y = df_train["y"],
    name="Data values"
)

st.subheader('Forecast data')
data = [trace_open,trace_high,trace_low,trace_close]
layout = go.Layout(title="Stock Price Forecast",xaxis_rangeslider_visible=True)

fig_forecast = go.Figure(data=data,layout=layout)
st.plotly_chart(fig_forecast)

####
st.write('---')
st.header('** Raw Data**')
st.write(tickerData.info)