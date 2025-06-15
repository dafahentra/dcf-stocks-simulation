CURR = {'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥', 'INR': '₹', 'KRW': '₩', 'IDR': 'Rp'}

def get_custom_css():
    """CSS"""
    return """
    <style>
        /* Hide Streamlit UI elements */
        #MainMenu, footer, header, .stDeployButton, .stToolbar, ._profileContainer {
            visibility: hidden; display: none;
        }
        
        /* Remove padding at top */
        .block-container { padding-top: 1rem; }
        
        /* Headers */
        .main-header {
            font-size: 2.5rem; font-weight: 300; margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #c584f7 0%, #a068d8 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        
        .sub-header { font-size: 1.1rem; color: #888; margin-bottom: 2rem; }
        
        /* Cards */
        .metric-card {
            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);
            padding: 1.5rem; border-radius: 12px;
        }
        
        .summary-box {
            background: rgba(197,132,247,0.1); border: 1px solid rgba(197,132,247,0.3);
            padding: 1.5rem; border-radius: 12px; margin: 2rem 0;
        }
        
        .input-section {
            background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
            padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
        }
    </style>
    """

def metric_card(label: str, value: str, delta: str = None) -> str:
    """Metric card"""
    d = f'<div style="color: {"#4ade80" if delta and "+" in delta[1] else "#f87171"}">{delta[1]}</div>' if delta else ''
    return f'<div class="metric-card"><div style="color:#888;font-size:0.875rem">{label}</div><div style="font-size:1.75rem;font-weight:600">{value}</div>{d}</div>'

def summary_box(title: str, content: str) -> str:
    """Summary box"""
    return f'<div class="summary-box"><div style="font-size:1.25rem;font-weight:600;color:#c584f7;margin-bottom:1rem">{title}</div><div>{content}</div></div>'

def fmt_curr(amt: float, curr: str = 'USD') -> str:
    """Format currency"""
    if not amt: return "N/A"
    s = CURR.get(curr, '$')
    for m, sfx in [(1e12,'T'), (1e9,'B'), (1e6,'M'), (1e3,'K')]:
        if abs(amt) >= m: return f"{s}{amt/m:.1f}{sfx}"
    return f"{s}{amt:.2f}"

def fmt_pct(val: float, dec: int = 1) -> str:
    """Format percentage"""
    return f"{val*100:.{dec}f}%" if val is not None else "N/A"