"""
Ultra-Optimized DCF Engine
"""

import numpy as np
from scipy import stats

class DCFEngine:
    """Streamlined DCF valuation engine"""
    
    def __init__(self, rf: float = 0.045, mp: float = 0.065):
        self.rf = max(0, rf)  # Ensure positive
        self.mp = max(0, mp)  # Ensure positive
    
    def calculate_value(self, p: dict) -> dict:
        """Single DCF calculation with inline WACC"""
        try:
            # Validate inputs
            if p['beta'] <= 0:
                p['beta'] = 0.1
                
            # WACC calc with validation
            ce = self.rf + p['beta'] * self.mp
            we = 1 / (1 + max(0, p['debt_to_equity']))  # Prevent negative
            wacc = we * ce + (1 - we) * max(0, p['cost_of_debt']) * (1 - max(0, min(1, p['tax_rate'])))
            
            # Ensure wacc is positive
            wacc = max(0.01, wacc)
            
            # Cash flows with validation
            fcf = []
            current_fcf = p['base_fcf']
            
            for g in p['growth_rates']:
                # Handle range inputs
                if isinstance(g, (tuple, list)):
                    g = np.mean(g)  # Use midpoint for base calculation
                current_fcf *= (1 + g)
                fcf.append(current_fcf)
            
            # Terminal value with better handling
            term_g = p['terminal_growth']
            if isinstance(term_g, (tuple, list)):
                term_g = np.mean(term_g)
                
            # Ensure terminal growth is less than WACC
            term_g = min(term_g, wacc - 0.001)
            
            if wacc > term_g + 0.001:
                tv = fcf[-1] * (1 + term_g) / (wacc - term_g)
            else:
                # Use exit multiple approach as fallback
                tv = fcf[-1] * 15
            
            # Present value calculations
            pv_fcf = sum(f / (1 + wacc)**(i+1) for i, f in enumerate(fcf) if f > 0)
            pv_tv = tv / (1 + wacc)**len(fcf) if tv > 0 else 0
            
            # Ensure positive enterprise value
            ev = max(0, pv_fcf + pv_tv)
            
            return {
                'enterprise_value': ev,
                'wacc': wacc,
                'terminal_value': tv,
                'fcf_projections': fcf
            }
        except Exception as e:
            # Return safe defaults on error
            return {
                'enterprise_value': 0,
                'wacc': 0.1,
                'terminal_value': 0,
                'fcf_projections': []
            }
    
    def monte_carlo(self, base: dict, n: int = 10000, unc: dict = None) -> dict:
        """Streamlined Monte Carlo with better error handling"""
        np.random.seed(42)
        u = unc or {'fcf_growth_std': 0.03, 'terminal_growth_std': 0.005, 'beta_std': 0.1}
        
        # Validate n
        n = max(100, min(100000, n))
        
        # Check range inputs
        g_range = isinstance(base['growth_rates'][0], (tuple, list))
        t_range = isinstance(base['terminal_growth'], (tuple, list))
        
        # Generate all random params at once
        betas = np.clip(np.random.normal(base['beta'], u['beta_std'], n), 0.3, 2.5)
        
        if g_range:
            growths = np.array([[np.random.uniform(max(-0.3, g[0]), min(0.5, g[1])) 
                                for g in base['growth_rates']] for _ in range(n)])
        else:
            growths = np.clip(np.random.normal(base['growth_rates'], u['fcf_growth_std'], 
                                              (n, len(base['growth_rates']))), -0.3, 0.5)
        
        if t_range:
            term_g = np.random.uniform(max(0, base['terminal_growth'][0]), 
                                     min(0.04, base['terminal_growth'][1]), n)
        else:
            term_g = np.clip(np.random.normal(base['terminal_growth'], 
                                             u['terminal_growth_std'], n), 0, 0.04)
        
        # Vectorized simulation with error handling
        evs = []
        for i in range(n):
            try:
                params = {**base, 'beta': betas[i], 'growth_rates': growths[i], 
                         'terminal_growth': term_g[i]}
                ev = self.calculate_value(params)['enterprise_value']
                if ev > 0 and not np.isnan(ev) and not np.isinf(ev):
                    evs.append(ev)
            except:
                continue
        
        # Ensure we have enough valid results
        if len(evs) < 100:
            # Fallback to simple calculation
            base_result = self.calculate_value(base)
            evs = [base_result['enterprise_value']] * 100
        
        # Results calculation with validation
        evs = np.array(evs)
        net_debt = max(0, base.get('net_debt', 0))
        shares = max(1, base.get('shares_outstanding', 1))
        
        eq_vals = np.maximum(evs - net_debt, 0)
        ps_vals = eq_vals / shares
        
        # Remove extreme outliers
        q1, q3 = np.percentile(ps_vals, [25, 75])
        iqr = q3 - q1
        mask = (ps_vals >= q1 - 3*iqr) & (ps_vals <= q3 + 3*iqr)
        ps_vals_clean = ps_vals[mask] if mask.any() else ps_vals
        
        pctls = [5, 10, 25, 50, 75, 90, 95]
        
        return {
            'per_share_values': ps_vals_clean,
            'mean': ps_vals_clean.mean(),
            'median': np.median(ps_vals_clean),
            'std': ps_vals_clean.std(),
            'skew': stats.skew(ps_vals_clean) if len(ps_vals_clean) > 3 else 0,
            'kurtosis': stats.kurtosis(ps_vals_clean) if len(ps_vals_clean) > 3 else 0,
            'percentiles': {f'p{p}': np.percentile(ps_vals_clean, p) for p in pctls},
            'n_simulations': len(ps_vals_clean)
        }