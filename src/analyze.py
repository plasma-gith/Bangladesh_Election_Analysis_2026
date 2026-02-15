import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from .config import get_economic_df

def run_decision_tree_analysis(df):
    """Performs Decision Tree analysis to find economic correlation."""
    print("\n--- Running Decision Tree Analysis ---")
    
    df_econ = get_economic_df()
    df_model = pd.merge(df, df_econ, on='Division', how='left')
    
    if 'Winner_Alliance' not in df_model.columns:
        print("Winner_Alliance column missing. Skipping Decision Tree.")
        return

    # Filter for the main battle: BNP-A vs 11PA
    binary_df = df_model[df_model['Winner_Alliance'].isin(['BNP-A', '11PA'])]
    
    if binary_df.empty:
        print("Not enough data for binary classification.")
        return

    X = binary_df[['Monthly_Income', 'Expenditure']]
    y = binary_df['Winner_Alliance']
    
    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X, y)
    
    print("Decision Rules (How the winner is decided):")
    print(export_text(clf, feature_names=['Income', 'Expenditure']))
    print(f"Feature Importance (Income, Expenditure): {clf.feature_importances_}")