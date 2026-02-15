import pandas as pd
import unicodedata

# Project Configuration
PROJECT_NAME = "Bangladesh_Election_Analysis_2026"

def get_economic_df():
    """Returns the standardized HIES 2022 Economic Data by Division."""
    econ_data = {
        'Division': ['Dhaka', 'Chattogram', 'Rajshahi', 'Khulna', 'Barishal', 'Mymensingh', 'Sylhet', 'Rangpur'],
        'Monthly_Income': [42696, 34054, 30398, 28192, 25892, 24183, 22861, 21674],
        'Expenditure': [37935, 34843, 25358, 26135, 23940, 24554, 30402, 21667]
    }
    return pd.DataFrame(econ_data)

def map_alliance(p):
    """Maps raw party names to their respective political alliances."""
    if pd.isna(p): return 'Others'
    p = unicodedata.normalize('NFKC', str(p)).strip()
    
    # 1. BNP Alliance (BNP-A)
    bnp_a_keywords = [
        'বাংলাদেশ জাতীয়তাবাদী দল', 'বিএনপি', 'BNP', 'গণঅধিকার পরিষদ', 'জিওপি', 
        'National People\'s Party', 'এনপিপি', 'গণসংহতি আন্দোলন', 
        'Nationalist Democratic Movement', 'এনডিএম', 'বিপ্লবী ওয়ার্কার্স পার্টি', 'RWP',
        'বাংলাদেশ জাতীয় পার্টি', 'বিজেপি', 'জমিয়তে উলামায়ে ইসলাম', 'JUIB'
    ]
    if any(k in p for k in bnp_a_keywords): return 'BNP-A'

    # 2. 11 Party Alliance (11PA)
    jamaat_11pa_keywords = [
        'বাংলাদেশ জামায়াতে ইসলামী', 'Jamaat', 'বাংলাদেশ খেলাফত মজলিস', 'জাতীয় নাগরিক পার্টি', 
        'এনসিপি', 'এবি পার্টি', 'আমার বাংলাদেশ পার্টি', 'খেলাফত মজলিস', 
        'বাংলাদেশ লেবার পার্টি', 'বাংলাদেশ খেলাফত আন্দোলন', 'লিবারেল ডেমোক্রেটিক পার্টি', 'এলডিপি', 
        'নেজামে ইসলাম', 'বাংলাদেশ ডেভেলপমেন্ট পার্টি', 'জাতীয় গণতান্ত্রিক পার্টি', 'জাগপা'
    ]
    if any(k in p for k in jamaat_11pa_keywords): return '11PA'

    # 3. National Democratic Front (NDF)
    ndf_keywords = [
        'জাতীয় পার্টি', 'Jatiya Party', 'সাংস্কৃতিক মুক্তিজোট', 'Muktijote', 'মুসলিম লীগ', 'Muslim League'
    ]
    if any(k in p for k in ndf_keywords): return 'NDF'

    # 4. Democratic United Front (DUF)
    duf_keywords = [
        'কমিউনিস্ট পার্টি', 'CPB', 'সমাজতান্ত্রিক দল', 'বাসদ', 'BASAD', 'মার্কসবাদী', 
        'জাতীয় সমাজতান্ত্রিক দল', 'গণ ফ্রন্ট', 'গণফ্রন্ট'
    ]
    if any(k in p for k in duf_keywords): return 'DUF'

    # 5. Greater Sunni Alliance (GSA)
    gsa_keywords = [
        'বাংলাদেশ ইসলামী ফ্রন্ট', 'সুপ্রীম পার্টি', 'BSP', 'ইসলামিক ফ্রন্ট বাংলাদেশ'
    ]
    if any(k in p for k in gsa_keywords): return 'GSA'

    # 6. Islami Andolan Bangladesh (IAB)
    if 'ইসলামী আন্দোলন' in p: return 'IAB'

    # 7. Independent (IND)
    if 'স্বতন্ত্র' in p: return 'IND'

    return 'Others'