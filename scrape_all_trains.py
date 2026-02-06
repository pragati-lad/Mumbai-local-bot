# ==================================================
# Mumbai Local Train - Complete Data Scraper
# ==================================================
# Scrapes REAL train data for AC and Non-AC trains
# Sources:
# - go4mumbai.com (Western Railway)
# - mumbailifeline.com (Central Railway)
# ==================================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def scrape_western_railway():
    """Scrape Western Railway trains from mumbailifeline.com and go4mumbai.com"""
    print("\n[Western Railway] Scraping from mumbailifeline.com...")

    all_trains = []

    # Scrape non-AC trains from mumbailifeline.com
    routes = [
        ("CHURCHGATE", "VIRAR", "DOWN"),
        ("VIRAR", "CHURCHGATE", "UP"),
        ("CHURCHGATE", "BORIVALI", "DOWN"),
        ("BORIVALI", "CHURCHGATE", "UP"),
    ]

    for src, dst, direction in routes:
        url = f"https://www.mumbailifeline.com/timetable.php?sel_route=western&sfrom={src}&sto={dst}&time1=04:00+AM&time2=11:59+PM&Submit=Submit"

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')

            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 10:
                    continue

                header = rows[0].find_all(['td', 'th'])
                header_text = [h.get_text(strip=True).lower() for h in header]

                if 'train' not in ' '.join(header_text) and 'speed' not in ' '.join(header_text):
                    continue

                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) < 6:
                        continue

                    train_no = cols[0].get_text(strip=True)
                    speed = cols[1].get_text(strip=True).upper()
                    origin = cols[3].get_text(strip=True)
                    dest_station = cols[4].get_text(strip=True)
                    time_str = cols[5].get_text(strip=True)

                    if 'train' in train_no.lower() or not time_str:
                        continue

                    is_ac = 'AC' in train_no.upper()
                    train_type = f"AC {speed}" if is_ac else speed

                    time_str = time_str.replace('\n', '').strip()

                    all_trains.append({
                        'line': 'WR',
                        'time': time_str,
                        'source': origin.title(),
                        'dest': dest_station.title(),
                        'type': train_type,
                        'is_ac': is_ac
                    })

            time.sleep(0.5)

        except Exception as e:
            print(f"[Western Railway] Error scraping {src} to {dst}: {e}")

    # Also scrape AC trains from go4mumbai.com
    print("[Western Railway] Adding AC trains from go4mumbai.com...")
    ac_url = "https://go4mumbai.com/ac-trains.php"

    try:
        response = requests.get(ac_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        tables = soup.find_all('table')

        for table_idx in [4, 5]:
            if table_idx >= len(tables):
                continue

            table = tables[table_idx]
            rows = table.find_all('tr')

            for row in rows:
                cols = row.find_all('td')
                col_texts = [c.get_text(strip=True) for c in cols]

                for i in range(0, len(col_texts) - 5, 6):
                    name = col_texts[i]
                    speed = col_texts[i + 1].upper()
                    source = col_texts[i + 3]
                    dest = col_texts[i + 4]
                    time_str = col_texts[i + 5]

                    if "AC" in name.upper():
                        all_trains.append({
                            'line': 'WR',
                            'time': time_str,
                            'source': source,
                            'dest': dest,
                            'type': f"AC {speed}",
                            'is_ac': True
                        })

    except Exception as e:
        print(f"[Western Railway] Error scraping AC trains: {e}")

    # Remove duplicates
    seen = set()
    unique_trains = []
    for t in all_trains:
        key = (t['time'], t['source'], t['dest'])
        if key not in seen:
            seen.add(key)
            unique_trains.append(t)

    print(f"[Western Railway] Found {len(unique_trains)} trains total")
    return unique_trains


def scrape_central_railway():
    """Scrape Central Railway trains from mumbailifeline.com"""
    print("\n[Central Railway] Scraping from mumbailifeline.com...")

    routes = [
        # (from, to, direction)
        ("Mumbai_CST", "Kalyan", "DOWN"),
        ("Kalyan", "Mumbai_CST", "UP"),
        ("Mumbai_CST", "Thane", "DOWN"),
        ("Thane", "Mumbai_CST", "UP"),
        ("Mumbai_CST", "Kasara", "DOWN"),
        ("Mumbai_CST", "Karjat", "DOWN"),
    ]

    all_trains = []

    for src, dst, direction in routes:
        url = f"https://www.mumbailifeline.com/timetable.php?sel_route=central&sfrom={src}&sto={dst}&time1=04:00+AM&time2=11:59+PM&Submit=Submit"

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')

            tables = soup.find_all('table')

            # Find the timetable table (usually has > 10 rows)
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 10:
                    continue

                # Check if header row has train info
                header = rows[0].find_all(['td', 'th'])
                header_text = [h.get_text(strip=True).lower() for h in header]

                if 'train' not in ' '.join(header_text) and 'speed' not in ' '.join(header_text):
                    continue

                # Parse train rows
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) < 6:
                        continue

                    train_no = cols[0].get_text(strip=True)
                    speed = cols[1].get_text(strip=True).upper()
                    origin = cols[3].get_text(strip=True)
                    dest_station = cols[4].get_text(strip=True)
                    time_str = cols[5].get_text(strip=True)

                    # Skip header-like rows
                    if 'train' in train_no.lower() or not time_str:
                        continue

                    # Check if AC train
                    is_ac = 'AC' in train_no.upper()
                    train_type = f"AC {speed}" if is_ac else speed

                    # Clean up time format
                    time_str = time_str.replace('\n', '').strip()

                    all_trains.append({
                        'line': 'CR',
                        'time': time_str,
                        'source': origin.replace('_', ' ').replace('Cst', 'CSMT').replace('Mumbai Cst', 'CSMT'),
                        'dest': dest_station.replace('_', ' '),
                        'type': train_type,
                        'is_ac': is_ac
                    })

            time.sleep(0.5)  # Be nice to the server

        except Exception as e:
            print(f"[Central Railway] Error scraping {src} to {dst}: {e}")

    # Remove duplicates
    seen = set()
    unique_trains = []
    for t in all_trains:
        key = (t['time'], t['source'], t['dest'])
        if key not in seen:
            seen.add(key)
            unique_trains.append(t)

    print(f"[Central Railway] Found {len(unique_trains)} trains")
    return unique_trains


def scrape_harbour_line():
    """Scrape Harbour Line trains from mumbailifeline.com"""
    print("\n[Harbour Line] Scraping from mumbailifeline.com...")

    routes = [
        ("Mumbai_CST", "Panvel", "DOWN"),
        ("Panvel", "Mumbai_CST", "UP"),
        ("Mumbai_CST", "Vashi", "DOWN"),
        ("Vashi", "Mumbai_CST", "UP"),
    ]

    all_trains = []

    for src, dst, direction in routes:
        url = f"https://www.mumbailifeline.com/timetable.php?sel_route=harbour&sfrom={src}&sto={dst}&time1=04:00+AM&time2=11:59+PM&Submit=Submit"

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')

            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 10:
                    continue

                header = rows[0].find_all(['td', 'th'])
                header_text = [h.get_text(strip=True).lower() for h in header]

                if 'train' not in ' '.join(header_text) and 'speed' not in ' '.join(header_text):
                    continue

                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) < 6:
                        continue

                    train_no = cols[0].get_text(strip=True)
                    speed = cols[1].get_text(strip=True).upper()
                    origin = cols[3].get_text(strip=True)
                    dest_station = cols[4].get_text(strip=True)
                    time_str = cols[5].get_text(strip=True)

                    if 'train' in train_no.lower() or not time_str:
                        continue

                    is_ac = 'AC' in train_no.upper()
                    train_type = f"AC {speed}" if is_ac else speed

                    time_str = time_str.replace('\n', '').strip()

                    all_trains.append({
                        'line': 'HR',
                        'time': time_str,
                        'source': origin.replace('_', ' ').replace('Cst', 'CSMT').replace('Mumbai Cst', 'CSMT'),
                        'dest': dest_station.replace('_', ' '),
                        'type': train_type,
                        'is_ac': is_ac
                    })

            time.sleep(0.5)

        except Exception as e:
            print(f"[Harbour Line] Error scraping {src} to {dst}: {e}")

    # Remove duplicates
    seen = set()
    unique_trains = []
    for t in all_trains:
        key = (t['time'], t['source'], t['dest'])
        if key not in seen:
            seen.add(key)
            unique_trains.append(t)

    print(f"[Harbour Line] Found {len(unique_trains)} trains")
    return unique_trains


def main():
    """Main function to scrape all train data"""
    print("=" * 60)
    print("Mumbai Local Train - Complete Data Scraper")
    print("=" * 60)

    # Scrape all lines
    wr_trains = scrape_western_railway()
    cr_trains = scrape_central_railway()
    hr_trains = scrape_harbour_line()

    # Combine all trains
    all_trains = wr_trains + cr_trains + hr_trains

    if all_trains:
        df = pd.DataFrame(all_trains)

        # Add train ID
        df['id'] = [f"{row['line']}_{i:04d}" for i, row in df.iterrows()]

        # Separate AC and non-AC trains
        ac_trains = df[df['is_ac'] == True].copy()
        non_ac_trains = df[df['is_ac'] == False].copy()

        # Save AC trains
        if len(ac_trains) > 0:
            ac_trains = ac_trains[['id', 'line', 'time', 'source', 'dest', 'type']]
            ac_trains.to_csv('mumbai_ac_trains.csv', index=False)
            print(f"\nSaved {len(ac_trains)} AC trains to 'mumbai_ac_trains.csv'")

        # Save non-AC trains
        if len(non_ac_trains) > 0:
            non_ac_trains = non_ac_trains[['id', 'line', 'time', 'source', 'dest', 'type']]
            non_ac_trains.to_csv('mumbai_local_trains.csv', index=False)
            print(f"Saved {len(non_ac_trains)} non-AC trains to 'mumbai_local_trains.csv'")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Western Railway: {len(wr_trains)} trains")
        print(f"Central Railway: {len(cr_trains)} trains")
        print(f"Harbour Line:    {len(hr_trains)} trains")
        print("-" * 40)
        print(f"Total AC:        {len(ac_trains)} trains")
        print(f"Total Non-AC:    {len(non_ac_trains)} trains")
        print(f"GRAND TOTAL:     {len(all_trains)} trains")
        print("=" * 60)

    else:
        print("\nNo data scraped. Check your internet connection.")


if __name__ == "__main__":
    main()
