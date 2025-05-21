import json
import time
from datetime import datetime, timedelta

import numpy as np
from sklearn.preprocessing import MinMaxScaler # type: ignore

from src.fetch_data import fetch_historical_data, fetch_ohlcv_data
from src.strategy import apply_strategy  
from src.backtest import run_backtest

CANDIDATE_CRYPTOS = [
    # Top 10 par capitalisation
    "BTC/USDT", "ETH/USDT", "USDT/USDT", "XRP/USDT", "BNB/USDT",
    "SOL/USDT", "USDC/USDT", "DOGE/USDT", "ADA/USDT", "TRX/USDT",

    # 11 à 20
    "AVAX/USDT", "DOT/USDT", "MATIC/USDT", "LINK/USDT", "LTC/USDT",
    "BCH/USDT", "UNI/USDT", "XLM/USDT", "ATOM/USDT", "ETC/USDT",

    # 21 à 30
    "HBAR/USDT", "ICP/USDT", "FIL/USDT", "APT/USDT", "NEAR/USDT",
    "INJ/USDT", "OP/USDT", "SUI/USDT", "ARB/USDT", "QNT/USDT",

    # 31 à 40
    "AAVE/USDT", "EGLD/USDT", "VET/USDT", "GRT/USDT", "RUNE/USDT",
    "ALGO/USDT", "MKR/USDT", "FTM/USDT", "ZEC/USDT", "SNX/USDT"
]
'''
CANDIDATE_CRYPTOS = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "DOGE/USDT",
    "ADA/USDT",
    "TRX/USDT",
    "AVAX/USDT",
    "DOT/USDT"
]
'''

limit = 500
TIMEFRAME = "4h"
TOP_N = 10
FEE = 0.001
INITIAL_BALANCE = 1000

# Stocker les résultats bruts pour normalisation plus tard
raw_results = []

def score_crypto(symbol):
    df = fetch_historical_data(symbol, TIMEFRAME, limit)

    if df.empty or len(df) < 100:
        print(f"{symbol}: Pas assez de données.")
        return None

    df = apply_strategy(df)  
    bt_result = run_backtest(df, INITIAL_BALANCE, FEE)

    return {
        "symbol": symbol,
        **bt_result
    }

def main():
    for symbol in CANDIDATE_CRYPTOS:
        print(f"⏳ Évaluation de {symbol}")
        result = score_crypto(symbol)
        if result:
            raw_results.append(result)
        time.sleep(1)

    if not raw_results:
        print("❌ Aucun résultat exploitable.")
        return

    # Normalisation des métriques
    sharpe = np.array([r["sharpe_ratio"] for r in raw_results]).reshape(-1, 1)
    winrate = np.array([r["win_rate_pct"] for r in raw_results]).reshape(-1, 1)
    pf = np.array([r["profit_factor"] for r in raw_results]).reshape(-1, 1)
    dd = np.array([abs(r["max_drawdown_pct"]) for r in raw_results]).reshape(-1, 1)

    scaler = MinMaxScaler()
    sharpe_n = scaler.fit_transform(sharpe).flatten()
    winrate_n = scaler.fit_transform(winrate).flatten()
    pf_n = scaler.fit_transform(pf).flatten()
    dd_n = scaler.fit_transform(dd).flatten()

    # Score total global (mauvais pour les poids)
    for i, r in enumerate(raw_results):
        r["score"] = round(
            0.4 * sharpe_n[i] +
            0.2 * winrate_n[i] +
            0.2 * pf_n[i] -
            0.2 * dd_n[i], 4
        )

    # Trier et garder top N
    sorted_cryptos = sorted(raw_results, key=lambda x: x["score"], reverse=True)
    top_cryptos = sorted_cryptos[:TOP_N]

    # Calculer le score total uniquement sur les top cryptos
    top_r_tot = sum(c["score"] for c in top_cryptos)

    # Générer la liste avec poids relatifs
    selected_cryptos = []
    for crypto in top_cryptos:
        weight = round(crypto["score"] / top_r_tot, 4) if top_r_tot > 0 else 0.0
        selected_cryptos.append({
            "symbol": crypto["symbol"],
            "weight": weight
        })

    # Sauvegarde dans le fichier JSON
    with open("data/selected_cryptos.json", "w") as f:
        json.dump(selected_cryptos, f, indent=4)



    print("\n✅ Top cryptos sélectionnées :")
    for crypto in selected_cryptos:
        print("-", crypto)

if __name__ == "__main__":
    main()
