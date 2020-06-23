from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import datetime
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import date
import os

def add_manual_transaction(ticker,
                        txn_date,
                        txn_type,
                        stock_price,
                        qty):
    txn_master = import_txn_master(os.path.dirname(__file__) + '/data/txn_master.csv')
    df_to_add = pd.DataFrame({'txn_date':[txn_date], 'ticker':[ticker], 'qty':[qty], 'trade_type':[txn_type], 'unit_price':[stock_price],'source':['manual']})
    df_to_add['txn_date'] = pd.to_datetime(df_to_add['txn_date']).dt.date
    txn_master = txn_master.append(df_to_add, ignore_index=True)
    txn_master.sort_values(by=['txn_date'], inplace=True, ignore_index=True)
    txn_master.reset_index(inplace=True, drop=True)
    export_txn_master(txn_master)

def update_dividend_yields_records():
    """
    Update dividend yields for all stocks in daily record
    """
    df = import_daily_record(os.path.dirname(__file__) + '/data/daily_record.csv')
    stocks = df['ticker'].unique().tolist()
    dividend_yield = []
    last_dividend_per_stock = []
    yearly_dividend_count = []
    for ticker in stocks:
        temp = yf.Ticker(ticker)
        temp_df = temp.history(period='1y')
        temp_df['record_date'] = temp_df.index
        temp_df['record_date'] = pd.to_datetime(temp_df['record_date']).dt.date
        temp_df.sort_values(by=['record_date'], inplace=True, ignore_index=True)
        last_close_price = temp_df['Close'].iloc[-1]
        temp_df = temp_df[temp_df['Dividends'] > 0]
        if len(temp_df) > 0:
            yearly_dividend = sum(temp_df['Dividends'])
            ticker_dividend_yield = 100 * yearly_dividend / last_close_price
            dividend_yield.append(ticker_dividend_yield)
            last_dividend = temp_df['Dividends'].iloc[-1]
            last_dividend_per_stock.append(last_dividend)
            yearly_dividend_count.append(len(temp_df))
        else:
            dividend_yield.append(0)
            last_dividend_per_stock.append(0)
            yearly_dividend_count.append(0)
    data_to_write = pd.DataFrame({'ticker':stocks,
                                  'dividend_yield':dividend_yield,
                                  'last_dividend_per_stock':last_dividend_per_stock,
                                  'yearly_dividend_count':yearly_dividend_count})
    data_to_write.to_csv('/home/yash/Desktop/py/stock_app/stockapp/data/stock_dividend_yields.csv',
                         index=False)

def get_dividend_yields(stocks):
    """
    Return the ttm dividend yield of the stocks list.
    """
    df = pd.read_csv('/home/yash/Desktop/py/stock_app/stockapp/data/stock_dividend_yields.csv')
    df[['dividend_yield','last_dividend_per_stock','yearly_dividend_count']] = df[['dividend_yield','last_dividend_per_stock','yearly_dividend_count']].apply(pd.to_numeric)
    df[['ticker']] = df[['ticker']].astype(str)
    df = df.loc[df['ticker'].isin(stocks),]
    return df

def get_future_dividend(stocks):
    df = agg_data_by_x(stocks, 'ticker', None)
    df_dividend = get_dividend_yields(stocks)
    df = df.merge(df_dividend,how='left',left_on='ticker',right_on='ticker')
    df['future_1y_dividend_by_value'] = df['qty'] * df['last_dividend_per_stock'] * df['yearly_dividend_count']
    df['future_1y_dividend_by_yield'] = df['ttl_value'] * df['dividend_yield'] * 0.01
    return sum(df['future_1y_dividend_by_value']),sum(df['future_1y_dividend_by_yield'])

def get_past_dividends_agg(stocks):
    df = import_daily_record(os.path.dirname(__file__) + '/data/daily_record.csv')
    df = df.loc[df['ticker'].isin(stocks),]
    # df_sector = import_stock_categories()
    # df = df.merge(df_sector,how='left',left_on='ticker',right_on='ticker')
    df = df[df['dividends'] > 0]
    df['dividend_earned'] = df['dividends'] * df['qty']
    total_dividend_earned = sum(df['dividend_earned'])
    return total_dividend_earned

def get_stock_history(i_stock,
                      date_start,
                      date_end):
    """
    Get historical stock data from yfinance for the given date range.

    Unit test created.
    """
    df = yf.download(i_stock, start=date_start, end=date_end, actions=True)
    df['record_date'] = df.index
    df['record_date'] = pd.to_datetime(df['record_date']).dt.date
    df.rename(columns={'Close':'close_price', 'Dividends':'dividends', 'Stock Splits':'stock_split'},
              inplace=True)
    return df

def import_txn_master(path):
    """Import and return the txn master data as csv

    Unit test created.
    """
    df = pd.read_csv(path)
    df[['qty', 'unit_price']] = df[['qty', 'unit_price']].apply(pd.to_numeric)
    df[['ticker', 'trade_type', 'source']] = df[['ticker', 'trade_type', 'source']].astype(str)
    df['txn_date'] = pd.to_datetime(df['txn_date']).dt.date
    df.reset_index(inplace=True, drop=True)
    return df

def import_daily_record(path):
    """Import and return the daily record data as csv

    Unit test created.
    """
    df = pd.read_csv(path)
    df[['qty', 'unit_price', 'close_price','dividends']] = df[['qty', 'unit_price', 'close_price','dividends']].apply(pd.to_numeric)
    df[['ticker']] = df[['ticker']].astype(str)
    df['record_date'] = pd.to_datetime(df['record_date']).dt.date
    df.reset_index(inplace=True, drop=True)
    return df

def define_daily_record():
    column_names = ['record_date','ticker', 'qty', 'unit_price', 'close_price']
    df = pd.DataFrame(columns = column_names)
    df[['qty', 'unit_price', 'close_price']] = df[['qty', 'unit_price', 'close_price']].apply(pd.to_numeric)
    df[['ticker']] = df[['ticker']].astype(str)
    df['record_date'] = pd.to_datetime(df['record_date']).dt.date
    df.reset_index(inplace=True, drop=True)
    return df

def import_stock_categories():
    df = pd.read_csv('/home/yash/Desktop/py/stock_app/stockapp/data/stock_category.csv')
    df[['ticker','sector']] = df[['ticker','sector']].astype(str)
    df.reset_index(inplace=True, drop=True)
    return df

def export_txn_master(data_to_write):
    data_to_write.to_csv('/home/yash/Desktop/py/stock_app/stockapp/data/txn_master.csv',
                         index=False)

def export_daily_record(data_to_write):
    data_to_write.to_csv('/home/yash/Desktop/py/stock_app/stockapp/data/daily_record.csv',
                         index=False)

def update_m1_txn_database(input_data,
                        date_column,
                        tckr_column,
                        qty_column,
                        txn_type,
                        unit_price):
    txn_master = import_txn_master(os.path.dirname(__file__) + '/data/txn_master.csv')
    temp_txn_master = txn_master[txn_master['source'] == 'm1']
    input_data[date_column] = pd.to_datetime(input_data[date_column]).dt.date

    #find latest in both records
    latest_date = max(input_data[date_column])
    _latest_date = max(temp_txn_master['txn_date'])

    #subset and rows and columns which need to be added to txn_master
    if latest_date > _latest_date:
        input_data = input_data.loc[input_data[date_column] > _latest_date]
        new_data = input_data.loc[:,[date_column,tckr_column,qty_column,txn_type,unit_price]]
        new_data.rename(columns={date_column:'txn_date',
                                 tckr_column:'ticker',
                                 qty_column:'qty',
                                 txn_type:'trade_type',
                                 unit_price:'unit_price'},
                        inplace=True)
        new_data.loc[:,'source'] = 'm1'
    else:
        print('Txn already up to date.')
        return
    
    txn_master = txn_master.append(new_data,ignore_index = True)
    txn_master.reset_index(inplace=True, drop=True)
    export_txn_master(txn_master)

def update_daily_snapshot():
    #import transactio and record datasets.
    txn_master = import_txn_master(os.path.dirname(__file__) + '/data/txn_master.csv')
    daily_record = define_daily_record()

    ##################################################
    # txn_master = txn_master.loc[txn_master['ticker'].isin(['AAPL','MMM']),]
    txn_master.reset_index(inplace=True, drop=True)
    if len(txn_master) == 0:
        print('No transactions to update.')
        return
    
    #List of all stocks in txn
    stocks = txn_master['ticker'].unique()
    print('Stocks to update:',stocks)

    #create start and end date variables
    date_start = min(txn_master['txn_date'])
    date_end = date.today()
    print('Updating records from %s to %s' % (date_start, date_end))

    #create list of dates from start to end date
    date_range = [date_start + datetime.timedelta(days=x) for x in range(0, (date_end - date_start).days + 1)]

    #for each date to be updates
    for i_stock in stocks:
        print('Updating %s.' % i_stock)
        
        #get transactions from i_stock
        i_stock_txn = txn_master.loc[txn_master['ticker'] == i_stock,]
        i_stock_txn = i_stock_txn.sort_values(by=['txn_date'], ignore_index=True)
        i_stock_txn.reset_index(drop=True, inplace=True)

        #get stock price data using yfinance
        i_stock_data = get_stock_history(i_stock,
                                         date_start,
                                         date_end + datetime.timedelta(days=1))

        #define default stock value and unit_price
        i_stock_current_qty = 0.000000
        i_stock_current_unit_price = 0.000000
        
        # join transactions to date list
        new_txn = pd.DataFrame({'record_date':date_range})
        new_txn = new_txn.merge(i_stock_txn,
                                left_on='record_date',
                                right_on='txn_date',
                                how='left')
        new_txn = new_txn.sort_values(by=['record_date'], ignore_index=True)
        new_txn.reset_index(inplace=True, drop=True)
        new_txn.loc[np.isnan(new_txn['qty']), 'qty'] = 0.000000
        new_txn.loc[np.isnan(new_txn['unit_price']), 'unit_price'] = 0.000000
        new_txn['trade_type'] = new_txn['trade_type'].replace(np.nan, '', regex=True)

        #assign the ticker variable
        new_txn.loc[:, 'ticker'] = i_stock

        #join close price (right join to remove days when market closed).
        if len(i_stock_data) > 0:
            new_txn = new_txn.merge(i_stock_data.loc[:,['record_date','close_price','dividends']],
                                    left_on='record_date',
                                    right_on='record_date',
                                    how='right')
            new_txn.loc[np.isnan(new_txn['close_price']), 'close_price'] = 0.000000
        else:
            print('No stock close price to join. Raise error')
            new_txn['close_price'] = 0.000000

        
        for i_date,rows in new_txn.iterrows():
            if (i_date == 0 and rows['trade_type'] == ''):
                new_txn.at[i_date, 'unit_price'] = 0.000000
                new_txn.at[i_date, 'qty'] = 0.000000
            elif (rows['trade_type'] == '' and i_date >0):
                new_txn.at[i_date, 'unit_price'] = i_stock_current_unit_price
                new_txn.at[i_date, 'qty'] = i_stock_current_qty
            elif (rows['trade_type'] == 'BUY'):
                new_txn.at[i_date, 'unit_price'] = ((rows['qty'] * rows['unit_price']) + (i_stock_current_qty * i_stock_current_unit_price))/(rows['qty'] + i_stock_current_qty)
                new_txn.at[i_date, 'qty'] = i_stock_current_qty + rows['qty']
                i_stock_current_unit_price = ((rows['qty'] * rows['unit_price']) + (i_stock_current_qty * i_stock_current_unit_price))/(rows['qty'] + i_stock_current_qty)
                i_stock_current_qty += rows['qty']
            elif (rows['trade_type'] == 'SELL'):
                new_txn.at[i_date, 'unit_price'] = ((i_stock_current_qty * i_stock_current_unit_price) - (rows['qty'] * rows['unit_price']))/(i_stock_current_qty - rows['qty'])
                new_txn.at[i_date, 'qty'] = i_stock_current_qty - rows['qty']
                i_stock_current_unit_price = ((i_stock_current_qty * i_stock_current_unit_price) - (rows['qty'] * rows['unit_price']))/(i_stock_current_qty - rows['qty'])
                i_stock_current_qty -= rows['qty']

        new_txn = new_txn.drop(['txn_date', 'trade_type', 'source'], axis=1)
        new_txn.drop(new_txn[(new_txn['qty'] == 0.0) & (new_txn['unit_price'] == 0.0)].index,
                     inplace=True)
        daily_record = daily_record.append(new_txn,
                                           ignore_index=True)
    daily_record.reset_index(drop=True, inplace=True)
    export_daily_record(daily_record)
    # pd.set_option('display.max_rows', None)
    # print(daily_record)

def get_stock_list(stocks):
    """Create list of tickers based on user input selected

    Unit Test created.
    """
    category = import_stock_categories()
    stock_list = []
    for i in stocks:
        if (i == 'all' or i == 'All' or i == 'ALL'):
            stock_list.extend(category['ticker'].tolist())
        elif i in category['sector'].tolist():
            stock_list.extend(category.loc[category['sector'] == i,'ticker'])
        elif i in category['ticker'].tolist():
            stock_list.append(i)
    return stock_list

def agg_data_by_x(stocks, by_variable, days):
    df = import_daily_record(os.path.dirname(__file__) + '/data/daily_record.csv')
    df_sector = import_stock_categories()
    df = df.merge(df_sector,how='left',left_on='ticker',right_on='ticker')
    df = df.loc[df['ticker'].isin(stocks),]
    df['ttl_investment'] = df['qty'] * df['unit_price']
    df['ttl_value'] = df['qty'] * df['close_price']
    if days is not None:
        df = df.loc[df['record_date'] >= (max(df['record_date']) - datetime.timedelta(days = days+1)),]
    
    if by_variable == 'record_date':
        df_agg = df.groupby(['record_date']).agg({'ttl_investment':'sum','ttl_value':'sum'}).reset_index()
    elif by_variable == 'ticker':
        df_agg = df.loc[df['record_date'] == max(df['record_date']),]
    elif by_variable == 'sector_record_date':
        df_agg = pd.DataFrame(columns=['sector','record_date','ttl_investment','ttl_value'])
        unique_sectors = df_sector['sector'].unique().tolist()
        for record_date in df['record_date'].unique():
            df_temp = df[df['record_date'] == record_date]
            df_temp = df_temp.groupby(['sector','record_date']).agg({'ttl_investment':'sum','ttl_value':'sum'}).reset_index()
            df_agg = df_agg.append(df_temp, ignore_index=True)
            for sector in unique_sectors:
                if (df_temp['sector'] == sector).any():
                    pass
                else:
                    df_agg = df_agg.append({'sector' : sector ,
                                            'record_date' : record_date,
                                            'ttl_investment': 0,
                                            'ttl_value': 0} , ignore_index=True)
        df_agg.reset_index(inplace=True)
    return df_agg

def get_summary(stocks):
    """
    Return a summary of the portfolio

    Args:
        stocks: List of stocks to consider for the summary
        days: Date range for summary
    
    Returns:
        overall_return: Return % for the selected stocks
        num_stocks: Number of companies (ticker count)

    Unit Test created.
    """
    df = agg_data_by_x(stocks, 'ticker', None)
    overall_return = 100*(sum(df['ttl_value']) - sum(df['ttl_investment']))/sum(df['ttl_investment'])
    num_stocks = len(df['ticker'].unique())
    return overall_return, num_stocks

def get_sector_stock_list():
    """Return unique list of stocks and sectors

    Unit test created.
    """
    daily_records = import_daily_record(os.path.dirname(__file__) + '/data/daily_record.csv')
    stock_category = import_stock_categories()
    stock_list = daily_records.ticker.unique()
    sector_list = stock_category.sector.unique()
    return stock_list.tolist(), sector_list.tolist()

def get_days_from_user_input(input):
    if input == '5y': return 1825
    elif input == '3y': return 1095
    elif input == '1y': return 365
    elif input == '1q': return 90
    elif input == '1m': return 30
    elif input == '1w': return 7
    elif input == '1d': return 1

def research_data(ticker, days):
    end_date = date.today()
    start_date = end_date - datetime.timedelta(days= int((days + 200)*1.5))
    df = yf.download(ticker, start= start_date, end=end_date, actions=True)
    df['record_date'] = df.index
    df['record_date'] = pd.to_datetime(df['record_date']).dt.date
    df.sort_values(by=['record_date'], inplace=True, ignore_index=True)
    df.rename(columns={'Close':'close_price'}, inplace=True)
    df['close_price_sma50'] = df.iloc[:,df.columns.get_loc("close_price")].rolling(window=50).mean()
    df['close_price_sma200'] = df.iloc[:,df.columns.get_loc("close_price")].rolling(window=200).mean()
    if days is not None:
        df = df.loc[df['record_date'] >= (max(df['record_date']) - datetime.timedelta(days = days+1)),]
    return df
