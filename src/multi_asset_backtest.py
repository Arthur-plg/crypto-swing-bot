import pandas as pd
import matplotlib.pyplot as plt # type: ignore

def plot_equity_curve(df,df1):
    plt.figure(figsize=(10, 5))
    plt.plot(pd.to_datetime(df["timestamp"]), df["equity"], label="Capital") 
    plt.plot(pd.to_datetime(df1["timestamp"]), df1["equity"], label="Buy & Hold", linestyle="--")   # Comparaison Buy & Hold
    plt.title("Évolution du capital (multi-actif)")
    plt.xlabel("Date")
    plt.ylabel("Capital (USD)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def run_multi_asset_backtest(historical_dict, initial_balance=1000.0, fee=0.001):
    # 1. Récupérer les données et poids
    data = {}
    weights = {}

    for symbol, content in historical_dict.items():
        data[symbol] = content["df"]
        weights[symbol] = content["weight"]

    # 2. Synchroniser les timestamps (union)
    common_index = sorted(set.union(*(set(df["timestamp"]) for df in data.values())))

    # 3. Initialisation du portefeuille
    balance = initial_balance
    positions = {symbol: None for symbol in data}
    entry_prices = {symbol: None for symbol in data}
    quantities = {symbol: 0 for symbol in data}
    equity_curve = []

    # 4. Backtest synchronisé sur timestamps communs (union)
    for ts in common_index:
        for symbol, df in data.items():
            row = df[df["timestamp"] == ts]
            if row.empty:
                # Pas de données à ce timestamp pour cette crypto => on skip
                continue

            signal = row.iloc[0]["signal"]
            price = row.iloc[0]["close"]
            weight = weights[symbol]

            if signal == "buy" and positions[symbol] is None:
                amount = balance * weight
                qty = amount / price
                cost = qty * price * (1 + fee)
                if cost <= balance:
                    balance -= cost
                    positions[symbol] = "long"
                    entry_prices[symbol] = price
                    quantities[symbol] = qty

            elif signal == "sell" and positions[symbol] == "long":
                proceeds = quantities[symbol] * price * (1 - fee)
                balance += proceeds
                positions[symbol] = None
                entry_prices[symbol] = None
                quantities[symbol] = 0

        # Calcul de la valeur totale du portefeuille (cash + positions)
        total_equity = balance
        for symbol in data:
            if positions[symbol] == "long":
                row = data[symbol][data[symbol]["timestamp"] == ts]
                if row.empty:
                    # Pas de prix dispo à ce timestamp, on ne compte pas cette position ici
                    continue
                price = row.iloc[0]["close"]
                total_equity += quantities[symbol] * price

        equity_curve.append({"timestamp": ts, "equity": total_equity})

    return pd.DataFrame(equity_curve)
