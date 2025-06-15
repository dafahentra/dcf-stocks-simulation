"""Optimized DCF Valuation Tool"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json

from dcf_engine import DCFEngine
from beta_fetcher import fetch_stock_beta
from visualization import *
from styles import *

st.set_page_config(page_title="DCF Valuation Tool", page_icon="", layout="wide")
st.markdown(get_custom_css(), unsafe_allow_html=True)

if 'valuation_results' not in st.session_state:
    st.session_state.valuation_results = None

def growth_stats(vals: list) -> dict:
    """Calculate growth statistics"""
    if len(vals) < 2: return {'mean': 0.05, 'std': 0.03}
    gr = np.diff(vals) / vals[:-1]
    gr = np.clip(gr, -0.5, 1.0)
    return {'mean': float(gr.mean()), 'std': float(gr.std()) if len(gr) > 1 else 0.03}

def main():
    # Header
    st.markdown('<h1 class="main-header">Stocks Valuation Simulation</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Using Monte Carlo for intrinsic value estimation</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        st.subheader("Market Parameters")
        rf = st.number_input("Risk-Free Rate", 0.0, 0.10, 0.045, 0.005, format="%.3f")
        mp = st.number_input("Market Risk Premium", 0.03, 0.12, st.session_state.get('mp_calc', 0.065), 0.005, format="%.3f")
        
        st.subheader("Simulation Settings")
        n_sims = st.select_slider("Monte Carlo Simulations", [1000, 5000, 10000, 25000, 50000], 10000)
        n_years = st.slider("Projection Years", 3, 10, 5)
    
    # Main content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Company Info
        st.markdown('<div class="input-section"><div style="font-size:1.3rem;font-weight:500;color:#c584f7">Company Information</div>', unsafe_allow_html=True)
        
        company = st.text_input("Company Name", "Example Corp")
        ticker = st.text_input("Ticker Symbol", "EXPL")
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "CNY", "INR",  "KRW", "IDR"])
        
        price = st.number_input("Current Stock Price", 0.01, value=100.00, format="%.2f")
        shares = st.number_input("Shares Outstanding (millions)", 0.1, value=100.00, format="%.2f")
        
        if st.button("Fetch Beta", use_container_width=True):
            with st.spinner("Fetching..."):
                beta, err, mkt_info = fetch_stock_beta(ticker)
                if beta:
                    st.session_state.fetched_beta = beta
                    st.session_state.mp_calc = mkt_info['market_premium']
                    st.success(f"Beta: {beta:.3f}")
                else:
                    st.error(err or "Unable to fetch beta")
        
        beta = st.number_input("Beta Coefficient", 0.1, 3.0, st.session_state.get('fetched_beta', 1.0), 0.01, format="%.3f")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Financial Structure
        st.markdown('<div class="input-section"><div style="font-size:1.3rem;font-weight:500;color:#c584f7">Financial Structure</div>', unsafe_allow_html=True)
        
        debt = st.number_input("Total Debt (millions)", 0.0, value=200.0, format="%.1f")
        cash = st.number_input("Cash & Equivalents (millions)", 0.0, value=50.0, format="%.1f")
        
        net_debt = debt - cash
        d2e = debt / (price * shares) if price * shares > 0 else 0
        
        cod = st.number_input("Cost of Debt", 0.0, 0.15, 0.04, 0.005, format="%.3f")
        tax = st.number_input("Effective Tax Rate", 0.0, 0.50, 0.25, 0.01, format="%.3f")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Historical Financials
        st.markdown('<div class="input-section"><div style="font-size:1.3rem;font-weight:500;color:#c584f7">Historical Financials</div>', unsafe_allow_html=True)
        
        years = st.slider("Years of historical data", 3, 5, 5)
        curr_yr = datetime.now().year
        
        # Revenue & FCF
        revs, fcfs = [], []
        
        st.markdown("**Revenue (millions)**")
        rev_cols = st.columns(years)
        for i, col in enumerate(rev_cols):
            yr = curr_yr - i
            revs.append(col.number_input(f"{yr}", -100100000000000.0, value=1000000000.0*(1.05**(years-i-1)), format="%.1f", key=f"r{yr}"))
        
        st.markdown("**Free Cash Flow (millions)**")
        fcf_cols = st.columns(years)
        for i, col in enumerate(fcf_cols):
            yr = curr_yr - i
            # Allow larger negative values for companies with losses
            fcfs.append(col.number_input(f"{yr}", -1000000000.0, 1000000000.0, value=100.0*(1.05**(years-i-1)), format="%.1f", key=f"f{yr}"))
        
        revs.reverse()
        fcfs.reverse()
        
        # Metrics
        rev_g = growth_stats(revs)
        fcf_g = growth_stats(fcfs)
        fcf_margin = np.mean([f/r for f,r in zip(fcfs, revs) if r > 0])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display metrics
        st.markdown('<div class="input-section"><div style="font-size:1.3rem;font-weight:500;color:#c584f7">Calculated Metrics</div>', unsafe_allow_html=True)
        
        # Quick WACC calc
        ce = rf + beta * mp
        we = 1 / (1 + d2e)
        wacc = we * ce + (1 - we) * cod * (1 - tax)
        
        cols = st.columns(4)
        cols[0].markdown(metric_card("Avg Revenue Growth", fmt_pct(rev_g['mean']), ('neutral', f"σ: {fmt_pct(rev_g['std'])}")), unsafe_allow_html=True)
        cols[1].markdown(metric_card("Avg FCF Growth", fmt_pct(fcf_g['mean']), ('neutral', f"σ: {fmt_pct(fcf_g['std'])}")), unsafe_allow_html=True)
        cols[2].markdown(metric_card("Avg FCF Margin", fmt_pct(fcf_margin)), unsafe_allow_html=True)
        cols[3].markdown(metric_card("WACC", fmt_pct(wacc)), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Growth assumptions
        st.markdown('<div class="input-section"><div style="font-size:1.3rem;font-weight:500;color:#c584f7">Growth Assumptions</div>', unsafe_allow_html=True)
        
        use_range = st.checkbox("Use growth rate ranges", True)
        
        proj_growth = []
        base_g = rev_g['mean']
        
        if use_range:
            st.markdown("**Projected Growth Rate Ranges**")
            for i in range(n_years):
                c1, c2, c3 = st.columns([2, 2, 2])
                center = max(base_g * (0.9**i), 0.02)
                with c1: st.markdown(f"**Year {i+1}**")
                with c2: min_g = st.number_input("Min", -0.5, 1.0, max(center-0.05, -0.1), 0.01, format="%.3f", key=f"ming{i}")
                with c3: max_g = st.number_input("Max", -0.5, 1.0, min(center+0.05, 0.3), 0.01, format="%.3f", key=f"maxg{i}")
                proj_growth.append((min(min_g, max_g), max(min_g, max_g)))
        else:
            st.markdown("**Projected Growth Rates**")
            g_cols = st.columns(n_years)
            for i, col in enumerate(g_cols):
                g = col.number_input(f"Year {i+1}", -0.5, 1.0, max(base_g*(0.9**i), 0.02), 0.01, format="%.3f", key=f"g{i}")
                proj_growth.append(g)
        
        # Terminal value
        st.markdown("**Terminal Value**")
        if use_range:
            c1, c2 = st.columns(2)
            with c1: tg_min = st.number_input("Min Terminal", 0.0, 0.04, 0.02, 0.005, format="%.3f")
            with c2: tg_max = st.number_input("Max Terminal", 0.0, 0.05, 0.03, 0.005, format="%.3f")
            term_growth = (tg_min, tg_max)
        else:
            term_growth = st.number_input("Terminal Growth", 0.0, 0.05, 0.025, 0.005, format="%.3f")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Run valuation
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Run DCF Valuation", type="primary", use_container_width=True):
        if price <= 0 or shares <= 0:
            st.error("Price and shares must be positive")
            return
        
        params = {
            'base_fcf': fcfs[-1] * 1e6,
            'growth_rates': proj_growth,
            'terminal_growth': term_growth,
            'beta': beta,
            'debt_to_equity': d2e,
            'cost_of_debt': cod,
            'tax_rate': tax,
            'net_debt': net_debt * 1e6,
            'shares_outstanding': shares * 1e6
        }
        
        unc = {'fcf_growth_std': max(fcf_g['std'], 0.03), 'terminal_growth_std': 0.005, 'beta_std': 0.1}
        
        with st.spinner(f"Running {n_sims:,} simulations..."):
            dcf = DCFEngine(rf, mp)
            results = dcf.monte_carlo(params, n_sims, unc)
            
            st.session_state.valuation_results = {
                'results': results, 'current_price': price, 'currency': currency,
                'company_name': company, 'parameters': params
            }
    
    # Display results
    if st.session_state.valuation_results:
        data = st.session_state.valuation_results
        res = data['results']
        price = data['current_price']
        curr = data['currency']
        company = data['company_name']
        
        st.markdown(f"## Valuation Results for {company}")
        
        # Summary
        display_summary(res, price, curr)
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["Distribution", "Scenarios", "Sensitivity"])
        
        with tab1:
            st.plotly_chart(plot_distribution(res['per_share_values'], price, curr), use_container_width=True)
            st.plotly_chart(plot_percentiles(res, price, curr), use_container_width=True)
        
        with tab2:
            scen = {'bear': res['percentiles']['p10'], 'base': res['percentiles']['p50'],
                   'bull': res['percentiles']['p90'], 'expected': res['mean']}
            
            st.plotly_chart(plot_waterfall(price, scen, curr), use_container_width=True)
            
            # Scenario table
            st.markdown("#### Scenario Summary")
            scen_df = pd.DataFrame([
                {'Scenario': name, 'Fair Value': fmt_curr(scen[key], curr),
                 'Upside/Downside': fmt_pct(scen[key]/price - 1)}
                for name, key in [('Bear (P10)', 'bear'), ('Base (P50)', 'base'),
                                 ('Bull (P90)', 'bull'), ('Expected (Mean)', 'expected')]
            ])
            st.dataframe(scen_df, use_container_width=True, hide_index=True)
        
        with tab3:
            st.plotly_chart(plot_sensitivity(res, data['parameters']), use_container_width=True)
            
            # Insight
            up_prob = (res['per_share_values'] > price).mean() * 100
            insight = ("Strong buy" if up_prob > 70 else "Moderate buy" if up_prob > 50 else 
                      "Fairly valued" if up_prob > 30 else "Potentially overvalued")
            
            st.markdown(summary_box("Key Insight",
                f"<strong>{up_prob:.0f}%</strong> probability of upside. {insight}."), 
                unsafe_allow_html=True)
        
        # Export
        st.markdown("### Export Results")
        
        export = {
            'summary': {'company': company, 'current_price': price, 
                       'mean_fair_value': res['mean'], 'upside_probability': f"{up_prob:.1f}%"},
            'percentiles': res['percentiles'],
            'statistics': {'std': res['std'], 'skew': res['skew'], 'kurtosis': res['kurtosis']}
        }
        
        st.download_button("Download Results (JSON)", json.dumps(export, indent=2),
                          f"{company}_DCF_{datetime.now().strftime('%Y%m%d')}.json", "application/json")

if __name__ == "__main__":
    main()