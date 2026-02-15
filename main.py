import os
import pandas as pd
from src import (
    run_decision_tree_analysis, 
    generate_charts, 
    clean_and_process, 
    run_scraper,
    run_weighted_analysis,
    generate_weighted_impact_chart 
)

def main():
    print("🇧🇩 Starting Bangladesh Election 2026 Analysis Pipeline...")
    
    # Use absolute paths to handle directory structures correctly
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_path = os.path.normpath(os.path.join(base_dir, 'data', 'raw_election_data.csv'))
    processed_seat_path = os.path.normpath(os.path.join(base_dir, 'data', 'seat_wise_votes.csv'))
    div_analysis_path = os.path.normpath(os.path.join(base_dir, 'data', 'division_analysis.csv'))
    images_dir = os.path.normpath(os.path.join(base_dir, 'images'))
    
    # Ensure necessary directories exist
    os.makedirs(os.path.join(base_dir, 'data'), exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    # 1. Ensure Raw Data exists
    if not os.path.exists(raw_data_path):
        if not os.path.exists(processed_seat_path):
            print(f"Raw data not found at {raw_data_path}. Scraping data...")
            run_scraper()
        else:
            print(f"✅ Processed data exists, skipping scraper.")
    else:
        print(f"✅ Raw data found at {raw_data_path}. Skipping scraper.")

    # 2. Process Seat-wise Votes
    if not os.path.exists(processed_seat_path):
        print("Generating processed seat-wise votes...")
        df_seats = clean_and_process(raw_data_path) 
        if df_seats is not None:
            df_seats.to_csv(processed_seat_path, index=False)
            print(f"✅ Created {processed_seat_path}")
    else:
        print(f"✅ Processed data found at {processed_seat_path}")

    # 3. Weighted Impact Analysis (New Phase)
    print("Running Weighted Impact Analysis...")
    run_weighted_analysis(processed_seat_path, div_analysis_path)
    
    # 4. Standard Analysis & Core Charts
    df = pd.read_csv(processed_seat_path)
    run_decision_tree_analysis(df)
    generate_charts(df, output_dir=images_dir)

    # 5. Specialized Weighted Impact Visualization
    print("Generating Weighted Impact Visualizations...")
    generate_weighted_impact_chart(div_analysis_path, output_dir=images_dir)

    print("\n🎉 Pipeline Complete! Check 'images/' and 'data/' folders.")

if __name__ == "__main__":
    main()