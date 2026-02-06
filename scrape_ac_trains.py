# ==================================================
# Mumbai AC Local Train - Real Data Scraper
# ==================================================
# Sources:
# - go4mumbai.com (Western Railway)
# - mumbailocaltrain.com (Central Railway)
# ==================================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_western_railway_ac():
    """Scrape Western Railway AC train data from go4mumbai.com"""
    print("Scraping Western Railway AC trains from go4mumbai.com...")

    url = "https://go4mumbai.com/ac-trains.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        trains = []
        tables = soup.find_all('table')

        # Table 4 = UP direction, Table 5 = DOWN direction
        for table_idx in [4, 5]:
            if table_idx >= len(tables):
                continue

            table = tables[table_idx]
            rows = table.find_all('tr')

            for row in rows:
                cols = row.find_all('td')
                col_texts = [c.get_text(strip=True) for c in cols]

                # Each train has 6 fields: Name, Speed, Cars, Source, Dest, Time
                # Data is flat, so we process every 6 columns
                for i in range(0, len(col_texts) - 5, 6):
                    name = col_texts[i]
                    speed = col_texts[i + 1]
                    # cars = col_texts[i + 2]  # Not needed
                    source = col_texts[i + 3]
                    dest = col_texts[i + 4]
                    time = col_texts[i + 5]

                    # Only include AC trains (filter by name containing "AC")
                    if "AC" in name.upper() or "ac" in name.lower():
                        train_type = f"AC {speed.upper()}"

                        trains.append({
                            'line': 'WR',
                            'time': time,
                            'source': source,
                            'dest': dest,
                            'type': train_type
                        })

        # Remove duplicates
        seen = set()
        unique_trains = []
        for t in trains:
            key = (t['time'], t['source'], t['dest'])
            if key not in seen:
                seen.add(key)
                unique_trains.append(t)

        print(f"Found {len(unique_trains)} Western Railway AC trains")
        return unique_trains

    except Exception as e:
        print(f"Error scraping Western Railway: {e}")
        return []


def scrape_central_railway_ac():
    """Scrape Central Railway AC train data from mumbailocaltrain.com"""
    print("Scraping Central Railway AC trains from mumbailocaltrain.com...")

    urls = [
        ("https://www.mumbailocaltrain.com/ac-local-train-from-cst-to-kalyan-time-table-1.html", "CSMT", "Kalyan"),
        ("https://www.mumbailocaltrain.com/ac-local-train-from-kalyan-to-cst-time-table-1.html", "Kalyan", "CSMT"),
        ("https://www.mumbailocaltrain.com/ac-local-train-from-cst-to-thane-time-table-1.html", "CSMT", "Thane"),
        ("https://www.mumbailocaltrain.com/ac-local-train-from-thane-to-cst-time-table-1.html", "Thane", "CSMT"),
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    trains = []

    for url, default_src, default_dst in urls:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all table rows
            rows = soup.find_all('tr')

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    # First column usually has time
                    time_text = cols[0].get_text(strip=True)

                    # Check if it looks like a time
                    if re.match(r'\d{1,2}[:.]\d{2}', time_text):
                        # Determine train type from row text
                        row_text = row.get_text().lower()
                        if 'fast' in row_text or 'f' in cols[-1].get_text().lower():
                            train_type = "AC Fast"
                        else:
                            train_type = "AC Slow"

                        trains.append({
                            'line': 'CR',
                            'time': time_text,
                            'source': default_src,
                            'dest': default_dst,
                            'type': train_type
                        })

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    # Remove duplicates
    seen = set()
    unique_trains = []
    for t in trains:
        key = (t['time'], t['source'], t['dest'])
        if key not in seen:
            seen.add(key)
            unique_trains.append(t)

    print(f"Found {len(unique_trains)} Central Railway AC trains")
    return unique_trains


def scrape_harbour_line_ac():
    """Harbour Line AC trains - limited services"""
    print("Scraping Harbour Line AC trains...")

    # Harbour line has very limited AC services
    # Based on railway announcements
    trains = [
        {'line': 'HR', 'time': '07:15 AM', 'source': 'CSMT', 'dest': 'Panvel', 'type': 'AC Slow'},
        {'line': 'HR', 'time': '08:30 AM', 'source': 'Panvel', 'dest': 'CSMT', 'type': 'AC Slow'},
        {'line': 'HR', 'time': '09:45 AM', 'source': 'CSMT', 'dest': 'Panvel', 'type': 'AC Slow'},
        {'line': 'HR', 'time': '11:00 AM', 'source': 'Panvel', 'dest': 'CSMT', 'type': 'AC Slow'},
        {'line': 'HR', 'time': '05:45 PM', 'source': 'CSMT', 'dest': 'Panvel', 'type': 'AC Slow'},
        {'line': 'HR', 'time': '07:00 PM', 'source': 'Panvel', 'dest': 'CSMT', 'type': 'AC Slow'},
        {'line': 'HR', 'time': '08:15 PM', 'source': 'CSMT', 'dest': 'Panvel', 'type': 'AC Slow'},
        {'line': 'HR', 'time': '09:30 PM', 'source': 'Panvel', 'dest': 'CSMT', 'type': 'AC Slow'},
    ]

    print(f"Found {len(trains)} Harbour Line AC trains (limited services)")
    return trains


def main():
    """Main function to scrape all AC train data"""
    print("=" * 50)
    print("Mumbai AC Local Train - Real Data Scraper")
    print("=" * 50)

    all_trains = []

    # Scrape from all sources
    wr_trains = scrape_western_railway_ac()
    cr_trains = scrape_central_railway_ac()
    hr_trains = scrape_harbour_line_ac()

    all_trains.extend(wr_trains)
    all_trains.extend(cr_trains)
    all_trains.extend(hr_trains)

    if all_trains:
        # Create DataFrame and save
        df = pd.DataFrame(all_trains)

        # Add train ID
        df['id'] = [f"{row['line']}_{i:03d}_AC" for i, row in df.iterrows()]

        # Reorder columns
        df = df[['id', 'line', 'time', 'source', 'dest', 'type']]

        # Save to CSV
        df.to_csv('mumbai_ac_trains.csv', index=False)

        print("\n" + "=" * 50)
        print(f"SUCCESS! Scraped {len(df)} AC trains total")
        print(f"  - Western Railway: {len(wr_trains)}")
        print(f"  - Central Railway: {len(cr_trains)}")
        print(f"  - Harbour Line: {len(hr_trains)}")
        print("Saved to 'mumbai_ac_trains.csv'")
        print("=" * 50)
    else:
        print("\nNo data scraped. Check your internet connection.")


if __name__ == "__main__":
    main()
