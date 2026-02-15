import pandas as pd
import os
from .config import get_economic_df

def run_weighted_analysis(input_path, output_path):
    """Calculates the weighted voter impact per division."""
    if not os.path.exists(input_path):
        return

    df_votes = pd.read_csv(input_path)
    df_econ = get_economic_df()

    # Define alliances for analysis
    alliance_cols = ['BNP-A', '11PA', 'DUF', 'GSA', 'IAB', 'IND', 'NDF', 'Others']
    available_cols = [c for c in alliance_cols if c in df_votes.columns]

    # Aggregate and calculate weights
    div_performance = df_votes.groupby('Division')[available_cols].sum()
    div_total_votes = div_performance.sum(axis=1)
    div_perf_pct = div_performance.div(div_total_votes, axis=0) * 100
    merged = pd.merge(div_perf_pct.reset_index(), df_econ, on='Division')

    total_national_votes = div_total_votes.sum()
    merged['Division_Total_Votes'] = merged['Division'].map(div_total_votes.to_dict())
    merged['Voter_Weight'] = merged['Division_Total_Votes'] / total_national_votes

    for alliance in ['BNP-A', '11PA']:
        if alliance in merged.columns:
            merged[f'Weighted_{alliance}'] = merged[alliance] * merged['Voter_Weight']

    merged = merged.sort_values(by='Monthly_Income', ascending=False)
    merged.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ Weighted analysis saved to: {output_path}")