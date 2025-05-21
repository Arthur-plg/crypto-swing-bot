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
    plot_equity_curve(results)

    
if __name__ == "__main__":
    main()

    
