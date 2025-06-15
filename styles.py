"""
Ultra-Optimized Styling Module
"""

CURR = {'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥', 'INR': '₹', 'KRW': '₩', 'IDR': 'Rp'}

def get_custom_css():
    """Minimal essential CSS"""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif !important; }
        .stApp { background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%); }
        
        .main-header {
            font-size: 2.5rem; font-weight: 300; margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #c584f7 0%, #a068d8 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        
        .sub-header { font-size: 1.1rem; color: #888; margin-bottom: 2rem; }
        
        .metric-card {
            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);
            padding: 1.5rem; border-radius: 12px; backdrop-filter: blur(10px);
        }
        
        .metric-label { color: #888; font-size: 0.875rem; margin-bottom: 0.25rem; }
        .metric-value { font-size: 1.75rem; font-weight: 600; color: #fff; }
        .metric-delta { font-size: 0.875rem; margin-top: 0.25rem; }
        
        .positive { color: #4ade80; }
        .negative { color: #f87171; }
        
        .summary-box {
            background: rgba(197,132,247,0.1); border: 1px solid rgba(197,132,247,0.3);
            padding: 1.5rem; border-radius: 12px; margin: 2rem 0;
        }
        
        .summary-title { font-size: 1.25rem; font-weight: 600; color: #c584f7; margin-bottom: 1rem; }
        
        .input-section {
            background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
            padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; position: relative;
        }
        
        .input-section-title { 
            font-size: 1.1rem; font-weight: 500; color: #c584f7; margin-bottom: 0rem;
            text-align: left;
            width: 100%;
            display: flex;
            align-items: center;
        }
        
        div[data-testid="stSidebar"] {
            background: rgba(0,0,0,0.3); border-right: 1px solid rgba(255,255,255,0.05);
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #c584f7 0%, #a068d8 100%);
            color: white; border: none; padding: 0.75rem 2rem; font-weight: 500;
            border-radius: 8px; transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px); box-shadow: 0 10px 30px rgba(197,132,247,0.3);
        }
        
        input { background: rgba(255,255,255,0.05) !important; }
    </style>
    """

def metric_card(label: str, value: str, delta: str = None) -> str:
    """Metric card HTML"""
    d = f'<div class="metric-delta {delta[0]}">{delta[1]}</div>' if delta else ''
    return f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div>{d}</div>'

def summary_box(title: str, content: str) -> str:
    """Summary box HTML"""
    return f'<div class="summary-box"><div class="summary-title">{title}</div><div class="summary-text">{content}</div></div>'

def fmt_curr(amt: float, curr: str = 'USD') -> str:
    """Format currency"""
    if not amt: return "N/A"
    s = CURR.get(curr, '$')
    mag = [(1e12,'T'), (1e9,'B'), (1e6,'M'), (1e3,'K')]
    for m, sfx in mag:
        if abs(amt) >= m: return f"{s}{amt/m:.1f}{sfx}"
    return f"{s}{amt:.2f}"

def fmt_pct(val: float, dec: int = 1) -> str:
    """Format percentage"""
    return f"{val*100:.{dec}f}%" if val is not None else "N/A"