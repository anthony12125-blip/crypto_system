"""
Dashboard Updater Module for Crypto Bots

Usage:
    from dashboard_updater import update_bot_status
    
    update_bot_status(
        bot_id='aggressive',
        position='FLAT',  # or 'LONG' or 'SHORT'
        cash=100.0,
        holdings=0.0,
        portfolio_value=110.0,
        total_return=10.0,
        trades=0,
        price=69305.94,
        confidence=0.54,  # optional
        signal='WAIT'     # optional
    )
"""

import requests
import os
from typing import Optional

# Dashboard API config
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'https://crypto-bot-409495160162.us-central1.run.app')  # Live URL
API_KEY = os.getenv('DASHBOARD_API_KEY', 'crypto-bot-2026')

def update_bot_status(
    bot_id: str,
    position: str,
    cash: float,
    holdings: float,
    portfolio_value: float,
    total_return: float,
    trades: int,
    price: float,
    confidence: Optional[float] = None,
    signal: Optional[str] = None,
    extra_data: Optional[dict] = None
) -> bool:
    """
    Update bot status on the dashboard.
    
    Args:
        bot_id: 'turtle', 'mean_revert', 'breakout', 'aggressive', 'balanced', or 'moderate'
        position: 'FLAT', 'LONG', or 'SHORT'
        cash: Cash balance
        holdings: Crypto holdings
        portfolio_value: Total portfolio value
        total_return: Percentage return
        trades: Number of completed trades
        price: Current BTC price
        confidence: Signal confidence (optional)
        signal: Signal type (optional)
        extra_data: Any additional fields (optional)
    
    Returns:
        True if successful, False otherwise
    """
    payload = {
        'bot_id': bot_id,
        'position': position,
        'cash': cash,
        'holdings': holdings,
        'portfolio_value': portfolio_value,
        'total_return': total_return,
        'trades': trades,
        'price': price
    }
    
    if confidence is not None:
        payload['confidence'] = confidence
    if signal is not None:
        payload['signal'] = signal
    if extra_data:
        payload.update(extra_data)
    
    try:
        response = requests.post(
            f'{DASHBOARD_URL}/api/update',
            json=payload,
            headers={'X-API-Key': API_KEY},
            timeout=5
        )
        if response.status_code == 200:
            return True
        else:
            print(f"Dashboard update failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Dashboard update error: {e}")
        return False

# Convenience functions for each bot
def update_turtle(position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs):
    return update_bot_status('turtle', position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs)

def update_mean_revert(position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs):
    return update_bot_status('mean_revert', position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs)

def update_breakout(position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs):
    return update_bot_status('breakout', position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs)

def update_aggressive(position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs):
    return update_bot_status('aggressive', position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs)

def update_balanced(position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs):
    return update_bot_status('balanced', position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs)

def update_moderate(position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs):
    return update_bot_status('moderate', position, cash, holdings, portfolio_value, total_return, trades, price, **kwargs)


if __name__ == '__main__':
    # Test update
    print("Testing dashboard update...")
    result = update_aggressive(
        position='FLAT',
        cash=100.0,
        holdings=0.0,
        portfolio_value=110.0,
        total_return=10.0,
        trades=0,
        price=69305.94,
        confidence=0.54,
        signal='WAIT'
    )
    print(f"Update result: {result}")
