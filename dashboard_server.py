#!/usr/bin/env python3
"""
Dashboard Server for Crypto Bot - MOBILE-FIRST REDESIGN

A Flask server optimized for mobile viewing with:
- Large, readable numbers
- 2-column card layout
- Vertical scrolling
- Touch-friendly interface

Usage:
    python dashboard_server.py
    
Environment variables:
    PORT - Server port (default: 5000)
    HOST - Server host (default: 0.0.0.0)
    DEBUG - Debug mode (default: False)
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Configuration
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Paths
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / 'logs'
STATE_PATTERN = 'state_container_*.json'


def parse_container_state(filepath):
    """Parse container state JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        name = data.get('container', Path(filepath).stem.replace('state_container_', ''))
        portfolio = data.get('portfolio_value', 0)
        peak = data.get('peak_value', portfolio)
        cash = data.get('cash', 0)
        drawdown = (peak - portfolio) / peak if peak > 0 else 0
        
        positions = data.get('positions', {})
        active_positions = len(positions)
        position_value = sum(p.get('position_value', 0) for p in positions.values())
        
        # Calculate total P&L from starting value of 150
        starting_value = 150.0
        total_pnl = portfolio - starting_value
        total_pnl_pct = (total_pnl / starting_value) * 100
        
        # Daily P&L from tracker
        daily_pnl_status = data.get('daily_pnl_status', {})
        daily_pnl = daily_pnl_status.get('daily_pnl', 0)
        daily_pnl_pct = daily_pnl_status.get('daily_pnl_pct', 0) * 100
        
        return {
            'name': name,
            'portfolio_value': portfolio,
            'starting_value': starting_value,
            'peak_value': peak,
            'cash': cash,
            'position_value': position_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'daily_pnl': daily_pnl,
            'daily_pnl_pct': daily_pnl_pct,
            'drawdown_pct': drawdown * 100,
            'drawdown_triggered': data.get('drawdown_triggered', False),
            'active_positions': active_positions,
            'trade_count': data.get('trade_count', 0),
            'positions': positions,
            'is_halted': data.get('drawdown_triggered', False) or not daily_pnl_status.get('can_trade', True)
        }
    except Exception as e:
        return {
            'name': Path(filepath).stem,
            'error': str(e),
            'portfolio_value': 0,
            'active_positions': 0
        }


def get_bot_status():
    """Get status of all container bots."""
    bots = []
    
    # Read container state files
    state_files = list(BASE_DIR.glob(STATE_PATTERN))
    for state_file in state_files:
        state = parse_container_state(state_file)
        bots.append(state)
    
    # Sort by name
    bots.sort(key=lambda x: x.get('name', ''))
    
    return bots


def aggregate_stats(bots):
    """Calculate aggregate statistics."""
    if not bots:
        return {
            'total_bots': 0,
            'total_value': 150.0,
            'total_pnl': 0,
            'total_pnl_pct': 0,
            'daily_pnl': 0,
            'daily_pnl_pct': 0,
            'active_positions': 0,
            'halted_bots': 0,
            'total_trades': 0,
            'avg_drawdown': 0
        }
    
    total_value = sum(b.get('portfolio_value', 0) for b in bots)
    total_starting = sum(b.get('starting_value', 150) for b in bots)
    total_pnl = total_value - total_starting
    total_pnl_pct = (total_pnl / total_starting) * 100 if total_starting > 0 else 0
    
    daily_pnl = sum(b.get('daily_pnl', 0) for b in bots)
    daily_pnl_pct = (daily_pnl / total_starting) * 100 if total_starting > 0 else 0
    
    active_positions = sum(b.get('active_positions', 0) for b in bots)
    halted_bots = sum(1 for b in bots if b.get('is_halted', False))
    total_trades = sum(b.get('trade_count', 0) for b in bots)
    
    avg_drawdown = sum(b.get('drawdown_pct', 0) for b in bots) / len(bots)
    
    return {
        'total_bots': len(bots),
        'total_value': round(total_value, 2),
        'total_starting': total_starting,
        'total_pnl': round(total_pnl, 2),
        'total_pnl_pct': round(total_pnl_pct, 2),
        'daily_pnl': round(daily_pnl, 2),
        'daily_pnl_pct': round(daily_pnl_pct, 2),
        'active_positions': active_positions,
        'halted_bots': halted_bots,
        'total_trades': total_trades,
        'avg_drawdown': round(avg_drawdown, 2)
    }


# MOBILE-FIRST DASHBOARD TEMPLATE
DASHBOARD_TEMPLATE = '''
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
        
        .position-tag.sell {
            background: var(--color-red-bg);
            color: var(--color-red);
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
        
        /* API Link Footer */
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
        
        /* Animations */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .updating {
            animation: pulse 1s infinite;
        }
        
        /* Desktop adjustments */
        @media (min-width: 768px) {
            .overview-value {
                font-size: 48px;
            }
            .overview-value.xlarge {
                font-size: 64px;
            }
            .bot-portfolio {
                font-size: 36px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
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
                    <div class="overview-value xlarge ${ 'positive' if stats.total_pnl >= 0 else 'negative' }">
                        ${{ "%.0f"|format(stats.total_value) }}
                    </div>
                    <div class="overview-subtitle ${ 'positive' if stats.total_pnl >= 0 else 'negative' }">
                        {{ "+%.2f"|format(stats.total_pnl) if stats.total_pnl >= 0 else "%.2f"|format(stats.total_pnl) }}
                        ({{ "+%.2f"|format(stats.total_pnl_pct) if stats.total_pnl_pct >= 0 else "%.2f"|format(stats.total_pnl_pct) }}%)
                    </div>
                </div>
                
                <!-- Daily P&L -->
                <div class="overview-card">
                    <div class="overview-label">Today's P&L</div>
                    <div class="overview-value ${ 'positive' if stats.daily_pnl >= 0 else 'negative' }">
                        {{ "+%.0f"|format(stats.daily_pnl) if stats.daily_pnl >= 0 else "%.0f"|format(stats.daily_pnl) }}
                    </div>
                    <div class="overview-subtitle ${ 'positive' if stats.daily_pnl_pct >= 0 else 'negative' }">
                        {{ "%.2f"|format(stats.daily_pnl_pct) }}%
                    </div>
                </div>
                
                <!-- Active Positions -->
                <div class="overview-card">
                    <div class="overview-label">Positions</div>
                    <div class="overview-value blue">{{ stats.active_positions }}</div>
                    <div class="overview-subtitle neutral">Active</div>
                </div>
            </div>
            
            {% if stats.halted_bots > 0 %}
            <div class="alert" style="margin-top: 16px;">
                <div class="alert-icon">🚨</div>
                <div class="alert-text">{{ stats.halted_bots }} bot{{ 's' if stats.halted_bots > 1 else '' }} halted (circuit breaker)</div>
            </div>
            {% endif %}
        </div>
        
        <!-- Bot Cards Section -->
        <div class="section">
            <div class="section-header">
                <div class="section-title">
                    🤖 Active Bots
                </div>
                <div class="section-count">{{ stats.total_bots }}</div>
            </div>
            
            <div class="bot-grid">
                {% for bot in bots %}
                <div class="bot-card {{ 'halted' if bot.is_halted else '' }}">
                    <div class="bot-header">
                        <div class="bot-name">{{ bot.name[:3] }}</div>
                        {% if bot.is_halted %}
                        <span class="badge badge-halted bot-status">HALTED</span>
                        {% elif bot.active_positions > 0 %}
                        <span class="badge badge-active bot-status">ACTIVE</span>
                        {% else %}
                        <span class="badge badge-warning bot-status">IDLE</span>
                        {% endif %}
                    </div>
                    
                    <div class="bot-portfolio {{ 'positive' if bot.total_pnl >= 0 else 'negative' }}">
                        ${{ "%.0f"|format(bot.portfolio_value) }}
                    </div>
                    
                    <div class="bot-pnl {{ 'positive' if bot.total_pnl >= 0 else 'negative' }}">
                        {{ "+%.2f"|format(bot.total_pnl) if bot.total_pnl >= 0 else "%.2f"|format(bot.total_pnl) }}
                        ({{ "+%.1f"|format(bot.total_pnl_pct) if bot.total_pnl_pct >= 0 else "%.1f"|format(bot.total_pnl_pct) }}%)
                    </div>
                    
                    <div class="bot-stats">
                        <div class="bot-stat">
                            <div class="bot-stat-value">{{ bot.active_positions }}</div>
                            <div class="bot-stat-label">Positions</div>
                        </div>
                        <div class="bot-stat">
                            <div class="bot-stat-value">{{ bot.trade_count }}</div>
                            <div class="bot-stat-label">Trades</div>
                        </div>
                        <div class="bot-stat">
                            <div class="bot-stat-value {{ 'negative' if bot.drawdown_pct > 15 else 'neutral' }}">{{ "%.1f"|format(bot.drawdown_pct) }}%</div>
                            <div class="bot-stat-label">Drawdown</div>
                        </div>
                        <div class="bot-stat">
                            <div class="bot-stat-value">${{ "%.0f"|format(bot.cash) }}</div>
                            <div class="bot-stat-label">Cash</div>
                        </div>
                    </div>
                    
                    {% if bot.positions %}
                    <div class="bot-positions">
                        {% for symbol, pos in bot.positions.items() %}
                        <span class="position-tag">
                            {{ symbol.replace('USDT', '') }}
                            <small>${{ "%.0f"|format(pos.position_value) }}</small>
                        </span>
                        {% endfor %}
                    </div>
                    {% endif %}
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
                    <div class="stat-value">{{ stats.total_trades }}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Started With</div>
                    <div class="stat-value">${{ "%.0f"|format(stats.total_starting) }}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Avg Drawdown</div>
                    <div class="stat-value {{ 'negative' if stats.avg_drawdown > 15 else 'neutral' }}">{{ "%.1f"|format(stats.avg_drawdown) }}%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Bots Running</div>
                    <div class="stat-value">{{ stats.total_bots - stats.halted_bots }}/{{ stats.total_bots }}</div>
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


@app.route('/')
def dashboard():
    """Render the mobile-first HTML dashboard."""
    bots = get_bot_status()
    stats = aggregate_stats(bots)
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        bots=bots,
        stats=stats,
        timestamp=datetime.now().strftime('%b %d, %I:%M %p')
    )


@app.route('/api/status')
def api_status():
    """Return JSON API with bot status."""
    bots = get_bot_status()
    stats = aggregate_stats(bots)
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'stats': stats,
        'bots': bots
    })


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print(f"🚀 Starting Crypto Bot Dashboard Server (Mobile-First)")
    print(f"   URL: http://{HOST}:{PORT}")
    print(f"   Optimized for mobile viewing")
    app.run(host=HOST, port=PORT, debug=DEBUG)
