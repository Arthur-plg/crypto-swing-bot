import json
import pandas as pd
from src.fetch_data import fetch_historical_data, fetch_ohlcv_data
from src.strategy import apply_strategy
from src.multi_asset_backtest import run_multi_asset_backtest
from src.multi_asset_backtest import plot_equity_curve

def load_selected_cryptos(filepath="data/selected_cryptos.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def main():
    # Chargement des cryptos et poids
    selected_cryptos = load_selected_cryptos()

    timeframe = '4h'
    limit = 500
    initial_balance = 1000
    fee = 0.001

    historical_data_dict = {}

    for crypto in selected_cryptos:
        symbol = crypto['symbol']
        weight = crypto['weight']

        print(f"\n--- Téléchargement de {symbol} ---")

        #df = fetch_ohlcv_data(symbol, timeframe, limit)   
        df = fetch_historical_data(symbol, timeframe, limit)
        df = apply_strategy(df)

        historical_data_dict[symbol] = {
            "df": df,
            "weight": weight
        }

    print("📅 Dates les plus anciennes par crypto :")

    for symbol, content in historical_data_dict.items():
        df = content["df"]
        if not df.empty:
            min_date = pd.to_datetime(df["timestamp"]).min()
            print(f" - {symbol} : {min_date}")

    print("\n=== Lancement du backtest multi-actif ===")

    results = run_multi_asset_backtest(historical_data_dict, initial_balance, fee)

    print("\n=== Résultats du backtest multi-actif ===")
    print(f"📈 Capital final : {results['equity'].iloc[-1]:.2f} USD")

    # Comparaison Buy & Hold
    
    buy_hold_equity = None  # cumul de l'équity passive

    for symbol, content in historical_data_dict.items():
        df = content["df"].copy()
        weight = content["weight"]

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        # Représente le capital investi initialement dans cet actif
        capital_initial = initial_balance * weight
        price_initial = df["close"].iloc[0]

        # Simule la valeur de l'investissement dans le temps
        df["equity"] = capital_initial * df["close"] / price_initial

        if buy_hold_equity is None:
            buy_hold_equity = df[["equity"]].copy()
        else:
            buy_hold_equity = buy_hold_equity.join(df["equity"], how="outer", rsuffix=f"_{symbol}")

    # Somme des capitalisations pondérées dans le temps
    buy_hold_equity["equity_total"] = buy_hold_equity.sum(axis=1)
    buy_hold_equity.reset_index(inplace=True)
    df1 = buy_hold_equity[["timestamp", "equity_total"]].rename(columns={"equity_total": "equity"})
    plot_equity_curve(results,df1)

    
if __name__ == "__main__":
    main()

    
