import streamlit as st
import yfinance as yf
import pandas as pd
from main import MyClass
import numpy as np
import plotly.express as px

st.set_page_config(layout="centered", page_title="Your Retirement Plan")
st.header("ETF Retirement Planner")

# # Beispiel-Dictionary für Symbole und Namen (kann weggelassen oder angepasst werden)
# my_dict = {"AAPL": "Apple", "MSFT": "Microsoft"}

@st.cache_data
def load_csv_to_df(file_name):
    df = pd.read_csv(file_name, sep=";")
    return df

@st.cache_resource
def get_yf_data(ticker):
    my_instance = MyClass(ticker)
    return my_instance

# Lade das Symbol-Dictionary aus der CSV-Datei
symbol_df = load_csv_to_df("ticker_list.csv").set_index("Name")
symbol_dict = symbol_df.to_dict()

# Initialisiere den Session State
if "selected_name" not in st.session_state:
    st.session_state.selected_name = list(symbol_dict["Ticker"].keys())[0]
if "text_ticker" not in st.session_state:
    st.session_state.text_ticker = symbol_dict["Ticker"][st.session_state.selected_name]
if "custom_symbols" not in st.session_state:
    st.session_state.custom_symbols = {}

# Funktion zum Abrufen von Symbolen von Yahoo Finance
def fetch_symbols_from_yahoo(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        # Hier wird angenommen, dass der Name des Unternehmens auf 'shortName' basiert
        # Du kannst dies anpassen, wenn du andere Attribute verwenden möchtest
        return info.get('shortName', 'Unknown')
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return "Unknown"

# Funktion zum Aktualisieren der Selectbox basierend auf der Eingabe im Text-Input
def update_selectbox():
    input_ticker = st.session_state.text_ticker
    # Suche nach dem Wert in my_dict basierend auf dem eingegebenen Ticker

    # Hole den Namen des Unternehmens von Yahoo Finance
    company_name = fetch_symbols_from_yahoo(input_ticker)
    st.session_state.selected_name = company_name
    st.session_state.custom_symbols[input_ticker] = company_name

# Funktion zum Aktualisieren des Text-Inputs basierend auf der Auswahl in der Selectbox
def update_text_input():
    selected_name = st.session_state.selected_name
    if selected_name in symbol_dict["Ticker"]:
        st.session_state.text_ticker = symbol_dict["Ticker"][selected_name]

    else:
        st.session_state.text_ticker = [k for k, v in st.session_state.custom_symbols.items() if v == selected_name][0]


# Kombiniere die ursprünglichen Namen, benutzerdefinierte Symbole und Yahoo Finance Namen
all_names = list(symbol_dict["Ticker"].keys()) + list(st.session_state.custom_symbols.values())


col1, col2 = st.columns(2)
with col1:
# Selectbox zur Auswahl des Namens
    ticker_name = st.selectbox("Symbol Search",
                 options=all_names,
                 key="selected_name",
                 on_change=update_text_input)
with col2:
    # Text-Input für die manuelle Eingabe des Tickers
    ticker_symbol =st.text_input("Select your Ticker",
                  key="text_ticker",
                  on_change=update_selectbox)

my_instance = get_yf_data(ticker_symbol)
info = my_instance.get_stock_info()

if ticker_name == "Unknown":
    st.error("Symbol not found. Please select a valid Yahoo finance ticker symbol.")
    st.stop()

currency = info["currency"]


col3, col4, col5, col6 = st.columns(4)
with col3:
    cagr1 = my_instance.get_cagr(100)
    st.metric("CAGR", f"{cagr1:.2%}")
with col4:
    cagr2 = my_instance.get_cagr(5)
    st.metric("5 year CAGR", f"{cagr2:.2%}")
with col5:
    cagr3 = my_instance.get_cagr(10)
    st.metric("10 year CAGR", f"{cagr3:.2%}")
with col6:
    cagr4 = my_instance.get_cagr(20)
    st.metric("20 year CAGR", f"{cagr4:.2%}")


st.divider()
st.subheader("Personal Information")
age_col, age_col2, start_col,  = st.columns(3)
with age_col:
    age1 = st.number_input("Your Age", value=30, min_value=0)
with age_col2:
    age2 = st.number_input("Retirement Age", value=63, min_value=age1+1)
with start_col:
    initial_invest = st.number_input("Initial Investment", min_value=0, step=1000, value=0)

save_col, target_col, e_cagr_col = st.columns(3)
with save_col:
    save_rate = st.number_input("Your Save Rate", min_value=10, step=10, value=100)
with target_col:
    save_target = st.number_input("Saving Target", min_value=10, step=100_000, value=1_000_000)
with e_cagr_col:
    expected_return = np.array([cagr1, cagr2, cagr3, cagr4]).min() * 0.9
    st.metric("Expected Growth Rate", f"{expected_return:.2%}",
              help="Its the minimum of the CARG rates with 10% margin of safety.\n"
                   "This growth rate is assumed for the future. ")

invest_timeframe = age2 - age1

col7, col8, col9 = st.columns(3)

with col7:
    is_custom_cagr = st.checkbox("Custom Growth Rate",
                                 help="Select a custom future growth rate. This rate is taken into account for calculations.")
with col8:

    if is_custom_cagr:
        custom_cagr = st.number_input("Custom CAGR", value=expected_return, min_value=0.0, max_value=1.0, step=0.01)
        expected_return = custom_cagr
    else:
        st.empty()


with col9:
    st.empty()


st.divider()
st.subheader("Result Section")

df = my_instance.get_future_returns(exp_cagr=expected_return,
                                    save_rate=save_rate,
                                    invest_years=invest_timeframe,
                                    initial_investment=initial_invest)


col7, col8, col9 = st.columns(3)
with col7:
    acc_value = df["value"].iloc[-1].round(2)
    st.metric("Expected Account value", f"{acc_value: ,.0f}")
with col8:
    invest = df["invest"].sum() + initial_invest
    st.metric("Value Invested", f"{invest: ,.0f}")
with col9:
    cap_gains = df["PnL"].sum() + (df["initial_invest_value"].iloc[-1] - initial_invest)
    st.metric("Capital Gains", f"{cap_gains: ,.0f}")


df2 = df.rename(columns={"invest_cum": "Amount invested", "value": "Account Balance"})
df2["year"] = df2["Date"].dt.year.astype(str)
df2["Amount invested"] = df2["Amount invested"].iloc[0] + initial_invest
df2 = df2.groupby("year").agg({"Account Balance": "last", "Amount invested": "last"}).reset_index()


chart_colors = ["#50C878", "#B80F0A"]

st.line_chart(df2,
                y=["Amount invested", "Account Balance"],
                x="year",
                x_label="Date",
                color=chart_colors)

min_save_rate = my_instance.get_saving_rate_for_target(expected_return, invest_timeframe, save_target, initial_invest)
st.write(f"To reach your savings target of {save_target:,.0f} you need to save a :red[ minimum of {min_save_rate} {currency} per month] for {invest_timeframe} years :money_with_wings:")


fig_data = {
    'Category': ['Personal Investment', 'Cap Gains'],
    'Value': [invest, cap_gains]
}

fig = px.pie(fig_data,
             values='Value',
             names='Category',
             title='Final Account Balance Breakdown',
             color_discrete_sequence=chart_colors)

st.plotly_chart(fig)


