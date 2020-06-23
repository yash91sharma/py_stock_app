import stock_fc
import matplotlib.pyplot as plt
import mpld3
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from tkinter import filedialog
import os
import numpy as np

print(os.environ.get('secret_key'))
    


#for later
# df = pd.DataFrame({'sector':['tech','tech','med'], 'dt':['1-1','2-2','1-1'],'c':[1,2,3], 'd':[2,4,6]})
# print(df)
# df = df.pivot(index='dt', columns='sector', values=['c','d'])
# df = df.fillna(0)
# df.reset_index(inplace=True)
# df.columns = ['_'.join(col).strip() for col in df.columns.values]
# df = df.melt('dt_', var_name=['sector'], value_name='value')
# df['value_name'] = df['sector'].str.split('_').str[0]
# df['sector'] = df['sector'].str.split('_').str[1]
# # df = df.pivot(index=['dt_','sector'], columns='value_name', values=['value'])
# print(df)

