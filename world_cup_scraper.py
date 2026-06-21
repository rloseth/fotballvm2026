import argparse
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

def fetch_match_data():
    """
    Fetches the match data.
    """
    import requests
    URL = "https://tv2no-livesport-api.public.tv2.no/v3/football/seasons/a315b842-f4bc-5687-9ecb-3e06d6acdf9a/matchesByDates"
    response = requests.get(URL)
    response.raise_for_status()
    return response.json()

def format_time_to_oslo(utc_time_str):
    """
    Converts a UTC time string to Europe/Oslo timezone.
    Returns just the time (HH:MM).
    """
    if not utc_time_str:
        return "TBA"
    
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=ZoneInfo("UTC"))
    oslo_time = utc_time.astimezone(ZoneInfo("Europe/Oslo"))
    return oslo_time.strftime("%H:%M")

def get_channel(broadcast):
    """Parses broadcast data to determine channel."""
    if not isinstance(broadcast, dict) or len(broadcast) < 4:
        return "N/D"
    if broadcast.get("isTV2") is True:
        return "TV2"
    elif broadcast.get("isNRK") is True:
        return "NRK"
    return "N/D"

def display_matches(days_data, show_results):
    """
    Parses and prints the matches to terminal.
    """
    print("=" * 80)
    print(" 🏆 WORLD CUP 2026 SCHEDULE (US/CAN/MEX) 🏆 ".center(80))
    print("=" * 80)

    for day in days_data:
        date_title = day.get("title", "Unknown Date").title()
        print(f"\n📅 {date_title}")
        print("-" * 80)

        matches = day.get("matches", [])
        if not matches:
            print("  No matches scheduled.")
            continue

        for match in matches:
            teams = match.get("teams", [])
            if len(teams) < 2:
                continue

            home_team = teams[0].get("name", "Unknown")
            away_team = teams[1].get("name", "Unknown")
            status = match.get("statusType", "UNKNOWN")
            
            time_oslo = format_time_to_oslo(match.get("startTime"))
            
            match_str = f"  🕒 {time_oslo} | {home_team} vs. {away_team}"
            match_str = match_str.ljust(45)

            channel = get_channel(match.get("broadcast", "N/D"))

            if status == "FINISHED":
                if show_results:
                    home_score = teams[0].get("score", {}).get("total", "0") if teams[0].get("score") else "0"
                    away_score = teams[1].get("score", {}).get("total", "0") if teams[1].get("score") else "0"
                    match_str += f"| ✅ RESULT: {home_score} - {away_score} | 📺 {channel}"
                else:
                    match_str += f"| 🙈 RESULT: [HIDDEN] | 📺 {channel}"
            elif status == "NOT_STARTED":
                match_str += f"| ⏳ UPCOMING | 📺 {channel}"
            else:
                match_str += f"| 🔄 {status} | 📺 {channel}"

            print(match_str)
            
    print("\n" + "=" * 80)

def generate_json(days_data):
    """
    Parses the same data into a clean structure and exports to public/matches.json
    for the static GitHub Pages frontend.
    """
    export_data = []

    for day in days_data:
        date_title = day.get("title", "Unknown Date").title()
        day_matches = []
        
        matches = day.get("matches", [])
        for match in matches:
            teams = match.get("teams", [])
            if len(teams) < 2:
                continue

            status_raw = match.get("statusType", "UNKNOWN")
            if status_raw == "FINISHED":
                status = "completed"
            elif status_raw == "NOT_STARTED":
                status = "upcoming"
            else:
                status = "in_progress"

            home_score = teams[0].get("score", {}).get("total", "0") if teams[0].get("score") else "0"
            away_score = teams[1].get("score", {}).get("total", "0") if teams[1].get("score") else "0"

            day_matches.append({
                "time": format_time_to_oslo(match.get("startTime")),
                "home": teams[0].get("name", "Unknown"),
                "away": teams[1].get("name", "Unknown"),
                "home_score": home_score,
                "away_score": away_score,
                "status": status,
                "channel": get_channel(match.get("broadcast", "N/D"))
            })
            
        if day_matches:
            export_data.append({
                "date": date_title,
                "matches": day_matches
            })

    # Ensure the directory exists
    os.makedirs("public", exist_ok=True)
    
    with open("public/matches.json", "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ JSON file created successfully at 'public/matches.json'!")

def main():
    parser = argparse.ArgumentParser(
        description="World Cup 2026 CLI Scraper - No Spoilers allowed!"
    )
    parser.add_argument(
        "--show-results",
        action="store_true",
        help="Include this flag to show results of finished matches in CLI."
    )
    
    args = parser.parse_args()
    
    try:
        data = fetch_match_data()
        
        # 1. Output to CLI
        display_matches(data, args.show_results)
        
        # 2. Output to JSON for frontend
        generate_json(data)
        
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()