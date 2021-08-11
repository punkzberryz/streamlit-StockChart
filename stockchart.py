import streamlit as st
from streamlit import session_state as ss
import yfinance as yf
from readFinance import createTable, exportTable
import altair as alt
import pandas as pd

def extractData(type):
    if type == 'Annually':
        ss.balancesheet = ss.stock.balance_sheet
        ss.cashflow = ss.stock.cashflow
        ss.financials = ss.stock.financials
    else :
        ss.balancesheet = ss.stock.quarterly_balance_sheet
        ss.cashflow = ss.stock.quarterly_cashflow
        ss.financials = ss.stock.quarterly_financials

def plotTable(type='Annually'):
    extractData(type)
    ss.table = createTable(ss.financials, ss.balancesheet, ss.cashflow, ss.price)
    
    ss.pricechart = ss.price.reset_index().melt('Date')
    fig1 = alt.Chart(ss.pricechart).mark_line().encode(
            alt.X('Date',axis=alt.Axis(format='%b, %Y',labelAngle=-90)),
            alt.Y('value', title='Share Price ($)'),
            alt.Color('variable', title='', legend=None)
            # color='variable',
        ).properties(
            width=600,height=400,
        ).interactive()

    if ss.addplot is not 'None':
        ss.chart2 = ss.table.transpose()[ss.addplot].rename_axis('Date').reset_index().melt('Date')
        fig2 = alt.Chart(ss.chart2).mark_line().encode(
            alt.X('Date',axis=alt.Axis(format='%b, %Y',labelAngle=-90)),
            alt.Y('value', title=ss.addplot),
            alt.Color('variable', title='', legend=None)
        ).properties(width=600, height=400).interactive()
        fig = alt.layer(fig1, fig2).resolve_scale(y='independent')


    else: fig=fig1

    st.altair_chart(fig)

    st.write('''
        # {}
        ##### {}
        ##### Market Cap {} (Billion)
        ###### Number shown in millions
    '''.format(ss.name, ss.business_info, ss.marketcap))
    st.table(ss.table)
    # st.button('Export Table', on_click=exportTable, args=(ss.ticker, ss.table, type))


st.title('Stock Financial')
ss.ticker = st.text_input('Enter Stock ticker','AAPL')

ss.stock = yf.Ticker(ss.ticker)
col1, col2 = st.beta_columns(2)
with col1:
    ss.table_type = st.selectbox('Show by', ['Annually', 'Quarterly'])
with col2:
    ss.addplot = st.radio('Add plot', ['None', 'Total Revenue', 'Net Income', 'Free Cash Flow',
    'Net Profit Margin (%)', 'Return On Equity (%)'])


ss.name = ss.stock.info['longName']
ss.business_info = ss.stock.info['longBusinessSummary']
ss.marketcap = format(round(ss.stock.info['marketCap']/1e9,1),',')
ss.price = ss.stock.history(period='5y')['Close']
plotTable(ss.table_type)
