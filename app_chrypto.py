import os
import streamlit as st
import pandas as pd
import pandas_datareader as dr
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
from bs4 import BeautifulSoup
import requests
import json
import time
from PIL import Image


#---------------------------------------------------------------------------------------------------
# Page layout (continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.beta_columns((2,1))

st.markdown(
    """
<style>
.sidebar .sidebar-content {
    background-image: linear-gradient(#add8e6,#add8e6);
    color: white;
}
</style>
""",
    unsafe_allow_html=True,
)

#---------------------------------------------------------------------------------------------------
# About
expander_bar = col1.beta_expander("About")
expander_bar.markdown("""
**Source:** 
* CoinMarketCap (http://coinmarketcap.com) 
* Yahoo (https://fr.finance.yahoo.com/screener?lang=fr-FR&region=FR) 
""")




#---------------------------------------------------------------------------------------------------
# tweet coinmarket
# @st.cache
# def load_hash():
#     cmc = requests.get('https://coinmarketcap.com')
#     soup = BeautifulSoup(cmc.content, 'html.parser')
#     elements = [] # On crée une liste vide qui contiendra tous les titres propres
#     for element in soup.findAll(name = 'h1' ,  attrs = {'class' : "sc-fzqBZW iVccbF"}):
#         elements.append(element.text)
#     for element in soup.findAll(name = 'div' ,  attrs = {'class' : "sc-AxhCb keRptt"}):
#         elements.append(element.text)
#     for element in soup.findAll(name = 'div' ,  attrs = {'class' : "sc-fznBMq ekttti"}):
#         elements.append(element.text)
#     return elements


# col2.title (''' Hashtag (coinmarketcap)
# ''')
# col3.markdown ('''

# ''')
# elements = load_hash()
# col2.warning(elements[2])
# col2.warning(elements[3])
# col3.warning(elements[4])
# col3.success(elements[1] )




#---------------------------------------------------------------------------------------------------
# api Yahoo :

@st.cache
def get_yahoo_courbe ():
    # scapping des ticket et des nom
    cmc = requests.get('https://finance.yahoo.com/cryptocurrencies/?count=100&offset=0')
    soup = BeautifulSoup(cmc.content, 'html.parser')
    symbole = [] 
    nom_crypto = []
    #page 1 yahoo
    for element in soup.findAll(name = 'a' ,  attrs = {'class' : "Fw(600) C($linkColor)"}):
        symbole.append(element.text)

    for element in soup.findAll(name = 'td' ,  attrs = {'class' : "Va(m) Ta(start) Px(10px) Fz(s)"}):
        nom_crypto.append(element.text)
    #page 2 yahoo
    cmc = requests.get('https://finance.yahoo.com/cryptocurrencies/?count=100&offset=100')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    for element in soup.findAll(name = 'a' ,  attrs = {'class' : "Fw(600) C($linkColor)"}):
        symbole.append(element.text)

    for element in soup.findAll(name = 'td' ,  attrs = {'class' : "Va(m) Ta(start) Px(10px) Fz(s)"}):
        nom_crypto.append(element.text)
    return symbole,nom_crypto


#Cytpto monnaies
ticket_crypto , company_crypto = get_yahoo_courbe ()

deb = '2012-01-01'
fin = str( '{}-{}-{}'.format(datetime.now().year, datetime.now().month,datetime.now().day) )
liste_temp = [ 7  , 14  , 30  ]

col1.title ('Param Yahoo')
place_boursiere_crypto = col1.selectbox(label = "Crypto choice", options = ticket_crypto, key=13)            
selection_temps = col1.selectbox(label = "Number of days", options = liste_temp, key=15)            

try:
    df_crypto = dr.data.get_data_yahoo (place_boursiere_crypto , start = deb, end = fin)
    titre_intro = place_boursiere_crypto
    # ticket_index = place_boursiere_crypto.index ()
except:
    st.error("Problème de récupération des données")
    st.stop()





#---------------------------------------------------------------------------------------------------
# Web scraping of CoinMarketCap data

## Sidebar - Currency price unit
# currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))
currency_price_unit ='USD'
@st.cache
def load_data():
    cmc = requests.get('https://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    for i in listings:
      coins[str(i['id'])] = i['slug']

    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []

    for i in listings:
      coin_name.append(i['slug'])
      coin_symbol.append(i['symbol'])
      price.append(i['quote'][currency_price_unit]['price'])
      percent_change_1h.append(i['quote'][currency_price_unit]['percentChange1h']) # percent_change_1h
      percent_change_24h.append(i['quote'][currency_price_unit]['percentChange24h']) #percent_change_24h
      percent_change_7d.append(i['quote'][currency_price_unit]['percentChange7d']) # percent_change_7d
      market_cap.append(i['quote'][currency_price_unit]['marketCap']) # market_cap
      volume_24h.append(i['quote'][currency_price_unit]['volume24h']) # volume_24h

    df = pd.DataFrame(columns=['coin_name', 'coin_symbol', 'marketCap', 'percentChange1h', 'percentChange24h', 'percentChange7d', 'price', 'volume24h'])
    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['percentChange1h'] = percent_change_1h
    df['percentChange24h'] = percent_change_24h
    df['percentChange7d'] = percent_change_7d
    df['marketCap'] = market_cap
    df['volume24h'] = volume_24h
    return df

df = load_data()

## Sidebar - Cryptocurrency selections
sorted_coin = sorted( df['coin_symbol'] )
# selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)
# df_selected_coin = df[ (df['coin_symbol'].isin(selected_coin)) ] # Filtering data
df_selected_coin = df

## Sidebar - Number of coins to display
# num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
df_coins = df_selected_coin[:]

## Sidebar - Percent change timeframe
col1.title ('Param Coinmarketcap')
percent_timeframe = col1.selectbox('Percent change time frame',
                                    ['1h' , '24h','7d' ])

## Sidebar - Percent change timeframe
percent_dict = {"7d":'percentChange7d',"24h":'percentChange24h',"1h":'percentChange1h'}
selected_percent_timeframe = percent_dict[percent_timeframe]

## Sidebar - Sorting values
# sort_values = col2.selectbox('Sort values?', ['Yes', 'No'])
sort_values = 'Yes'
# Download CSV data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href

st.title ('Today Cryptocurrency Prices by Market Cap')
# col2.dataframe(df_coins [['coin_name' , 'coin_symbol'  ]].set_index ('coin_symbol' ) )

df_1h = df_coins.sort_values ( by = 'percentChange1h' , ascending = False)
df_7d = df_coins.sort_values ( by = 'percentChange7d' , ascending = False)

st.markdown('**Evolution sur 1 heure**')
st.dataframe ( df_1h.set_index('coin_symbol')  .rename ( columns = {  'percentChange1h' : '%1h' } ) [['%1h' , 'price']] )

st.markdown('**Evolution sur 24h**')
st.dataframe(df_coins.set_index('coin_symbol') [[ 'percentChange24h' , 'price' ] ].rename ( columns = {  'percentChange24h' : '%24h' }) .sort_values ( by = '%24h' , ascending = False) )


st.markdown('**Evolution sur 7 jours**')
st.dataframe ( df_7d.set_index('coin_symbol')  .rename ( columns = {  'percentChange7d' : '%7d' } ) [['%7d' , 'price']] )


#---------------------------------------------------------------------------------------------------
# courbe Yahoo 
st.title('Courbes Cryptocurrency (Yahoo)')

plotly_figure_intro_crypto = px.line(data_frame = df_crypto, 
                        x = df_crypto.index, 
                        y = ['Close' ] , 
                        title = titre_intro + ' - Cours' )
st.plotly_chart ( plotly_figure_intro_crypto)

df_crypto_reduced = df_crypto.tail (selection_temps)
plotly_figure_intro_crypto_r = px.line(data_frame =df_crypto_reduced, 
                        x = df_crypto_reduced.index, 
                        y = ['Close' ] , 
                        title = titre_intro + ' - Last ' + str (selection_temps)+ ' days' )
st.plotly_chart ( plotly_figure_intro_crypto_r)










#---------------------------------------------------------------------------------------------------
#  Bar plot evolution du prix :
st.title('Evolution du prix (%) - Coinmarketcap')

# st.header('Table of % Price Change')
df_change = pd.concat([df_coins.coin_symbol, df_coins.percentChange1h, df_coins.percentChange24h, df_coins.percentChange7d], axis=1)
df_change = df_change.set_index('coin_symbol')
df_change['positive_percent_change_1h'] = df_change['percentChange1h'] > 0
df_change['positive_percent_change_24h'] = df_change['percentChange24h'] > 0
df_change['positive_percent_change_7d'] = df_change['percentChange7d'] > 0
# st.dataframe(df_change)

# # Conditional creation of Bar plot (time frame)

if percent_timeframe == '7d':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percentChange7d'])
    st.write('*7 days period*')
    plt.figure(figsize=(5,25))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percentChange7d'].plot(kind='barh', color=df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
    st.pyplot(plt)
elif percent_timeframe == '24h':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percentChange24h'])
    st.write('*24 hour period*')
    plt.figure(figsize=(5,25))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percentChange24h'].plot(kind='barh', color=df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
    st.pyplot(plt)
else:
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percentChange1h'])
    st.write('*1 hour period*')
    plt.figure(figsize=(5,25))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percentChange1h'].plot(kind='barh', color=df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))
    st.pyplot(plt)

col1.title ('Dictionnaire')
col1.dataframe(df_coins [['coin_name' , 'coin_symbol'  ]].set_index ('coin_symbol' ).sort_index() )
















