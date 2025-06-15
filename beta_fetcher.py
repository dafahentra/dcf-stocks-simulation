import numpy as np
import yfinance as yf
import streamlit as st

# Gunakan requests standar sebagai fallback
try:
    from curl_cffi import requests
except ImportError:
    import requests

MARKETS = {
    'US': {'idx': '^GSPC', 'sfx': '', 'mp': 0.065, 'rf': 0.045},
    'UK': {'idx': '^FTSE', 'sfx': '.L', 'mp': 0.060, 'rf': 0.040},
    'DE': {'idx': '^GDAXI', 'sfx': '.DE', 'mp': 0.055, 'rf': 0.025},
    'JP': {'idx': '^N225', 'sfx': '.T', 'mp': 0.050, 'rf': 0.001},
    'HK': {'idx': '^HSI', 'sfx': '.HK', 'mp': 0.065, 'rf': 0.040},
    'IN': {'idx': '^BSESN', 'sfx': '.NS', 'mp': 0.080, 'rf': 0.070},
    'CN': {'idx': '000001.SS', 'sfx': '.SS', 'mp': 0.070, 'rf': 0.025},
}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_beta(ticker: str, period: str = "2y"):
    """Fetch beta & market info in one go"""
    try:
        ticker = ticker.upper().strip()  # Add strip()
        
        # Create session with proper error handling
        try:
            session = requests.Session(impersonate="chrome120")
        except:
            session = None
            
        stock = yf.Ticker(ticker, session=session)
        
        # Market detection with validation
        market = 'US'  # Default
        for k, v in MARKETS.items():
            if v['sfx'] and ticker.endswith(v['sfx']):
                market = k
                break
                
        mkt = MARKETS[market]
        
        # Try info beta first
        info = stock.info
        if info and (beta := info.get('beta')) and 0.1 <= beta <= 3.0:
            return float(beta), None, {'market': market, 'market_premium': mkt['mp'], 'risk_free': mkt['rf']}
        
        # Calculate beta
        s_hist = stock.history(period=period)['Close']
        m_hist = yf.Ticker(mkt['idx'], session=session).history(period=period)['Close']
        
        if len(s_hist) < 60 or len(m_hist) < 60:
            return None, "Insufficient data", None
        
        # Returns & beta calc with better error handling
        s_ret = s_hist.pct_change().dropna()
        m_ret = m_hist.pct_change().dropna()
        
        # Align the series
        s_ret, m_ret = s_ret.align(m_ret, join='inner')
        
        # Remove outliers
        mask = (abs(s_ret) < 0.5) & (abs(m_ret) < 0.5)
        clean_s = s_ret[mask]
        clean_m = m_ret[mask]
        
        if len(clean_s) < 60:
            return None, "Insufficient clean data", None
        
        # Calculate beta with validation
        var_m = clean_m.var()
        if var_m == 0 or np.isnan(var_m):
            return None, "Market variance is zero", None
            
        beta = clean_s.cov(clean_m) / var_m
        
        # Validate beta
        if np.isnan(beta) or np.isinf(beta):
            return None, "Invalid beta calculation", None
            
        beta = np.clip(beta, 0.1, 3.0)
        
        return beta, None, {'market': market, 'market_premium': mkt['mp'], 'risk_free': mkt['rf']}
        
    except Exception as e:
        return None, f"Error: {str(e)}", None