import sys
import subprocess
import time
import random
import os
import pandas as pd

def install(package):
    """Installs missing packages at runtime."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def run_scraper():
    """Wrapped scraper function to collect raw election data."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ Libraries found!")
    except ImportError:
        print("⚠️ Libraries missing. Installing them now...")
        install("selenium")
        install("webdriver-manager")
        install("pandas")
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager

    # Configuration
    BASE_URL = "https://election.somoynews.tv/seat/"
    TOTAL_SEATS = 300
    # Output path must match what main.py expects to avoid re-scraping
    OUTPUT_FILE = os.path.join("data", "raw_election_data.csv")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized") 
    # Uncomment next line for silent background scraping
    # options.add_argument("--headless") 

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    all_data = []

    print(f"🚀 Starting Selenium Scrape for {TOTAL_SEATS} seats...")

    try:
        for seat_id in range(1, TOTAL_SEATS + 1):
            url = f"{BASE_URL}{seat_id}"
            print(f"Opening Seat {seat_id}...", end=" ", flush=True)
            
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "text-subtitle-1-display"))
                )

                # 1. Extract Seat Name
                try:
                    header_element = driver.find_element(By.CSS_SELECTOR, "div.text-h5.px-0")
                    full_text = header_element.text
                    seat_name = full_text.split(',')[0].strip()
                except:
                    seat_name = f"Seat-{seat_id}"

                # 2. Extract Seat Statistics
                stats = {"Total_Voters": "0", "Total_Centers": "0", "Male_Voters": "0", "Female_Voters": "0"}
                stat_boxes = driver.find_elements(By.CLASS_NAME, "border-lightgray")
                for box in stat_boxes:
                    try:
                        label = box.find_element(By.CLASS_NAME, "text-subtitle-1").text.strip()
                        value = box.find_element(By.CSS_SELECTOR, ".text-green, .text-title-1").text.strip()
                        if "মোট ভোটার" in label: stats["Total_Voters"] = value
                        elif "মোট কেন্দ্র" in label: stats["Total_Centers"] = value
                        elif "পুরুষ ভোটার" in label: stats["Male_Voters"] = value
                        elif "নারী ভোটার" in label: stats["Female_Voters"] = value
                    except: continue

                # 3. Extract Candidate Cards
                cards = driver.find_elements(By.CLASS_NAME, "my-4")
                for card in cards:
                    try:
                        name = card.find_element(By.CLASS_NAME, "text-subtitle-1-display").text.strip()
                        p_tags = card.find_elements(By.TAG_NAME, "p")
                        party = symbol = votes = "Unknown"
                        for p in p_tags:
                            text = p.text
                            if "দল:" in text: party = text.replace("দল:", "").strip()
                            if "মার্কা:" in text: symbol = text.replace("মার্কা:", "").strip()
                            if "ভোট:" in text: votes = text.replace("ভোট:", "").replace("\n", "").strip()

                        all_data.append({
                            "Seat_ID": seat_id, "Seat_Name": seat_name,
                            **stats, "Candidate": name, "Party": party,
                            "Symbol": symbol, "Votes": votes
                        })
                    except: continue
                print(f"✅ {seat_id}: Success.")
            except Exception:
                print(f"⚠️  Skipping Seat {seat_id} (Loading issue)")
            
            time.sleep(random.uniform(0.5, 1.2))

    finally:
        driver.quit()
        if all_data:
            df = pd.DataFrame(all_data)
            
            # Translate Bengali numerals to Integers for calculation
            def bangla_to_int(s):
                if pd.isna(s): return 0
                s = str(s).replace(',', '')
                translation = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
                try: return int(s.translate(translation))
                except: return 0

            df['Votes_Numeric'] = df['Votes'].apply(bangla_to_int)
            # Identify winner based on highest vote count per seat
            winner_indices = df.groupby('Seat_ID')['Votes_Numeric'].idxmax()
            df['Status'] = 'পরাজিত' 
            df.loc[winner_indices, 'Status'] = 'বি বিজয়ী'
            df = df.drop(columns=['Votes_Numeric'])

            # Ensure 'data' directory exists
            os.makedirs("data", exist_ok=True)
            df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
            print(f"\n🎉 SUCCESS! Saved {len(df)} rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_scraper()