import yfinance as yf
import pandas as pd
import streamlit as st
import numpy as np
import os

st.cache()
def createTable(finance, balancesheet, cashflow, price):
    cols_bs = ['Total Assets', 'Total Current Assets', 'Total Liab','Short Long Term Debt', 'Long Term Debt', 'Total Stockholder Equity']
    col_cf = ['Total Cash From Operating Activities','Capital Expenditures']
    table = pd.DataFrame(finance.transpose()[['Total Revenue', 'Net Income', 'Total Operating Expenses']])
    for col in cols_bs:
        try: table[col] = balancesheet.transpose()[col]
        except: table[col] = table['Net Income'] * 0
    for col in col_cf:
        try: table[col] = cashflow.transpose()[col]
        except: table[col] = table['Net Income'] * 0
    table['Free Cash Flow'] = table['Total Cash From Operating Activities'] + table['Capital Expenditures']
    table = table/1e6 #shown in millions
    price_val = []
    for t in table.index:
        tx = price.index.get_loc(t, method='nearest')
        price_val.append(price.iloc[tx])
    table['Price'] = price_val
    rev_growth, income_growth = [], []
    for t in range(len(table.index)-1):
        rev_growth.append((table['Total Revenue'].iloc[t]/table['Total Revenue'].iloc[t+1]-1)*100)
        income_growth.append((table['Net Income'].iloc[t]/table['Net Income'].iloc[t+1]-1)*100)
    rev_growth.append(None)
    income_growth.append(None)
    table['Revenue Growth (%)'] = rev_growth
    table['Net Profit Growth (%)'] = income_growth
    table['Net Profit Margin (%)'] = table['Net Income'] / table['Total Revenue'] * 100
    table['Positive OCF ?'] = table['Total Cash From Operating Activities']>0
    table['Current Ratio'] = table['Total Current Assets'] / table['Total Liab']
    table['Debt/Equity'] = (table['Short Long Term Debt']+table['Long Term Debt']) / table['Total Stockholder Equity']
    table['Return On Equity (%)'] = table['Net Income'] / table['Total Stockholder Equity'] * 100
    return table.transpose().replace(0, np.nan)

def exportTable(ticker, table, type='Annually'):
    #get period of table
    startY, stopY = table.columns[-1].year, table.columns[0].year
    startM, stopM = table.columns[-1].month, table.columns[0].month
    os.makedirs(os.path.dirname('./database/stock/{}/'.format(ticker)),exist_ok=True) #create folder
    if type == 'Annually':
        table.to_csv('./database/stock/{}/{}_Financials_{}_{}.csv'.format(ticker, ticker, startY, stopY))
    else:
        table.to_csv('./database/stock/{}/{}_Financials_Quarter_{}_{}_{}_{}.csv'.format(ticker, ticker, startY, startM, stopY, stopM))