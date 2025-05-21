import pandas as pd
import json
from src.fetch_data import fetch_ohlcv_data, fetch_historical_data
from src.strategy import apply_strategy, get_signals
import matplotlib.pyplot as plt  # type: ignore
from src.backtest import *

def load_selected_cryptos(filepath="data/selected_cryptos.json"):
        with open(filepath, "r") as f:
            return json.load(f)

def main():

    selected_cryptos = load_selected_cryptos()
    
    timeframe = '4h'
    limit = 500
    list_rendement=[]

    for crypto in selected_cryptos:

        symbol = crypto["symbol"]
        weight = crypto["weight"]
            
        print(f"\n=== Analyse de {symbol} ===")
        
        df = fetch_historical_data(symbol, timeframe, limit)


        # Appliquer la stratégie (ajout des indicateurs et calcul des signaux d'achat et de vente)
        df = apply_strategy(df)


        # === Backtest ===
        result = run_backtest(df, initial_balance=1000, fee=0.001)

        print("\n=== Résultats du Backtest ===")
        print(f"📈 Capital final : {result['final_balance']} USD")
        print(f"📊 Rendement total : {result['return_pct']}%")
        list_rendement.append(result['return_pct'])

        print(f"🔁 Profit Factor : {result.get('profit_factor', 'N/A')}")
        print(f"📉 Max Drawdown : {result.get('max_drawdown_pct', 'N/A')}%")
        print(f"✅ Win Rate : {result.get('win_rate_pct', 'N/A')}%")
        print(f"⚖️ Sharpe Ratio : {result.get('sharpe_ratio', 'N/A')}")
        print(f"📊 Nombre de trades : {result['nb_trades']}")

        print("\n📌 Derniers trades :")
        for trade in result['trade_log'][-5:]:
            print(trade)



        # === Affichage graphique (uniquement les trades exécutés) ===
        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['close'], label="Prix de clôture", color='blue')

        # --- Extraire les trades exécutés ---
        trade_df = pd.DataFrame(result['trade_log'])
        if not trade_df.empty:
            buys  = trade_df[trade_df['type'] == 'buy']
            sells = trade_df[trade_df['type'] == 'sell']

            if not buys.empty:
                plt.scatter(buys['timestamp'], buys['price'],
                            label='Trade BUY', marker='^', color='g')
            if not sells.empty:
                plt.scatter(sells['timestamp'], sells['price'],
                            label='Trade SELL', marker='v', color='r')

        # Légende & déco
        plt.title(f"Trades exécutés pour {symbol} – TF {timeframe}")
        plt.xlabel('Timestamp')
        plt.ylabel('Prix (USDT)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    print(list_rendement)
if __name__ == "__main__":
    main()