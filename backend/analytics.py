import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    'user_id',
    'status',            # expected values: active|churned|inactive
    'converted',         # 0/1 or True/False
    'session_duration',  # minutes (float)
    'sessions_count',
    'signup_date',
]

NUMERIC_COLUMNS = ['converted', 'session_duration', 'sessions_count', 'revenue']

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean incoming user dataset so downstream metrics don't fail.
    - Ensures required columns exist (create with sensible defaults when missing)
    - Coerces dtypes (numeric columns to numeric, signup_date to datetime)
    - Normalizes status values to {'active','churned','inactive'}
    - Drops exact-duplicate rows by user_id + signup_date
    - Handles impossible values (negative durations/sessions)
    """
    df = df.copy()

    # Ensure required columns
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            if col == 'user_id':
                df[col] = np.arange(1, len(df) + 1)
            elif col == 'status':
                df[col] = 'active'
            elif col == 'converted':
                df[col] = 0
            elif col == 'session_duration':
                df[col] = 0.0
            elif col == 'sessions_count':
                df[col] = 0
            elif col == 'signup_date':
                df[col] = pd.Timestamp('today').normalize()

    # Normalize dirty tokens to NaN (vectorized)
    import re
    dirty_pattern = re.compile(r"^\s*(?:|nan|na|none|\?|-|n/a|###|ok|fail|error|check)\s*$", re.IGNORECASE)
    df = df.replace(dirty_pattern, np.nan, regex=True)

    # Robust numeric coercion helper
    def coerce_numeric(series: pd.Series) -> pd.Series:
        # remove thousands separators and quotes; keep leading minus and digits/decimal
        s = series.astype(str).str.replace(',', '', regex=False).str.replace('"', '', regex=False)
        # strip non-numeric except leading - and dot
        s = s.str.extract(r'\s*([-+]?[0-9]*\.?[0-9]+)')[0]
        out = pd.to_numeric(s, errors='coerce')
        return out

    # Coerce numeric for known numeric columns
    for col in [c for c in NUMERIC_COLUMNS if c in df.columns]:
        df[col] = coerce_numeric(df[col])

    # Negative protections
    if 'session_duration' in df.columns:
        df['session_duration'] = df['session_duration'].clip(lower=0)
    if 'sessions_count' in df.columns:
        df['sessions_count'] = df['sessions_count'].clip(lower=0)
    if 'revenue' in df.columns:
        df['revenue'] = df['revenue'].clip(lower=0)

    # Converted to 0/1
    df['converted'] = df['converted'].fillna(0).astype(float).clip(0, 1)

    # Parse signup_date if present, otherwise try to parse 'date' (aggregate schema)
    if 'signup_date' in df.columns:
        df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
        df['signup_date'] = df['signup_date'].ffill().bfill()
        df['signup_date'] = df['signup_date'].fillna(pd.Timestamp('today').normalize())
    if 'date' in df.columns:
        parsed = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
        # Try alternate parsing for US-style where first attempt failed
        mask_bad = parsed.isna()
        if mask_bad.any():
            parsed2 = pd.to_datetime(df.loc[mask_bad, 'date'], errors='coerce', dayfirst=False)
            parsed.loc[mask_bad] = parsed2
        df['date'] = parsed
        df['date'] = df['date'].ffill().bfill()

    # If aggregate-style columns exist, coerce them to numeric and sanitize
    MAX_USERS = 10_000_000
    for col in ['total_users', 'active_users', 'churned_users', 'new_users']:
        if col in df.columns:
            df[col] = coerce_numeric(df[col])
            df[col] = df[col].fillna(0)
            # Clip to sensible ranges
            df[col] = df[col].clip(lower=0, upper=MAX_USERS)

    # Extra aggregate-schema cleanup and derivations
    if ('date' in df.columns) and ('total_users' in df.columns):
        # Keep only rows with a valid date
        df = df[~df['date'].isna()].copy()
        df = df.sort_values('date')

        total = pd.to_numeric(df.get('total_users', 0), errors='coerce').fillna(0).clip(lower=0, upper=MAX_USERS)
        active = pd.to_numeric(df.get('active_users', np.nan), errors='coerce')
        churn = pd.to_numeric(df.get('churned_users', np.nan), errors='coerce')

        # Derive missing using identities
        active = active.where(~active.isna(), total - churn.where(~churn.isna(), 0))
        churn = churn.where(~churn.isna(), total - active.where(~active.isna(), 0))

        # Bound
        active = active.fillna(0).clip(lower=0)
        churn = churn.fillna(0).clip(lower=0)
        # Ensure active + churn <= total by reducing churn first
        over = (active + churn) - total
        mask_over = over > 0
        if mask_over.any():
            reduce_amt = over[mask_over]
            churn_adj = (churn[mask_over] - reduce_amt).clip(lower=0)
            remaining_over = (active[mask_over] + churn_adj) - total[mask_over]
            active_adj = (active[mask_over] - remaining_over.clip(lower=0)).clip(lower=0)
            churn.loc[mask_over] = churn_adj
            active.loc[mask_over] = active_adj

        # Clean new_users using positive diffs of total where missing or inconsistent
        provided_new = pd.to_numeric(df.get('new_users', np.nan), errors='coerce')
        diffs = total.diff().fillna(0).clip(lower=0)
        new_clean = provided_new.where(~provided_new.isna(), diffs)
        inconsistent = (new_clean > (diffs * 3)) & (diffs > 0)
        new_clean = new_clean.where(~inconsistent, diffs)
        new_clean = new_clean.fillna(0).clip(lower=0, upper=MAX_USERS)

        # Write back (integers)
        df['total_users'] = total.round().astype(int)
        df['active_users'] = active.round().astype(int)
        df['churned_users'] = churn.round().astype(int)
        df['new_users'] = new_clean.round().astype(int)

    # Normalize status
    def normalize_status(x):
        if pd.isna(x):
            return 'inactive'
        s = str(x).strip().lower()
        if s in {'active', 'activated', 'current'}:
            return 'active'
        if s in {'churned', 'cancelled', 'canceled', 'lost'}:
            return 'churned'
        return 'inactive'
    df['status'] = df['status'].map(normalize_status)

    # Drop duplicates
    subset = [c for c in ['user_id', 'signup_date'] if c in df.columns]
    if subset:
        df = df.drop_duplicates(subset=subset, keep='first')

    # Final NA handling
    df = df.fillna({
        'sessions_count': 0,
        'session_duration': 0.0,
        'converted': 0.0,
    })

    return df

def compute_metrics(df):
    """
    Compute key SaaS metrics from user data
    Returns dictionary of calculated metrics
    """
    results = {}

    # If the dataset is aggregate-style (no user_id but has date + totals), compute metrics accordingly
    if ('user_id' not in df.columns) and ('date' in df.columns) and ('total_users' in df.columns):
        # Ensure clean types
        total_users_series = pd.to_numeric(df['total_users'], errors='coerce').fillna(0)
        active_series = pd.to_numeric(df['active_users'], errors='coerce').fillna(0) if 'active_users' in df.columns else pd.Series([0]*len(df))
        churned_series = pd.to_numeric(df['churned_users'], errors='coerce').fillna(0) if 'churned_users' in df.columns else pd.Series([0]*len(df))
        new_users_series = pd.to_numeric(df['new_users'], errors='coerce').fillna(0) if 'new_users' in df.columns else pd.Series([0]*len(df))

        # Sort by date and use last row as snapshot
        ordered = df.copy()
        ordered['__date'] = pd.to_datetime(df['date'], errors='coerce')
        ordered = ordered.sort_values('__date')
        if ordered.empty:
            return {
                'total_users': 0,
                'active_users': 0,
                'churned_users': 0,
                'conversion_rate': 0,
                'avg_session_duration': 0,
                'avg_sessions_per_user': 0,
                'cohort_analysis': {}
            }

        # Forward-fill numeric series to stabilize latest values
        for c in ['total_users','active_users','churned_users','new_users']:
            if c in ordered.columns:
                ordered[c] = pd.to_numeric(ordered[c], errors='coerce').ffill()

        # Pick last row with a valid total_users > 0
        valid_mask = pd.to_numeric(ordered['total_users'], errors='coerce').fillna(0) > 0
        if valid_mask.any():
            last = ordered.loc[valid_mask].iloc[-1]
        else:
            last = ordered.iloc[-1]

        total_latest = pd.to_numeric(last.get('total_users'), errors='coerce')
        active_latest = pd.to_numeric(last.get('active_users'), errors='coerce')
        churn_latest = pd.to_numeric(last.get('churned_users'), errors='coerce')

        # Derive missing values where possible
        if pd.isna(active_latest) and not pd.isna(total_latest) and not pd.isna(churn_latest):
            active_latest = max(float(total_latest) - float(churn_latest), 0)
        if pd.isna(churn_latest) and not pd.isna(total_latest) and not pd.isna(active_latest):
            churn_latest = max(float(total_latest) - float(active_latest), 0)
        if pd.isna(total_latest):
            total_latest = 0.0
        if pd.isna(active_latest):
            active_latest = 0.0
        if pd.isna(churn_latest):
            churn_latest = 0.0

        # Bound values
        total_latest = max(total_latest, 0)
        active_latest = min(max(active_latest, 0), total_latest)
        churn_latest = min(max(churn_latest, 0), total_latest)

        results['total_users'] = int(total_latest)
        results['active_users'] = int(active_latest)
        results['churned_users'] = int(churn_latest)

        # Approximate conversion_rate as active / total when available
        conv = float(results['active_users'] / results['total_users']) if results['total_users'] else 0.0
        results['conversion_rate'] = max(0.0, min(conv, 1.0))
        results['avg_session_duration'] = 0.0
        results['avg_sessions_per_user'] = 0.0

        # Cohort by month from 'date' using new_users (or diffs of total_users if new_users missing)
        dates = pd.to_datetime(ordered['date'], errors='coerce')
        df_dates = ordered.copy()
        df_dates['signup_month'] = dates.dt.to_period('M')
        if 'new_users' in df.columns:
            cohort_series = pd.to_numeric(df_dates['new_users'], errors='coerce').fillna(0)
            cohort_series = df_dates.groupby('signup_month')['new_users'].sum()
        else:
            # Approximate new users using positive diffs of total_users
            totals_ordered = pd.to_numeric(ordered['total_users'], errors='coerce').fillna(0)
            diffs = totals_ordered.diff().clip(lower=0).fillna(0)
            df_dates['_diff'] = diffs
            cohort_series = df_dates.groupby('signup_month')['_diff'].sum()
        results['cohort_analysis'] = {str(k): int(v) for k, v in cohort_series.to_dict().items()}

        # Optionally revenue metrics if provided
        if 'revenue' in df.columns:
            rev = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)
            results['avg_revenue_per_user'] = float(rev.mean())
            results['total_revenue'] = float(rev.sum())

        return results
    
    # Basic metrics
    results['total_users'] = len(df)
    results['active_users'] = df[df['status'] == 'active'].shape[0]
    results['churned_users'] = df[df['status'] == 'churned'].shape[0]
    
    # Conversion rates
    results['conversion_rate'] = df['converted'].mean()
    
    # Engagement metrics
    results['avg_session_duration'] = df['session_duration'].mean()
    results['avg_sessions_per_user'] = df['sessions_count'].mean()
    
    # Revenue metrics (if available)
    if 'revenue' in df.columns:
        results['avg_revenue_per_user'] = df['revenue'].mean()
        results['total_revenue'] = df['revenue'].sum()
    
    # Cohort analysis
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df['signup_month'] = df['signup_date'].dt.to_period('M')
    cohort_data = df.groupby('signup_month')['user_id'].nunique()
    
    # Convert cohort_data to a dictionary and ensure keys are strings
    if isinstance(cohort_data, pd.Series):
        cohort_dict = cohort_data.to_dict()
    else:
        # If it's a scalar, create a dictionary with one key-value pair
        cohort_dict = {df['signup_month'].iloc[0]: cohort_data}
    
    # Convert all keys to strings
    results['cohort_analysis'] = {str(k): v for k, v in cohort_dict.items()}
    
    return results
