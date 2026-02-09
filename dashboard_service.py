#!/usr/bin/env python3
"""
Crypto Bot Dashboard Service - MOBILE-FIRST REDESIGN
Cloud Run compatible Flask app optimized for mobile viewing

Features:
- Large, readable numbers for mobile
- 2-column card layout
- Vertical scrolling
- Touch-friendly interface
- Auto-refresh every 30 seconds
"""

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import os
import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Configuration
API_KEY = os.getenv('DASHBOARD_API_KEY', 'crypto-bot-2026')
GCS_BUCKET = os.getenv('GCS_BUCKET', 'haley_chat')

# Paths for state files (will be mounted from GCS or local)
STATE_DIR = Path('/app/state') if os.path.exists('/app/state') else Path('.')

# MOBILE-FIRST DASHBOARD TEMPLATE
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>🤖 Bot Dashboard</title>
    <style>
        :root {
            --bg-primary: #0a0e14;
            --bg-secondary: #141b24;
            --bg-card: #1a2332;
            --border-color: #2d3748;
            --text-primary: #f7fafc;
            --text-secondary: #a0aec0;
            --text-muted: #718096;
            --color-green: #48bb78;
            --color-green-bg: rgba(72, 187, 120, 0.15);
            --color-red: #f56565;
            --color-red-bg: rgba(245, 101, 101, 0.15);
            --color-blue: #4299e1;
            --color-blue-bg: rgba(66, 153, 225, 0.15);
            --color-yellow: #ecc94b;
            --color-orange: #ed8936;
            --font-mono: 'SF Mono', Monaco, 'Cascadia Code', monospace;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.4;
            min-height: 100vh;
            padding-bottom: 40px;
        }
        
        /* Header - Fixed at top */
        .header {
            background: linear-gradient(135deg, #1a365d 0%, #2d3748 100%);
            padding: 20px 16px;
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid var(--border-color);
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 4px;
        }
        
        .header-time {
            font-size: 14px;
            color: var(--text-muted);
        }
        
        .refresh-btn {
            position: absolute;
            top: 20px;
            right: 16px;
            background: rgba(255,255,255,0.1);
            border: none;
            color: white;
            width: 44px;
            height: 44px;
            border-radius: 12px;
            font-size: 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Portfolio Overview - BIG NUMBERS */
        .overview-section {
            padding: 24px 16px;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
        }
        
        .overview-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .overview-card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 20px 16px;
            border: 1px solid var(--border-color);
            text-align: center;
        }
        
        .overview-card.full-width {
            grid-column: 1 / -1;
        }
        
        .overview-label {
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .overview-value {
            font-size: 36px;
            font-weight: 800;
            font-family: var(--font-mono);
            letter-spacing: -1px;
        }
        
        .overview-value.xlarge {
            font-size: 48px;
        }
        
        .overview-subtitle {
            font-size: 15px;
            margin-top: 6px;
            font-weight: 600;
        }
        
        .positive { color: var(--color-green); }
        .negative { color: var(--color-red); }
        .neutral { color: var(--text-secondary); }
        .blue { color: var(--color-blue); }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge-halted {
            background: var(--color-red-bg);
            color: var(--color-red);
        }
        
        .badge-active {
            background: var(--color-green-bg);
            color: var(--color-green);
        }
        
        .badge-warning {
            background: rgba(237, 137, 54, 0.15);
            color: var(--color-orange);
        }
        
        /* Section Headers */
        .section {
            padding: 24px 16px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        
        .section-title {
            font-size: 20px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .section-count {
            background: var(--bg-card);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            color: var(--text-muted);
        }
        
        /* Bot Cards - 2 per row */
        .bot-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .bot-card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 16px;
            border: 1px solid var(--border-color);
            position: relative;
        }
        
        .bot-card.halted {
            border-color: var(--color-red);
            background: linear-gradient(135deg, var(--bg-card) 0%, rgba(245, 101, 101, 0.1) 100%);
        }
        
        .bot-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        
        .bot-name {
            font-size: 16px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .bot-status {
            font-size: 10px;
            padding: 3px 8px;
        }
        
        .bot-portfolio {
            font-size: 32px;
            font-weight: 800;
            font-family: var(--font-mono);
            margin-bottom: 4px;
        }
        
        .bot-pnl {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 12px;
        }
        
        .bot-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            padding-top: 12px;
            border-top: 1px solid var(--border-color);
        }
        
        .bot-stat {
            text-align: center;
        }
        
        .bot-stat-value {
            font-size: 18px;
            font-weight: 700;
            font-family: var(--font-mono);
        }
        
        .bot-stat-label {
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-top: 2px;
        }
        
        .bot-positions {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid var(--border-color);
        }
        
        .position-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--color-blue-bg);
            color: var(--color-blue);
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        
        /* Summary Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .stat-item {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid var(--border-color);
        }
        
        .stat-label {
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 800;
            font-family: var(--font-mono);
        }
        
        /* Alert Box */
        .alert {
            background: linear-gradient(135deg, rgba(245, 101, 101, 0.2) 0%, rgba(245, 101, 101, 0.1) 100%);
            border: 1px solid var(--color-red);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .alert-icon {
            font-size: 24px;
        }
        
        .alert-text {
            font-size: 14px;
            font-weight: 600;
            color: var(--color-red);
        }
        
        /* Footer */
        .footer {
            padding: 24px 16px;
            text-align: center;
        }
        
        .api-link {
            color: var(--color-blue);
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
        }
        
        /* Desktop adjustments */
        @media (min-width: 768px) {
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            .overview-value {
                font-size: 48px;
            }
            .overview-value.xlarge {
                font-size: 64px;
            }
            .bot-portfolio {
                font-size: 36px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🤖 Bot Dashboard</h1>
            <div class="header-time">{{ timestamp }}</div>
            <button class="refresh-btn" onclick="location.reload()">🔄</button>
        </div>
        
        <!-- Portfolio Overview -->
        <div class="overview-section">
            <div class="overview-grid">
                <!-- Total Portfolio Value -->
                <div class="overview-card full-width">
                    <div class="overview-label">Total Portfolio Value</div>
                    <div class="overview-value xlarge {{ 'positive' if summary.total_pnl >= 0 else 'negative' }}">
                        ${{ "%.0f"|format(summary.portfolio_value) }}
                    </div>
                    <div class="overview-subtitle {{ 'positive' if summary.total_pnl >= 0 else 'negative' }}">
                        {{ "+%.2f"|format(summary.total_pnl) if summary.total_pnl >= 0 else "%.2f"|format(summary.total_pnl) }}
                        ({{ "+%.2f"|format(summary.total_pnl_pct) if summary.total_pnl_pct >= 0 else "%.2f"|format(summary.total_pnl_pct) }}%)
                    </div>
                </div>
                
                <!-- Daily P&L -->
                <div class="overview-card">
                    <div class="overview-label">Today's P&L</div>
                    <div class="overview-value {{ 'positive' if summary.daily_pnl >= 0 else 'negative' }}">
                        {{ "+%.0f"|format(summary.daily_pnl) if summary.daily_pnl >= 0 else "%.0f"|format(summary.daily_pnl) }}
                    </div>
                    <div class="overview-subtitle {{ 'positive' if summary.daily_pnl_pct >= 0 else 'negative' }}">
                        {{ "%.2f"|format(summary.daily_pnl_pct) }}%
                    </div>
                </div>
                
                <!-- Active Positions -->
                <div class="overview-card">
                    <div class="overview-label">Positions</div>
                    <div class="overview-value blue">{{ summary.active_positions }}</div>
                    <div class="overview-subtitle neutral">Active</div>
                </div>
            </div>
            
            {% if summary.halted_bots > 0 %}
            <div class="alert" style="margin-top: 16px;">
                <div class="alert-icon">🚨</div>
                <div class="alert-text">{{ summary.halted_bots }} bot{{ 's' if summary.halted_bots > 1 else '' }} halted (circuit breaker)</div>
            </div>
            {% endif %}
        </div>
        
        <!-- Bot Cards Section -->
        <div class="section">
            <div class="section-header">
                <div class="section-title">
                    🤖 Active Bots
                </div>
                <div class="section-count">{{ summary.total_bots }}</div>
            </div>
            
            <div class="bot-grid">
                {% for bot in bots %}
                <div class="bot-card {{ 'halted' if bot.halted else '' }}">
                    <div class="bot-header">
                        <div class="bot-name">{{ bot.name[:3] }}</div>
                        {% if bot.halted %}
                        <span class="badge badge-halted bot-status">HALTED</span>
                        {% elif bot.positions > 0 %}
                        <span class="badge badge-active bot-status">ACTIVE</span>
                        {% else %}
                        <span class="badge badge-warning bot-status">IDLE</span>
                        {% endif %}
                    </div>
                    
                    <div class="bot-portfolio {{ 'positive' if bot.pnl >= 0 else 'negative' }}">
                        ${{ "%.0f"|format(bot.portfolio_value) }}
                    </div>
                    
                    <div class="bot-pnl {{ 'positive' if bot.pnl >= 0 else 'negative' }}">
                        {{ "+%.2f"|format(bot.pnl) if bot.pnl >= 0 else "%.2f"|format(bot.pnl) }}
                        ({{ "+%.1f"|format(bot.pnl_pct) if bot.pnl_pct >= 0 else "%.1f"|format(bot.pnl_pct) }}%)
                    </div>
                    
                    <div class="bot-stats">
                        <div class="bot-stat">
                            <div class="bot-stat-value">{{ bot.positions }}</div>
                            <div class="bot-stat-label">Positions</div>
                        </div>
                        <div class="bot-stat">
                            <div class="bot-stat-value">{{ bot.trades }}</div>
                            <div class="bot-stat-label">Trades</div>
                        </div>
                        <div class="bot-stat">
                            <div class="bot-stat-value {{ 'negative' if bot.drawdown > 15 else 'neutral' }}">{{ "%.1f"|format(bot.drawdown) }}%</div>
                            <div class="bot-stat-label">Drawdown</div>
                        </div>
                        <div class="bot-stat">
                            <div class="bot-stat-value">${{ "%.0f"|format(bot.cash) }}</div>
                            <div class="bot-stat-label">Cash</div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Summary Stats -->
        <div class="section">
            <div class="section-header">
                <div class="section-title">
                    📊 Stats
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Total Trades</div>
                    <div class="stat-value">{{ summary.total_trades }}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Started With</div>
                    <div class="stat-value">${{ "%.0f"|format(summary.starting_value) }}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Avg Drawdown</div>
                    <div class="stat-value {{ 'negative' if summary.avg_drawdown > 15 else 'neutral' }}">{{ "%.1f"|format(summary.avg_drawdown) }}%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Bots Running</div>
                    <div class="stat-value">{{ summary.running_bots }}/{{ summary.total_bots }}</div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <a href="/api/status" class="api-link">View API →</a>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function() {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
'''


def load_bot_data():
    """Load bot data from state files or use sample data."""
    bots = []
    
    # Try to load from local state files first
    try:
        for container in ['aggressive', 'balanced', 'conservative']:
            state_file = STATE_DIR / f'state_container_{container}.json'
            if state_file.exists():
                with open(state_file) as f:
                    data = json.load(f)
                
                portfolio = data.get('portfolio_value', 150)
                starting = 150.0
                pnl = portfolio - starting
                pnl_pct = (pnl / starting) * 100
                
                daily_status = data.get('daily_pnl_status', {})
                
                bots.append({
                    'name': data.get('container', container).upper(),
                    'portfolio_value': portfolio,
                    'starting_value': starting,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'cash': data.get('cash', portfolio),
                    'positions': len(data.get('positions', {})),
                    'trades': data.get('trade_count', 0),
                    'drawdown': ((data.get('peak_value', starting) - portfolio) / data.get('peak_value', starting)) * 100,
                    'halted': data.get('drawdown_triggered', False) or not daily_status.get('can_trade', True),
                    'daily_pnl': daily_status.get('daily_pnl', 0) * portfolio
                })
    except Exception as e:
        print(f"Error loading state files: {e}")
    
    # If no bots loaded, use sample data
    if not bots:
        bots = [
            {
                'name': 'AGG',
                'portfolio_value': 148.5,
                'starting_value': 150.0,
                'pnl': -1.5,
                'pnl_pct': -1.0,
                'cash': 100.0,
                'positions': 1,
                'trades': 12,
                'drawdown': 1.0,
                'halted': False,
                'daily_pnl': -0.5
            },
            {
                'name': 'BAL',
                'portfolio_value': 152.3,
                'starting_value': 150.0,
                'pnl': 2.3,
                'pnl_pct': 1.53,
                'cash': 80.0,
                'positions': 2,
                'trades': 8,
                'drawdown': 0.0,
                'halted': False,
                'daily_pnl': 1.2
            },
            {
                'name': 'CON',
                'portfolio_value': 151.8,
                'starting_value': 150.0,
                'pnl': 1.8,
                'pnl_pct': 1.2,
                'cash': 75.0,
                'positions': 2,
                'trades': 6,
                'drawdown': 0.0,
                'halted': False,
                'daily_pnl': 0.8
            }
        ]
    
    return bots


def calculate_summary(bots):
    """Calculate aggregate statistics."""
    if not bots:
        return {
            'portfolio_value': 150.0,
            'starting_value': 150.0,
            'total_pnl': 0,
            'total_pnl_pct': 0,
            'daily_pnl': 0,
            'daily_pnl_pct': 0,
            'active_positions': 0,
            'halted_bots': 0,
            'total_trades': 0,
            'starting_value': 150.0 * len(bots) if bots else 150.0,
            'avg_drawdown': 0,
            'running_bots': 0,
            'total_bots': len(bots)
        }
    
    total_value = sum(b['portfolio_value'] for b in bots)
    starting = sum(b['starting_value'] for b in bots)
    total_pnl = total_value - starting
    total_pnl_pct = (total_pnl / starting) * 100 if starting > 0 else 0
    
    daily_pnl = sum(b.get('daily_pnl', 0) for b in bots)
    daily_pnl_pct = (daily_pnl / starting) * 100 if starting > 0 else 0
    
    active_positions = sum(b['positions'] for b in bots)
    halted_bots = sum(1 for b in bots if b['halted'])
    total_trades = sum(b['trades'] for b in bots)
    avg_drawdown = sum(b['drawdown'] for b in bots) / len(bots)
    
    return {
        'portfolio_value': total_value,
        'starting_value': starting,
        'total_pnl': total_pnl,
        'total_pnl_pct': total_pnl_pct,
        'daily_pnl': daily_pnl,
        'daily_pnl_pct': daily_pnl_pct,
        'active_positions': active_positions,
        'halted_bots': halted_bots,
        'total_trades': total_trades,
        'avg_drawdown': avg_drawdown,
        'running_bots': len(bots) - halted_bots,
        'total_bots': len(bots)
    }


@app.route('/')
def dashboard():
    """Render the mobile-first HTML dashboard."""
    bots = load_bot_data()
    summary = calculate_summary(bots)
    
    return render_template_string(
        DASHBOARD_HTML,
        bots=bots,
        summary=summary,
        timestamp=datetime.now().strftime('%b %d, %I:%M %p')
    )


@app.route('/api/status')
def api_status():
    """Return JSON API with bot status."""
    bots = load_bot_data()
    summary = calculate_summary(bots)
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'summary': summary,
        'bots': bots
    })


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/update', methods=['POST'])
def update_bot_data():
    """Receive bot data updates (requires API key)."""
    api_key = request.headers.get('X-API-Key')
    if api_key != API_KEY:
        return jsonify({'error': 'Invalid API key'}), 401
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    bot_name = data.get('bot_name')
    if bot_name:
        bot_data[bot_name] = {
            **data,
            'last_update': datetime.now().isoformat()
        }
    
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"🚀 Starting Crypto Bot Dashboard Service")
    print(f"   URL: http://0.0.0.0:{port}")
    print(f"   Mobile-optimized design loaded")
    app.run(host='0.0.0.0', port=port)
