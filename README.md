# Crypto Swing Bot

Algorithme de swing trading basé sur une stratégie de **mean reversion** (retour à la moyenne) sur cryptomonnaies.
Comparaison de l'évolution du PnL entre ma stratégie et une stratégie Buy&Hold dans le dossier image.

---

## Timeframe

- Utilisation du timeframe **4 heures**  
- Choisi pour optimiser le retour à la moyenne tout en éliminant le bruit des fluctuations trop courtes.

---

## Portefeuille de cryptomonnaies

- Sélection des **10 meilleures cryptos** pondérées selon un score combinant plusieurs critères normalisés :  
  - Sharpe Ratio  
  - Win Rate  
  - Profit Factor  
  - Maximum Drawdown  

- Données OHLCV récupérées via l’API Binance.

- **Attention** : biais de sélection possible, les cryptos sont choisies selon leur performance passée sur la stratégie.

---

## Stratégie de trading

- **Type** : Mean Reversion en swing trading, pour capturer des profits sur la volatilité.  
- **Position** : Une position à la fois (possibilité d’évolution vers pyramidal inversé).  
- **Approche conservatrice** :  
  - Vente si marché suracheté, achat si survendu.  
  - **Critères combinés (2/3 nécessaires pour buy/sell)** :  
    - RSI > 70 → vente (surachat)  
    - RSI < 30 → achat (survente)  
    - EMA9 > EMA50 → achat (momentum haussier)  
    - EMA9 < EMA50 → vente (momentum baissier)  
    - Prix < bande inférieure de Bollinger → achat  
    - Prix > bande supérieure de Bollinger → vente  

- Résumé : stratégie combinant **momentum (RSI)**, **tendance (EMA)** et **volatilité (Bandes de Bollinger)**.

- Optionnel : filtre de tendance basé sur BTC, désactivant la stratégie de mean reversion si BTC est en tendance haussière (hypothèse que la tendance de la crypto suit celle du BTC).

---

## Gestion des risques

- Stop Loss (SL) et Trailing Stop (TS) basés sur l’**ATR** (avec paramètres k_ts=5, k_sl=3 testés en backtest).  
- Sur main.py : risque par trade fixé à **1 % du capital** (pour l’instant, portefeuille de chaque crypto géré séparément).  
- Sur main_multi.py : risque par trade fixé à **poids de la crypto dans le portefeuille**.
---

## Architecture du projet

- `multi_asset_backtest.py` : backtest multi-actifs synchronisé avec gestion partagée du capital.  
- `main.py` : backtest mono-actif classique.

---

## À venir / améliorations

- Mettre photo comparaison buy & hold 
- Tester un choix de crypto sur une periode differente du backtest de la strategie pour moins de biais

- Portefeuille mutualisé avec pondération adaptée à la performance des cryptos.  
- Intégration des canaux de Keltner.  
- Ajout du MACD comme indicateur.  
- Prise en compte du volume dans la stratégie.  
- Passage à l’exécution réelle avec intégration des ordres via API.

---

## Installation & utilisation

```bash
pip install -r requirements.txt
python main.py  # ou python main_multi.py
