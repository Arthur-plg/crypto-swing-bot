import ccxt # type: ignore
import pandas as pd
import time

def fetch_ohlcv_data(symbol, timeframe, limit=100):
    """
    Récupère les données OHLCV depuis Binance pour une paire donnée.

    :param symbol: La paire de trading (ex: 'BTC/USDT')
    :param timeframe: Intervalle de temps (ex: '4h', '1d')
    :param limit: Nombre de bougies à récupérer
    :return: DataFrame pandas contenant les données OHLCV
    """
    binance = ccxt.binance()

    # Récupérer les données OHLCV
    ohlcv = binance.fetch_ohlcv(symbol, timeframe, limit=limit)

    # Convertir les données en DataFrame pandas
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # Convertir le timestamp en format datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df

def fetch_historical_data(symbol: str, timeframe: str, since: int, max_candles: int = 30000):
    """
    Récupère les données OHLCV historiques depuis une date donnée (timestamp en ms).
    """
    

    exchange = ccxt.binance()
    all_ohlcv = []
    limit = 1000  # Limite max par appel chez Binance
    now = exchange.milliseconds()
    current_since = since

    while len(all_ohlcv) < max_candles:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=current_since, limit=limit)
            if not ohlcv:
                break
            all_ohlcv.extend(ohlcv)
            current_since = ohlcv[-1][0] + 1  # Prochaine bougie après la dernière récupérée
            time.sleep(0.2)  # Pour éviter d’être bloqué par l’API
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            break

        if current_since > now:
            break

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

