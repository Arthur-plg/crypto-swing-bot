import pandas as pd
import numpy as np

def run_backtest(df, initial_balance, fee, risk_per_trade=0.1, risk_free_rate=0.0):
    balance = initial_balance
    position = None
    entry_price = 0
    quantity = 0
    trade_log = []
    equity_curve = []

    for i in range(len(df)):
        row = df.iloc[i]
        signal = row.get('signal', None)
        price = row['close']

        if signal == 'buy' and position is None:
            amount_to_invest = balance * risk_per_trade
            quantity = amount_to_invest / price
            position = 'long'
            entry_price = price
            balance -= quantity * price * (1 + fee)

            trade_log.append({
                'type': 'buy',
                'price': price,
                'quantity': quantity,
                'timestamp': row['timestamp'],
                'balance': round(balance, 2)
            })

        elif signal == 'sell' and position == 'long':
            proceeds = quantity * price * (1 - fee)
            balance += proceeds

            trade_log.append({
                'type': 'sell',
                'price': price,
                'quantity': quantity,
                'timestamp': row['timestamp'],
                'balance': round(balance, 2),
                'pnl_pct': (price - entry_price) / entry_price * 100  # Pour le win rate
            })

            position = None
            quantity = 0
            entry_price = 0

        equity_curve.append(balance)

    # --------- ANALYSE DES PERFORMANCES -----------
    trade_df = pd.DataFrame(trade_log)
    sell_trades = trade_df[trade_df['type'] == 'sell']

    # 1. Profit factor
    profits = sell_trades[sell_trades['pnl_pct'] > 0]['pnl_pct']
    losses = -sell_trades[sell_trades['pnl_pct'] < 0]['pnl_pct']  # signe positif
    profit_factor = profits.sum() / losses.sum() if not losses.empty else np.inf

    # 2. Win rate
    win_rate = len(profits) / len(sell_trades) * 100 if not sell_trades.empty else 0

    # 3. Sharpe ratio
    returns = pd.Series(equity_curve).pct_change().dropna()
    sharpe_ratio = (returns.mean() - risk_free_rate) / returns.std() * np.sqrt(252 * 24 * 2) if not returns.empty else 0
    # 252 j/an * 24h * 2 (1 trade toutes les 30min)

    # 4. Max Drawdown
    curve = pd.Series(equity_curve)
    rolling_max = curve.cummax()
    drawdowns = (curve - rolling_max) / rolling_max
    max_drawdown = drawdowns.min() * 100

    return {
        'final_balance': round(balance, 2),
        'return_pct': round(((balance - initial_balance) / initial_balance) * 100, 2),
        'nb_trades': len(trade_log) // 2,
        'trade_log': trade_log,
        'sharpe_ratio': round(sharpe_ratio, 2),
        'max_drawdown_pct': round(max_drawdown, 2),
        'profit_factor': round(profit_factor, 2),
        'win_rate_pct': round(win_rate, 2)
    }
