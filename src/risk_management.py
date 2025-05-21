# 1ère Méthode avec SL TS fixé en %

def apply_fixed_stop_loss(entry_price, current_price, stop_loss_pct):
    """
    Déclenche un stop loss fixe si le prix baisse trop.
    """
    stop_loss_price = entry_price * (1 - stop_loss_pct)
    return current_price <= stop_loss_price


def apply_trailing_stop(high_since_entry, current_price, trailing_pct):
    """
    Déclenche un trailing stop si le prix baisse trop après un sommet.
    """
    trailing_stop_price = high_since_entry * (1 - trailing_pct)
    return current_price <= trailing_stop_price



# 2ème Méthode avec SL et TS basé sur l'ATR

def apply_atr_stop_loss(entry_price, current_price, atr_value, k_sl):
    """
    Déclenche un stop-loss basé sur l'ATR si le prix baisse trop.
    
    :param entry_price: Prix d'entrée dans la position
    :param current_price: Prix actuel
    :param atr_value: Valeur actuelle de l'ATR
    :param k_sl: Multiplicateur de l'ATR pour le SL
    :return: True si le stop-loss est déclenché, sinon False
    """
    stop_loss_price = entry_price - (atr_value * k_sl)
    return current_price <= stop_loss_price


def apply_atr_trailing_stop(high_since_entry, current_price, atr_value, k_ts):
    """
    Déclenche un trailing stop basé sur l'ATR si le prix redescend trop après un sommet.
    
    :param high_since_entry: Plus haut atteint depuis l'entrée
    :param current_price: Prix actuel
    :param atr_value: Valeur actuelle de l'ATR
    :param k_ts: Multiplicateur de l'ATR pour le trailing stop
    :return: True si le trailing stop est déclenché, sinon False
    """
    trailing_stop_price = high_since_entry - (atr_value * k_ts)
    return current_price <= trailing_stop_price

