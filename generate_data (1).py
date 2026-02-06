import pandas as pd
from datetime import datetime, timedelta
import random

def generate_full_ac_schedule():
    print("Initializing Full AC Schedule Generator...")

    all_ac_trains = []

    # --- AC TRAIN LOGIC (Based on Real World Frequency) ---
    # Western Line has MAX AC trains (approx every 30-45 mins)
    # Central Line has Medium (approx every 1 hour)
    # Harbour Line has Very Less (approx every 2-3 hours)

    ac_configs = [
        # (Line, Start, End, Stops, Peak_Gap_Mins, OffPeak_Gap_Mins)
        
        # WESTERN LINE (High Frequency)
        ("WR", "Churchgate", "Virar", ["Bandra", "Andheri", "Borivali", "Vasai"], 35, 60),
        ("WR", "Churchgate", "Borivali", ["Bandra", "Andheri"], 45, 90),
        
        # CENTRAL LINE (Medium Frequency)
        ("CR", "CSMT", "Kalyan", ["Dadar", "Kurla", "Ghatkopar", "Thane", "Dombivli"], 50, 80),
        ("CR", "CSMT", "Thane", ["Dadar", "Kurla", "Ghatkopar"], 60, 120),
        ("CR", "CSMT", "Titwala", ["Dadar", "Thane", "Kalyan"], 90, 150),
        
        # HARBOUR LINE (Low Frequency)
        ("HR", "CSMT", "Panvel", ["Vadala", "Kurla", "Vashi", "Nerul", "Belapur"], 90, 180),
    ]

    # Time Loop: 5:00 AM to 1:00 AM
    start_time = datetime.strptime("05:00", "%H:%M")
    end_time = datetime.strptime("01:00", "%H:%M") + timedelta(days=1)

    # Generate schedule for each Route Configuration
    for line, start_stn, end_stn, stops, peak_gap, off_gap in ac_configs:
        
        # Reset clock for this specific route
        current_time = start_time
        
        while current_time < end_time:
            # Check Peak Hours
            h = current_time.hour
            is_peak = (8 <= h <= 11) or (17 <= h <= 21)
            
            # Decide gap based on time
            gap = peak_gap if is_peak else off_gap
            
            # Add some randomness (+/- 10 mins) so it looks natural
            variation = random.randint(-10, 10)
            actual_gap = max(15, gap + variation) # Minimum 15 min gap
            
            current_time += timedelta(minutes=actual_gap)
            
            if current_time >= end_time:
                break

            # Generate BOTH Directions (UP & DOWN)
            for direction in ["UP", "DOWN"]:
                if direction == "DOWN":
                    src, dst = start_stn, end_stn
                else:
                    src, dst = end_stn, start_stn
                
                # AC Trains are usually Fast on WR/CR, Slow on HR
                if line == "HR":
                    speed_type = "AC Slow"
                else:
                    # On WR/CR, most ACs are fast, but some are slow
                    speed_type = "AC Fast" if random.random() > 0.2 else "AC Slow"

                # ID: WR_0930_AC
                t_str = current_time.strftime("%I:%M %p")
                t_id = current_time.strftime("%H%M")
                train_id = f"{line}_{t_id}_{src[:2].upper()}{dst[:2].upper()}_AC"

                all_ac_trains.append({
                    "id": train_id,
                    "line": line,
                    "time": t_str,
                    "source": src,
                    "dest": dst,
                    "type": speed_type,
                    "dt_iso": current_time # For sorting
                })

    # --- SAVE ---
    df = pd.DataFrame(all_ac_trains)
    
    # Sort by Time
    df = df.sort_values(by="dt_iso").drop(columns=["dt_iso"])
    
    df.to_csv("mumbai_ac_trains.csv", index=False)
    
    print(f"SUCCESS! Generated {len(df)} AC Trains covering all lines.")
    print("Saved to 'mumbai_ac_trains.csv'")

if __name__ == "__main__":
    generate_full_ac_schedule()