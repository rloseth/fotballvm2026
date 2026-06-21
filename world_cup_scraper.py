import argparse
import json
from datetime import datetime
from zoneinfo import ZoneInfo

def fetch_match_data():
    """
    Fetches the match data.
    For this example, we assume you saved the JSON provided to a file named 'data.json'.
    In a real scenario, you uncomment the requests logic below.
    """
    import requests
    URL = "https://tv2no-livesport-api.public.tv2.no/v3/football/seasons/a315b842-f4bc-5687-9ecb-3e06d6acdf9a/matchesByDates" 
    response = requests.get(URL)
    response.raise_for_status()
    return response.json()

def format_time_to_oslo(utc_time_str):
    """
    Converts a UTC time string (e.g., '2026-06-11T19:00:00Z') to Europe/Oslo timezone.
    Returns just the time (HH:MM) since the date is already known from the grouping.
    """
    if not utc_time_str:
        return "TBA"
    
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=ZoneInfo("UTC"))
    oslo_time = utc_time.astimezone(ZoneInfo("Europe/Oslo"))
    return oslo_time.strftime("%H:%M")

def display_matches(days_data, show_results):
    """
    Parses and prints the matches, grouped by day, filtering results based on user preference.
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
            # Extract safe defaults in case some data is missing
            teams = match.get("teams", [])
            if len(teams) < 2:
                continue

            home_team = teams[0].get("name", "Unknown")
            away_team = teams[1].get("name", "Unknown")
            status = match.get("statusType", "UNKNOWN")
            
            # Format time
            time_oslo = format_time_to_oslo(match.get("startTime"))
            
            # Base string for the match
            match_str = f"  🕒 {time_oslo} | {home_team} vs. {away_team}"
            
            # Pad the string so results align nicely in the CLI
            match_str = match_str.ljust(45)

            broadcast = match.get("broadcast", "N/D")
            if len(broadcast) < 4:
                channel = "N/D"
            else:
                if broadcast.get("isTV2") == True:
                    channel = "TV2"
                elif broadcast.get("isNRK") == True:
                    channel = "NRK"
                else:
                    channel = "N/D"

            if status == "FINISHED":
                if show_results:
                    # Parse scores - fallback to '0' if it fails
                    home_score = teams[0].get("score", {}).get("total", "0") if teams[0].get("score") else "0"
                    away_score = teams[1].get("score", {}).get("total", "0") if teams[1].get("score") else "0"
                    match_str += f"| ✅ RESULT: {home_score} - {away_score} | 📺 " + channel
                else:
                    match_str += "| 🙈 RESULT: [HIDDEN] | 📺 : " + channel
            elif status == "NOT_STARTED":
                match_str += "| ⏳ UPCOMING | 📺 " + channel
            else:
                match_str += f"| 🔄 {status}"

            print(match_str)
            
    print("\n" + "=" * 80)

def main():
    parser = argparse.ArgumentParser(
        description="World Cup 2026 CLI Scraper - No Spoilers allowed!"
    )
    parser.add_argument(
        "--show-results",
        action="store_true",
        help="Include this flag to show results of finished matches."
    )
    
    args = parser.parse_args()
    
    try:
        data = fetch_match_data()
        display_matches(data, args.show_results)
    except FileNotFoundError:
        print("❌ Error: 'data.json' not found. Please save the API response to this file.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()