import os
import time
import json
import csv
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from balldontlie import BalldontlieAPI
from balldontlie.exceptions import RateLimitError
from balldontlie.exceptions import ServerError

# Load API Key
load_dotenv()
API_KEY = os.getenv("BALLDONTLIE_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Set the BALLDONTLIE_API_KEY environment variable.")

# Initialize API Client
api = BalldontlieAPI(api_key=API_KEY)

# Function to extract and clean API response data
def extract_values(data_list):
    cleaned_data = []
    for item in data_list:
        cleaned_item = {}
        for key, value in item.__dict__.items():
            if hasattr(value, "__dict__"):
                nested_data = {f"{key}_{k}": v for k, v in value.__dict__.items()}
                cleaned_item.update(nested_data)
            else:
                cleaned_item[key] = value
        cleaned_data.append(cleaned_item)
    return cleaned_data

# Optimized pagination function
def fetch_all_data(endpoint_func, filename, params={}):
    all_data = []
    cursor = None
    while True:
        try:
            if cursor:
                params["cursor"] = cursor
            params["per_page"] = 100
            response = endpoint_func(**params)
            extracted = extract_values(response.data)
            all_data.extend(extracted)
            cursor = response.meta.next_cursor
            print(f"✅ Retrieved {len(all_data)} records for {filename}...")
            if not cursor:
                break
        except RateLimitError:
            print("⚠️ Rate limit reached. Waiting for 10 seconds before retrying...")
            time.sleep(10)

    df = pd.DataFrame(all_data)
    df.to_csv(filename, index=False)
    print(f"✅ {filename} saved successfully with {len(df)} records!")

# Function for single-page data fetching
def fetch_single_page(endpoint_func, filename, params={}):
    try:
        response = endpoint_func(**params)
        data_list = response.data
        if not data_list:
            print(f"⚠️ No data returned for {filename}!")
            return

        cleaned_data = extract_values(data_list)
        df = pd.DataFrame(cleaned_data)
        df.to_csv(filename, index=False)
        print(f"✅ {filename} saved successfully!")

    except RateLimitError:
        print("⚠️ Rate limit reached. Waiting for 10 seconds before retrying...")
        time.sleep(10)
        fetch_single_page(endpoint_func, filename, params)


# Pick NBA seasons
seasons = [2020, 2021, 2022, 2023, 2024]

# Loop through each season to fetch and process season-dependent data
for season in seasons:

    # Step 1: Fetch Advanced Stats
    fetch_all_data(api.nba.advanced_stats.list, f"./New_data/nba_game_advanced_stats_{season}.csv", {"seasons": [season]})

    # Step 2: Fetch All NBA Games
    fetch_all_data(api.nba.games.list, f"./New_data/nba_games_{season}.csv", {"seasons": [season]})


    # Step 3: Fetch Box Scores
    file_path = f"./New_data/nba_games_{season}.csv"

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
    else:
        df_games = pd.read_csv(file_path)
        today = datetime.today().strftime("%Y-%m-%d")
        valid_dates = [date for date in df_games["date"].unique() if date < today]

        for date in valid_dates:
            try:
                print(f"📅 Fetching box scores for {date}...")
                api_response = api.nba.box_scores.get_by_date(date=date)
                data = api_response.model_dump_json()

                # Save response to JSON
                with open(f"./New_data/nba_box_scores_{date}.json", "w") as f:
                    json.dump(data, f, indent=4)

            except ServerError as e:
                print(f"⚠️ Error fetching box scores for {date}: {e}. Skipping this date...")
                time.sleep(2)  # Short delay before the next request

        print("✅ Finished fetching box scores!")

    # Step 4: Combine Box Scores into One CSV
    input_folder = "./New_data/"
    output_file = f"./New_data/nba_box_scores_combined_{season}.csv"
    headers = [
        "date", "season", "status", "home_team_id", "home_team", "visitor_team_id", "visitor_team",
        "home_score", "visitor_score", "player_id", "player_first_name", "player_last_name",
        "team", "minutes", "fgm", "fga", "fg_pct", "fg3m", "fg3a", "fg3_pct", "ftm", "fta",
        "ft_pct", "oreb", "dreb", "reb", "ast", "stl", "blk", "turnover", "pf", "pts"
    ]
    all_games = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, str):
                data = json.loads(data)

            games = data.get("data", [])
            all_games.extend(games)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for game in all_games:
            date = game.get("date", "")
            season = game.get("season", "")
            status = game.get("status", "")
            home_team = game.get("home_team", {})
            visitor_team = game.get("visitor_team", {})
            
            home_team_id = home_team.get("id", "")
            home_team_name = home_team.get("full_name", "")
            visitor_team_id = visitor_team.get("id", "")
            visitor_team_name = visitor_team.get("full_name", "")
            
            home_score = game.get("home_team_score", "")
            visitor_score = game.get("visitor_team_score", "")

            for team_key in ["home_team", "visitor_team"]:
                team = game.get(team_key, {})
                team_name = team.get("full_name", "")
                
                for player in team.get("players", []):
                    player_info = player.get("player", {})
                    player_id = player_info.get("id", "")
                    player_first_name = player_info.get("first_name", "")
                    player_last_name = player_info.get("last_name", "")
                    
                    minutes = player.get("min", "")
                    fgm = player.get("fgm", "")
                    fga = player.get("fga", "")
                    fg_pct = player.get("fg_pct", "")
                    fg3m = player.get("fg3m", "")
                    fg3a = player.get("fg3a", "")
                    fg3_pct = player.get("fg3_pct", "")
                    ftm = player.get("ftm", "")
                    fta = player.get("fta", "")
                    ft_pct = player.get("ft_pct", "")
                    oreb = player.get("oreb", "")
                    dreb = player.get("dreb", "")
                    reb = player.get("reb", "")
                    ast = player.get("ast", "")
                    stl = player.get("stl", "")
                    blk = player.get("blk", "")
                    turnover = player.get("turnover", "")
                    pf = player.get("pf", "")
                    pts = player.get("pts", "")
                    
                    writer.writerow([
                        date, season, status, home_team_id, home_team_name, visitor_team_id, visitor_team_name,
                        home_score, visitor_score, player_id, player_first_name, player_last_name,
                        team_name, minutes, fgm, fga, fg_pct, fg3m, fg3a, fg3_pct, ftm, fta,
                        ft_pct, oreb, dreb, reb, ast, stl, blk, turnover, pf, pts
                    ])

    print(f"Data from {len(all_games)} games exported successfully to {output_file} 🎯")

    # Check if the output CSV exists before deletion
    if os.path.exists(output_file):
        print(f"✅ {output_file} exists. Proceeding with JSON file deletion...")

        # Loop through all JSON files in the folder
        for filename in os.listdir(input_folder):
            if filename.startswith("nba_box_scores_") and filename.endswith(".json"):
                file_path = os.path.join(input_folder, filename)
                os.remove(file_path)
                print(f"🗑️ Deleted JSON file: {filename}")

        print("✅ All JSON files deleted successfully!")
    else:
        print(f"⚠️ {output_file} not found. JSON files will not be deleted.")

    # Step 5: Fetch Team Standings
    # Ensure season is an integer
    season = int(season)
    fetch_single_page(api.nba.standings.get, f"./New_data/nba_team_standings_{season}.csv", {"season": season})    

# ------------------------------
# Season-independent steps:
# ------------------------------

# Step 6: Fetch Active Players List
fetch_all_data(api.nba.players.list_active, "./New_data/nba_active_players.csv")    

# Step 7: Fetch and Process Injury Data
fetch_all_data(api.nba.injuries.list, "./New_data/nba_player_injuries.csv")
injury_data = pd.read_csv("./New_data/nba_player_injuries.csv")
injured_players = injury_data[injury_data["status"] == "Out"][["player_id"]]
injured_players.to_csv("./New_data/injured_players_cleaned.csv", index=False)

print("✅ All data successfully retrieved and saved! 🏀")