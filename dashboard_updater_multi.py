#!/usr/bin/env python3
"""
Dashboard Updater - Multi-Coin Support with Ensemble & On-Chain Data
Updates dashboard with all bot statuses, predictions, and metrics
"""

import requests
import os
import glob
import json
from datetime import datetime

DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'https://crypto-bot-409495160162.us-central1.run.app')
API_KEY = os.getenv('DASHBOARD_API_KEY', 'crypto-bot-2026')

# Bot registry - all 9+ existing bots
BOT_REGISTRY = {
    # Multi-strategy bots (3 strategies x 2 coins = 6 bots)
    'aggressive_BTCUSDT': {'name': 'Aggressive BTC', 'strategy': 'aggressive', 'symbol': 'BTCUSDT', 'type': 'multi'},
    'aggressive_ETHUSDT': {'name': 'Aggressive ETH', 'strategy': 'aggressive', 'symbol': 'ETHUSDT', 'type': 'multi'},
    'balanced_BTCUSDT': {'name': 'Balanced BTC', 'strategy': 'balanced', 'symbol': 'BTCUSDT', 'type': 'multi'},
    'balanced_ETHUSDT': {'name': 'Balanced ETH', 'strategy': 'balanced', 'symbol': 'ETHUSDT', 'type': 'multi'},
    'moderate_BTCUSDT': {'name': 'Moderate BTC', 'strategy': 'moderate', 'symbol': 'BTCUSDT', 'type': 'multi'},
    'moderate_ETHUSDT': {'name': 'Moderate ETH', 'strategy': 'moderate', 'symbol': 'ETHUSDT', 'type': 'multi'},
    
    # High confidence bots (4 coins)
    'BTC_high_BTCUSDT': {'name': 'High Conf BTC', 'strategy': 'high_conf', 'symbol': 'BTCUSDT', 'type': 'highconf'},
    'ETH_high_ETHUSDT': {'name': 'High Conf ETH', 'strategy': 'high_conf', 'symbol': 'ETHUSDT', 'type': 'highconf'},
    'ADA_high_ADAUSDT': {'name': 'High Conf ADA', 'strategy': 'high_conf', 'symbol': 'ADAUSDT', 'type': 'highconf'},
    'SOL_high_SOLUSDT': {'name': 'High Conf SOL', 'strategy': 'high_conf', 'symbol': 'SOLUSDT', 'type': 'highconf'},
    
    # Advanced bots (3 strategies - placeholders for when ready)
    'adv_conservative_BTCUSDT': {'name': 'Adv Conservative BTC', 'strategy': 'conservative', 'symbol': 'BTCUSDT', 'type': 'advanced'},
    'adv_conservative_ETHUSDT': {'name': 'Adv Conservative ETH', 'strategy': 'conservative', 'symbol': 'ETHUSDT', 'type': 'advanced'},
    'adv_balanced_BTCUSDT': {'name': 'Adv Balanced BTC', 'strategy': 'balanced_adv', 'symbol': 'BTCUSDT', 'type': 'advanced'},
    'adv_balanced_ETHUSDT': {'name': 'Adv Balanced ETH', 'strategy': 'balanced_adv', 'symbol': 'ETHUSDT', 'type': 'advanced'},
    'adv_aggressive_BTCUSDT': {'name': 'Adv Aggressive BTC', 'strategy': 'aggressive_adv', 'symbol': 'BTCUSDT', 'type': 'advanced'},
    'adv_aggressive_ETHUSDT': {'name': 'Adv Aggressive ETH', 'strategy': 'aggressive_adv', 'symbol': 'ETHUSDT', 'type': 'advanced'},
}

def get_current_price(symbol):
    """Fetch current price from Coinbase"""
    try:
        coinbase_sym = symbol.replace('USDT', '-USD')
        url = f'https://api.exchange.coinbase.com/products/{coinbase_sym}/ticker'
        response = requests.get(url, timeout=5)
        return float(response.json()['price'])
    except:
        return None

def get_ensemble_prediction(symbol):
    """Get ensemble model prediction if available"""
    try:
        # Check for ensemble metadata
        meta_path = f'models/{symbol}_ensemble_metadata.json'
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            return {
                'lgbm_accuracy': meta.get('lgbm_accuracy', 0),
                'lstm_accuracy': meta.get('lstm_accuracy', 0),
                'ensemble': meta.get('ensemble', False)
            }
    except:
        pass
    return None

def get_onchain_metrics(symbol):
    """Get on-chain metrics if available"""
    asset = symbol.replace('USDT', '')
    metrics = {}
    
    # Check for on-chain data files
    onchain_dir = 'data_onchain'
    if os.path.exists(onchain_dir):
        for metric_type in ['exchange_inflows', 'exchange_outflows', 'active_addresses', 'sopr']:
            filepath = f'{onchain_dir}/{asset}_{metric_type}.csv'
            if os.path.exists(filepath):
                try:
                    import pandas as pd
                    df = pd.read_csv(filepath)
                    if not df.empty:
                        latest = df.iloc[-1]
                        metrics[metric_type] = float(latest.iloc[-1])  # Last column is value
                except:
                    pass
    
    return metrics if metrics else None

def get_fear_greed_index():
    """Get Fear & Greed Index if available"""
    try:
        if os.path.exists('data_advanced/fear_greed.csv'):
            import pandas as pd
            df = pd.read_csv('data_advanced/fear_greed.csv')
            if not df.empty:
                latest = df.iloc[-1]
                return {
                    'value': int(latest.get('fear_greed_value', 50)),
                    'classification': latest.get('fear_greed_classification', 'Neutral')
                }
    except:
        pass
    return None

def update_bot_status(bot_data):
    """Update bot status on dashboard"""
    try:
        response = requests.post(
            f'{DASHBOARD_URL}/api/update',
            json=bot_data,
            headers={'X-API-Key': API_KEY},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"  Update error: {e}")
        return False

def scan_and_update():
    """Scan all state files and update dashboard"""
    print(f"\n{'='*80}")
    print(f"DASHBOARD UPDATE | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Track combined P&L
    total_portfolio_value = 0
    total_invested = 0
    bot_count = 0
    active_bots = 0
    
    # Get market-wide indicators
    fear_greed = get_fear_greed_index()
    if fear_greed:
        print(f"\nMarket Sentiment: {fear_greed['value']} ({fear_greed['classification']})")
    
    # Scan state files
    state_files = glob.glob('state_*.json')
    print(f"\nScanning {len(state_files)} state files...")
    
    for filename in state_files:
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
            
            name = state.get('name', 'unknown')
            symbol = state.get('symbol', 'UNKNOWN')
            cash = state.get('cash', 100.0)
            holdings = state.get('holdings', 0.0)
            position = state.get('position', 0)
            entry_price = state.get('entry_price')
            total_fees = state.get('total_fees_paid', state.get('total_fees', 0.0))
            trades = state.get('trades', [])
            
            # Get current price
            current_price = get_current_price(symbol) or (entry_price if entry_price else 100.0)
            
            # Calculate portfolio value
            if position == 1 and holdings > 0:
                gross_value = holdings * current_price
                exit_fee = gross_value * 0.001  # 0.1%
                portfolio_value = cash + (gross_value - exit_fee)
            else:
                portfolio_value = cash
            
            # Calculate return
            initial_investment = 100.0  # Standard starting amount
            total_return = ((portfolio_value / initial_investment) - 1) * 100
            
            position_str = 'LONG' if position == 1 else 'FLAT'
            if position == 1:
                active_bots += 1
            
            # Get additional data
            ensemble_data = get_ensemble_prediction(symbol)
            onchain_data = get_onchain_metrics(symbol)
            
            # Build bot data
            bot_data = {
                'bot_id': f"{name}_{symbol}",
                'name': BOT_REGISTRY.get(f"{name}_{symbol}", {}).get('name', f"{name} {symbol}"),
                'strategy': BOT_REGISTRY.get(f"{name}_{symbol}", {}).get('strategy', 'unknown'),
                'type': BOT_REGISTRY.get(f"{name}_{symbol}", {}).get('type', 'unknown'),
                'symbol': symbol,
                'position': position_str,
                'cash': cash,
                'holdings': holdings,
                'portfolio_value': portfolio_value,
                'total_return': total_return,
                'trades_count': len(trades),
                'price': current_price,
                'total_fees': total_fees,
                'ensemble': ensemble_data,
                'onchain': onchain_data,
                'fear_greed': fear_greed,
                'last_update': datetime.now().isoformat()
            }
            
            # Update dashboard
            success = update_bot_status(bot_data)
            
            status = "✓" if success else "✗"
            print(f"{status} {name:15} {symbol:10} | {position_str:4} | ${portfolio_value:8.2f} | {total_return:+5.2f}%")
            
            # Accumulate totals
            total_portfolio_value += portfolio_value
            total_invested += initial_investment
            bot_count += 1
            
        except Exception as e:
            print(f"✗ Error processing {filename}: {e}")
    
    # Calculate combined P&L
    if total_invested > 0:
        combined_return = ((total_portfolio_value / total_invested) - 1) * 100
        
        # Update summary to dashboard
        summary_data = {
            'bot_id': 'COMBINED_SUMMARY',
            'name': 'All Bots Combined',
            'type': 'summary',
            'portfolio_value': total_portfolio_value,
            'total_invested': total_invested,
            'combined_return': combined_return,
            'active_bots': active_bots,
            'total_bots': bot_count,
            'fear_greed': fear_greed,
            'last_update': datetime.now().isoformat()
        }
        
        update_bot_status(summary_data)
        
        print(f"\n{'='*80}")
        print(f"COMBINED SUMMARY")
        print(f"{'='*80}")
        print(f"Total Portfolio:     ${total_portfolio_value:,.2f}")
        print(f"Total Invested:      ${total_invested:,.2f}")
        print(f"Combined Return:     {combined_return:+.2f}%")
        print(f"Active Bots:         {active_bots}/{bot_count}")
        print(f"{'='*80}\n")

if __name__ == '__main__':
    scan_and_update()
