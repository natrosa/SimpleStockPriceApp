
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

# Plot raw data
def plot_raw_data():
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
	fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
	fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
	st.plotly_chart(fig)
	
plot_raw_data()


# Predict forecast with Prophet.
df_train = data[['Date','Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

# Show and plot forecast
st.subheader('Forecast data')
st.write(forecast.tail())
    
st.write(f'Forecast plot for {n_years} years')
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)

st.write("Forecast components")
fig2 = m.plot_components(forecast)
st.write(fig2)





####
st.write('---')
st.header('** Raw Data**')
st.write(tickerData.info)