from numpy import exp
import yfinance as yf
import pandas as pd
import numpy as np

aapl = yf.Ticker('SE')
price = aapl.history(period='5y')['Close']

# show financials
financials = aapl.financials
quarterly_financials = aapl.quarterly_financials

# show balance sheet
balance_sheet = aapl.balance_sheet
quarterly_balance_sheet = aapl.quarterly_balance_sheet

# show cashflow
cash_flow = aapl.cashflow
quarterly_cashflow = aapl.quarterly_cashflow

# show earnings
earnings = aapl.earnings
quarterly_earnings = aapl.quarterly_earnings

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
    table['Revenue Growth'] = rev_growth
    table['Net Profit Growth'] = income_growth
    table['Net Profit Margin'] = table['Net Income'] / table['Total Revenue'] * 100
    table['Positive OCF'] = table['Total Cash From Operating Activities']>0
    table['Current Ratio'] = table['Total Current Assets'] / table['Total Liab']
    table['Debt/Equity'] = (table['Short Long Term Debt']+table['Long Term Debt']) / table['Total Stockholder Equity']
    table['Return On Equity'] = table['Net Income'] / table['Total Stockholder Equity'] * 100
    return table.transpose().replace(0, np.nan)

table = createTable(financials, balance_sheet, cash_flow, price)
table2 = createTable(quarterly_financials, quarterly_balance_sheet, quarterly_cashflow, price)