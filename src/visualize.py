import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from .config import get_economic_df

def generate_charts(df, output_dir):
    """Generates and saves five improved election visualization charts."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Standardize economic data and division names
    df_econ = get_economic_df()
    df_merged = pd.merge(df, df_econ, on='Division', how='left')
    sns.set_style("whitegrid")
    
    # --- PLOT 1: Improved Seat Share Pie Chart (Donut) ---
    if 'Winner_Alliance' in df.columns:
        winner_counts = df['Winner_Alliance'].value_counts()
        plt.figure(figsize=(10, 8))
        plt.pie(winner_counts, labels=winner_counts.index, autopct='%1.1f%%', startangle=140, 
                colors=sns.color_palette('pastel'), pctdistance=0.85, 
                explode=[0.05]*len(winner_counts), textprops={'fontsize': 12})
        plt.gcf().gca().add_artist(plt.Circle((0,0),0.70,fc='white'))
        plt.title('2026 Election Seat Share by Alliance', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'Seat_Share_Pie_Chart_Improved.png'), dpi=300)
        plt.close()

    # --- PLOT 2: Improved Division-wise Stacked Bar Chart ---
    if 'Winner_Alliance' in df.columns:
        div_counts = df.groupby(['Division', 'Winner_Alliance']).size().unstack(fill_value=0)
        ax = div_counts.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='viridis', width=0.8)
        plt.title('Division-wise Seat Wins by Alliance', fontsize=16, fontweight='bold')
        plt.ylabel('Number of Seats')
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Alliance', bbox_to_anchor=(1.02, 1), loc='upper left')
        # Annotate bars
        for c in ax.containers:
            labels = [int(v) if v > 0 else "" for v in c.datavalues]
            ax.bar_label(c, labels=labels, label_type='center', fontsize=10, color='white', fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'Division_Seat_Wins_Bar_Chart_Improved.png'), dpi=300)
        plt.close()

    # Define alliances for vote share calculation
    alliance_cols = ['BNP-A', '11PA', 'DUF', 'GSA', 'IAB', 'IND', 'NDF', 'Others']
    existing_cols = [c for c in alliance_cols if c in df.columns]
    df_merged['Total_Votes_Seat'] = df_merged[existing_cols].sum(axis=1)

    # --- PLOT 3: Improved Scatter Plot (Income vs BNP-A Vote Share) ---
    if 'BNP-A' in df.columns:
        df_merged['BNP_Vote_Share'] = (df_merged['BNP-A'] / df_merged['Total_Votes_Seat']) * 100
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=df_merged, x='Monthly_Income', y='BNP_Vote_Share', hue='Division', 
                        style='Division', s=120, palette='deep', alpha=0.9, edgecolor='black')
        plt.title('Monthly Income vs BNP-A Vote Share', fontsize=16, fontweight='bold')
        plt.xlabel('Avg. Monthly Income of Division (BDT)')
        plt.ylabel('BNP-A Vote Share in Seat (%)')
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='Division')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'Income_vs_BNP_Vote_Share_Scatter_Improved.png'), dpi=300)
        plt.close()

    # --- PLOT 4: Improved Scatter Plot (Income vs Jamaat Vote Share) ---
    if '11PA' in df.columns:
        df_merged['Jamaat_Vote_Share'] = (df_merged['11PA'] / df_merged['Total_Votes_Seat']) * 100
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=df_merged, x='Monthly_Income', y='Jamaat_Vote_Share', hue='Division', 
                        style='Division', s=120, palette='deep', alpha=0.9, edgecolor='black')
        plt.title('Monthly Income vs Jamaat Alliance (11PA) Vote Share', fontsize=16, fontweight='bold')
        plt.xlabel('Avg. Monthly Income of Division (BDT)')
        plt.ylabel('Jamaat Alliance Vote Share in Seat (%)')
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='Division')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'Income_vs_Jamaat_Vote_Share_Scatter_Improved.png'), dpi=300)
        plt.close()

    # --- PLOT 5: Improved Box Plot (Expenditure Decision) ---
    if 'Winner_Alliance' in df.columns and 'BNP-A' in df.columns and '11PA' in df.columns:
        main_alliances = df_merged[df_merged['Winner_Alliance'].isin(['BNP-A', '11PA'])]
        if not main_alliances.empty:
            plt.figure(figsize=(10, 6))
            sns.boxplot(data=main_alliances, x='Winner_Alliance', y='Expenditure', palette='Set2', width=0.5, linewidth=2)
            sns.swarmplot(data=main_alliances, x='Winner_Alliance', y='Expenditure', color='black', alpha=0.5, size=4)
            plt.title('Expenditure Decision Boundary by Winning Alliance', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'Expenditure_vs_Winner_Boxplot_Improved.png'), dpi=300)
            plt.close()

    print(f"✅ All 5 improved visualizations saved to {output_dir}")
    
def generate_weighted_impact_chart(analysis_file, output_dir='images'):
    """Creates a comparison between Raw Vote Share and Weighted National Impact."""
    if not os.path.exists(analysis_file):
        return

    df = pd.read_csv(analysis_file)
    os.makedirs(output_dir, exist_ok=True)

    # We will visualize the two main alliances
    alliances = ['BNP-A', '11PA']
    
    for alliance in alliances:
        if alliance not in df.columns or f'Weighted_{alliance}' not in df.columns:
            continue

        plt.figure(figsize=(12, 6))
        
        # Prepare data for plotting
        plot_df = df[['Division', alliance, f'Weighted_{alliance}']].copy()
        plot_df = plot_df.melt(id_vars='Division', var_name='Metric', value_name='Percentage')
        
        # Rename metrics for better legends
        plot_df['Metric'] = plot_df['Metric'].replace({
            alliance: 'Raw Vote Share (%)',
            f'Weighted_{alliance}': 'Weighted National Impact (%)'
        })

        sns.barplot(data=plot_df, x='Division', y='Percentage', hue='Metric', palette='viridis')
        
        plt.title(f'{alliance}: Raw Performance vs. Weighted National Impact (2026)')
        plt.ylabel('Percentage / Impact Score')
        plt.xlabel('Division (Sorted by Monthly Income)')
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(output_dir, f'weighted_impact_{alliance.lower()}.png')
        plt.savefig(save_path)
        plt.close()
        print(f"✅ Weighted impact chart saved: {save_path}")