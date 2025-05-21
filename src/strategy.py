import talib  # type: ignore
import pandas as pd
from src.risk_management import *

def calculate_indicators(df):
    """
    Ajoute les indicateurs techniques à un DataFrame
    """
    # Calcul des moyennes mobiles
    df['EMA_short'] = talib.EMA(df['close'], timeperiod=9)
    df['EMA_long'] = talib.EMA(df['close'], timeperiod=50)

    # RSI
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)

    # Bandes de Bollinger
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(df['close'], timeperiod=20)

    # ATR
    df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)

    return df


def compute_btc_trend(btc_df: pd.DataFrame) -> pd.Series:
    """
    Retourne une série booléenne alignée sur btc_df.index :
    True si BTC < EMA200 (marché latéral / baissier) → mean-reversion autorisée.
    """
    EMA200 = btc_df['close'].rolling(window=200).mean()
    return btc_df['close'] < EMA200


def apply_strategy(df):
    """
    Applique la stratégie de swing trading et génère une colonne 'signal'
    """
    df = calculate_indicators(df)
    df['signal'] = None

    # Initialisation de l'état de position
    position = {
        'is_long': False,
        'entry_price': None,
        'high_since_entry': None,
    }

    # Parcours chronologique du DataFrame
    for i, row in df.iterrows():
        if position['is_long']:
            # Met à jour le high depuis l’entrée
            position['high_since_entry'] = max(position['high_since_entry'], row['high'])

        # Score achat
        score_buy = int(row['RSI'] < 30) + int(row['EMA_short'] > row['EMA_long']) + int(row['close'] < row['lower_band'])

        # Score vente
        score_sell = int(row['RSI'] > 70) + int(row['EMA_short'] < row['EMA_long']) + int(row['close'] > row['upper_band'])

        # Signal d'achat (si pas déjà en position)
        if not position['is_long'] and score_buy >= 2:
            df.at[i, 'signal'] = 'buy'
            position['is_long'] = True
            position['entry_price'] = row['close']
            position['high_since_entry'] = row['high']
            continue

        # Signal de vente (si en position)
        if position['is_long']:
            atr_value = row['ATR']
            sl_triggered = apply_atr_stop_loss(position['entry_price'], row['close'], atr_value, k_sl=5)
            ts_triggered = apply_atr_trailing_stop(position['high_since_entry'], row['close'], atr_value, k_ts=3)


            if score_sell >= 2 or sl_triggered or ts_triggered:
                df.at[i, 'signal'] = 'sell'
                position['is_long'] = False
                position['entry_price'] = None
                position['high_since_entry'] = None

    return df

def get_signals(df):
    """
    Version optionnelle : retourne une liste de signaux à partir du df (déjà enrichi)
    """
    signals = []

    for i, row in df.iterrows():
        if row['signal'] == 'buy':
            signals.append({
                'index': i,
                'signal': 'buy',
                'price': row['close'],
                'timestamp': row['timestamp']
            })
        elif row['signal'] == 'sell':
            signals.append({
                'index': i,
                'signal': 'sell',
                'price': row['close'],
                'timestamp': row['timestamp']
            })

    return signals
