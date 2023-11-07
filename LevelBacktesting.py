import pandas as pd
import yfinance as yf
import backtesting
# import pandas_ta as ta
from datetime import datetime

from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover

import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'
# print(pio.renderers)

ticker = "META"
backlash = 0.30
stock = yf.download(ticker, start="2023-10-22", interval="1H", prepost=False)[
    ["Open", "High", "Low", "Close", "Volume"]  
]

# stock = stock.reset_index()

pd.set_option('display.max_rows', stock.shape[0]+1)


def support(df1, l, n1, n2): #n1 n2 before and after candle l
    for i in range(l-n1+1, l+1):
        if(df1.Low[i]>df1.Low[i-1]):
            return 0
    for i in range(l+1,l+n2+1):
        if(df1.Low[i]<df1.Low[i-1]):
            return 0
    return 1
#support(df,46,3,2)

def resistance(df1, l, n1, n2): #n1 n2 before and after candle l
    for i in range(l-n1+1, l+1):
        if(df1.High[i]<df1.High[i-1]):
            return 0
    for i in range(l+1,l+n2+1):
        if(df1.High[i]>df1.High[i-1]):
            return 0
    return 1
#resistance(df, 30, 3, 5)

sr = []
n1=3
n2=2
# Finding levels in the range:
for row in range(n1, len(stock)-n2): #len(df)-n2
    if support(stock, row, n1, n2):
        sr.append((stock.index[row], stock.Low[row], 1))
    if resistance(stock, row, n1, n2):
        sr.append((stock.index[row], stock.High[row], 2))
print(sr)

# List of support lvls
plotlist1 = [(x[1], x[0]) for x in sr if x[2]==1]
# List of resistance lvls
plotlist2 = [(x[1], x[0]) for x in sr if x[2]==2]
plotlist1.sort()
plotlist2.sort()

# Getting rid of lvls that are too close to each other
for i in range(1,len(plotlist1)):
    if(i>=len(plotlist1)):
        break
    if abs(plotlist1[i][0]-plotlist1[i-1][0])<=backlash:
        plotlist1.pop(i)

for i in range(1,len(plotlist2)):
    if(i>=len(plotlist2)):
        break
    if abs(plotlist2[i][0]-plotlist2[i-1][0])<=backlash:
        plotlist2.pop(i)


dfpl = stock[0:len(stock)]
# print(dfpl)
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

fig.update_layout(
    title=dict(text=ticker, font=dict(size=30))
)

fig.update_xaxes(
    rangebreaks=[
        dict(bounds=[16, 9], pattern="hour"), #hide hours outside of 9am-5pm
        dict(bounds=['sat', 'mon']) #hide weekends
    ])

fig.update_layout(hovermode="x unified", template="plotly_white")

# Plotting support lvls on a chart
c=0
while (1):
    if(c>len(plotlist1)-1 ):#or sr[c][0]>e
        break
    fig.add_shape(type='line', x0=plotlist1[c][1], y0=plotlist1[c][0],
                  x1=dfpl.index[-1],
                  y1=plotlist1[c][0],
                  line=dict(color="MediumPurple",width=3)
                  )
    c+=1
# Plotting resistance lvls on a chart
c=0
while (1):
    if(c>len(plotlist2)-1 ):#or sr[c][0]>e
        break
    fig.add_shape(type='line', x0=plotlist2[c][1], y0=plotlist2[c][0],
                  x1=dfpl.index[-1],
                  y1=plotlist2[c][0], 
                  line=dict(color="RoyalBlue",width=1)
                  )
    c+=1    
    
# Add dropdown
# fig.update_layout(
#     updatemenus=[
#         dict(
#             buttons=list([
#                 dict(
#                     args=["type", "candlestick"],
#                     label="candlestick",
#                     method="restyle"
#                 ),
#                 dict(
#                     args=["type", "scatter"],
#                     label="scatter",
#                     method="restyle"
#                 )
#             ]),
#             direction="down",
#             pad={"r": 10, "t": 10},
#             showactive=True,
#             x=0.1,
#             xanchor="left",
#             y=1.1,
#             yanchor="top"
#         ),
#     ]
# )
fig.write_html('test.html', auto_open=True)
fig.show()

def isBreakOut(candle):
    if (candle > plotlist1[0][0]):
        return 1
    
    elif (candle < plotlist2[0][0]):
        return 2
    
    else:
        return 0
    
# stock["isBreakOut"] = [isBreakOut(candle) for candle in stock.Close]
    
def SIGNAL():
    return stock.isBreakOut

class BreakOut(Strategy):
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)

    def next(self):
        super().next()
        TPSLRatio = 1.5

        if self.signal1==1 and len(self.trades)==0:   
            # sl1 = pmLow
            # tp1 = pmHigh + (pmHigh-pmLow) + 2
            sl1 = self.data.Low[-1]
            tp1 = self.data.Close[-1] + abs(self.data.Close[-1]-sl1)*TPSLRatio
            self.buy(sl=sl1, tp=tp1)
            # self.buy()

        elif self.signal1==2 and len(self.trades)==0:    
            sl1 = self.data.High[-1]
            tp1 = self.data.Close[-1] - abs(sl1-self.data.Close[-1])*TPSLRatio     
            # sl1 = pmHigh
            # tp1 = pmLow - (pmHigh-pmLow) - 15
            self.sell(sl=sl1, tp=tp1)
            # self.sell()

# bt = Backtest(stock, BreakOut, commission=.000,
#               exclusive_orders=True)
# stats = bt.run()
# bt.plot()

# stats = bt.optimize(
#         upper_bound = range(50,85,5),
#         lower_bound = range(15,45,5),
#         rsi_window = range(10,30,2),
#         maximize='Equity Final [$]')

# strategy = stats["_strategy"]
# print(strategy.lower_bound)