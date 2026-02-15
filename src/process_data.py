import pandas as pd
from .config import map_alliance

def clean_and_process(file_path):
    """Processes raw candidate data into a seat-level summary."""
    df = pd.read_csv(file_path)
    
    def bn_to_en(s):
        """Converts Bengali numerals to English integers."""
        if pd.isna(s) or s == '': return 0
        translation = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
        return int(str(s).replace(',', '').translate(translation))

    df['Votes_Num'] = df['Votes'].apply(bn_to_en)
    df['Alliance'] = df['Party'].apply(map_alliance)
    pivot_df = df.pivot_table(
        index=['Seat_ID', 'Seat_Name', 'Division'],
        columns='Alliance',
        values='Votes_Num',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    return pivot_df