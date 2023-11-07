from dash import Dash, dcc, html
import plotly.graph_objects as go
import numpy as np
import yfinance as yf

ticker = "META"
stock = yf.download(ticker, start="2023-10-22", interval="1H", prepost=False)[
    ["Open", "High", "Low", "Close", "Volume"]  
]

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

app = Dash()

app.layout = html.Div([
    # html.H4('Interactive plot with custom data source'),
    dcc.Graph(figure=fig),
    # html.P("Number of bars:"),
    # dcc.Slider(id="slider", min=2, max=10, value=4, step=1),
])

app.run_server(debug=True)