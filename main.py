import yfinance as yf
import pandas as pd

# ticker = "AAPL"
# save_rate = 100


class MyClass:

    def __init__(self, ticker):

        self.obj = yf.Ticker(ticker)
        self.data = self.obj.history(interval="1mo", period="max")
        self.info = self.obj.get_info()
        self.data = self.data[["Open"]]
        self.data.index = pd.to_datetime(self.data.index)

    def get_cagr(self, year):
        data = self.data[self.data.index >= self.data.index.max() - pd.DateOffset(years=year)]
        cagr = (data["Open"].iloc[-1] / data["Open"].iloc[0]) ** (1 / (len(data.Open) / 12)) - 1
        return cagr

    def get_historic_table(self, save_rate):
        data = self.data
        data["pct_change"] = data.Open.pct_change()
        data["invest"] = save_rate
        data["invest_cum"] = data["invest"].cumsum()
        data["shares"] = data["invest"] / data["Open"]
        data["PnL"] = (data["shares"] * data["Open"].iloc[-1]) - data["invest"]
        print("Calulated")
        return data

    def get_last_price(self):
        return self.data["Open"].iloc[-1]

    def get_profits(self):
        return self.data["PnL"].sum()

    def get_amount_invested(self):
        return self.data["invest"].sum()

    def get_mean_return(self):
        return self.data["pct_change"].mean()

    def get_median_return(self):
        return self.data["pct_change"].median()

    def get_historic_values(self):
        return self.data.round(4)

    def get_account_value(self):
        return self.data["value"].iloc[-1].round(2)

    def get_future_returns(self, exp_cagr, save_rate, invest_years, initial_investment=0):
        # Startdatum (heutiges Datum)
        start_date = pd.to_datetime("today")
        # Enddatum (fünf Jahre ab jetzt)
        end_date = start_date + pd.DateOffset(years=invest_years)
        # Erzeuge eine monatliche Zeitreihe von Start- bis Enddatum
        monthly_dates = pd.date_range(start=start_date, end=end_date, freq='ME')

        monthly_return = (1 + exp_cagr) ** (1 / 12) - 1

        df = pd.DataFrame({
            "Date": monthly_dates,
        })
        df['Date'] = pd.to_datetime(df['Date'], ).dt.to_period('M') #format='%Y-%m'
        df["invest"] = save_rate
        df["invest_cum"] = df["invest"].cumsum()
        df["expected_return"] = monthly_return
        df["initial_invest_value"] = [initial_investment * (1 + monthly_return) ** i for i in
                                      range(invest_years * 12)]
        df["expected_share_price"] = [self.get_last_price() * (1 + monthly_return) ** i for i in
                                      range(invest_years * 12)]
        df["shares"] = df["invest"] / df["expected_share_price"]
        df["shares_cumsum"] = df["shares"].cumsum()
        df["PnL"] = (df["shares"] * df["expected_share_price"].iloc[-1]) - df["invest"]
        df["value"] = (df["shares_cumsum"] * df["expected_share_price"]) + df["initial_invest_value"]

        return df

    def get_saving_rate_for_target(self, exp_cagr, invest_years, saving_target, initial_investment=0):
        save_rate = 50

        df = self.get_future_returns(exp_cagr, save_rate, invest_years, initial_investment)
        final_value = df["value"].iloc[-1]
        while final_value < saving_target:
            save_rate += 50
            df = self.get_future_returns(exp_cagr, save_rate, invest_years, initial_investment)
            final_value = df["value"].iloc[-1]
        return save_rate

    def get_saving_rate_for_target2(self, exp_cagr, invest_years, saving_target, initial_investment=0):
        lower_bound = 10
        upper_bound = 10000  # Setze eine vernünftige obere Grenze für die Sparrate
        tolerance = 100  # Toleranzbereich, um den Zielwert zu erreichen

        while lower_bound < upper_bound - tolerance:
            mid_rate = (lower_bound + upper_bound) / 2
            df = self.get_future_returns(exp_cagr, mid_rate, invest_years, initial_investment)
            final_value = df["value"].iloc[-1]

            if final_value < saving_target:
                lower_bound = mid_rate
            else:
                upper_bound = mid_rate

        return (lower_bound + upper_bound) / 2

    def get_stock_info(self):
        return self.info

#instance = MyClass("QQQ")

#
#
# info = instance.get_stock_info()
# print(info)


