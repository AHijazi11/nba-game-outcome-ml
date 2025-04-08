**Note**: This project was refactored to be more modular and replace csv files with Postgre SQL database and a Streamlit App hosted on Herok for continuous data updates, predictions, and model training. The new repo and Streamlit App can be viewed here: [Repo](https://github.com/AHijazi11/nba-game-prediction-heroku-streamlit) | [Streamlit](https://nba-game-predictions-streamlit-49d83933a063.herokuapp.com/)

# 🏀 NBA Game Outcome Prediction – Project Overview

I started this project because I thought it would be fun to apply machine learning techniques to NBA game predictions. My goal was not only to challenge myself with a complex, real-world dataset but also to explore the potential of these models for making informed bets if the predictions proved accurate enough.

This notebook builds a machine learning pipeline to predict the outcome of NBA games using historical data and engineered features. The pipeline includes:

- **Preprocessing:** Detailed cleaning and normalization of raw data.
- **Feature Engineering:** Creation of advanced metrics and rolling statistics.
- **Model Training:** Implementation of various machine learning models.
- **Evaluation:** Comprehensive assessment of model performance.
- **Predictions:** Generating predictions for upcoming games.

Historical data and the list of upcoming games are fetched from the Balldontlie API using the script `get_all_nba_data_api.py`.

---

## 📊 Data Preprocessing & Feature Engineering

The notebook uses a merged dataset containing game-level statistics, team metrics, and player data. The data is split chronologically into training, validation, and test sets.

Key engineered features include:

- **Team-level game stats**: e.g., `team_elo`, `season_elo`, `win_streak`, `time_in_season`
- **Opponent-related features**: `opponent_elo`, `opponent_season_elo`
- **Contextual features**: `is_home_game`, `game_postseason`, `travel_distance`
- **Player absence impact**: `absent_players`, `team_absent_impact`
- **Rolling averages**: Stats based on the past 15 games
- **Win/loss streak**: Positive for wins, negative for losses, based on team history
- **ELO ratings**: Calculated in two ways – all-time and reset per season

---

## 🎯 Target Variable

The target for classification is `game_won`:
- `1` if the team won the game
- `0` otherwise

This is a binary classification problem.

---

## 🧠 Model Training

The primary model trained and evaluated is:

- **XGBoost Classifier (`best_xgb_model`)**
  - Tuned using `GridSearchCV`
  - Training on the training set
  - Validation using a hold-out set
  - Test accuracy used for final evaluation

Other models considered:
- LightGBM
- RNNs (Recurrent Neural Networks)
- Ensemble stacking using LightGBM

---

## 🧪 Evaluation & Results

**Metrics computed**:
- Accuracy
- ROC AUC
- Precision, Recall, F1 Score

Best-performing model:
- **LightGBM**
  - **Validation Accuracy**: ~64.5%
  - **Test Accuracy**: ~68%

---

## 🔮 Predictions on Upcoming Games

The notebook includes a separate workflow `predicting_nba_game_outcomes.ipynb` that:

1. Loads upcoming NBA games with partial metadata.
2. Injects missing features (like rolling performance metrics, ELO, injuries, rest days, etc.).
3. Uses the trained `best_xgb_model` model to predict outcomes.
4. Compares predictions with actual game results (manually retrieved from online sources).
5. Computes prediction accuracy for a recent batch of real NBA games.

---

## Comparison of Model Predictions with Actual Outcomes

In example below, trained XGBoost model (using data up to March 11th, 2025) was used to make predictions for NBA games scheduled for March 12th, 2025. After looking up the actual outcomes of the games online, the results are summarized in the table below:

| Game ID  | Date       | Home Team               | Away Team                | Predicted Winner       | Actual Winner          | Correct? |
|----------|------------|-------------------------|--------------------------|------------------------|------------------------|----------|
| 15908677 | 2025-03-12 | Boston Celtics          | Oklahoma City Thunder    | Boston Celtics         | Oklahoma City Thunder  | No       |
| 15908678 | 2025-03-12 | Toronto Raptors         | Philadelphia 76ers       | Toronto Raptors        | Toronto Raptors        | Yes      |
| 15908680 | 2025-03-12 | Houston Rockets         | Phoenix Suns             | Houston Rockets        | Houston Rockets        | Yes      |
| 15908681 | 2025-03-12 | Memphis Grizzlies       | Utah Jazz                | Memphis Grizzlies      | Memphis Grizzlies      | Yes      |
| 15908679 | 2025-03-12 | Miami Heat              | LA Clippers              | LA Clippers            | LA Clippers            | Yes      |
| 15908684 | 2025-03-12 | Portland Trail Blazers  | New York Knicks          | New York Knicks        | New York Knicks        | Yes      |
| 15908682 | 2025-03-12 | San Antonio Spurs       | Dallas Mavericks         | Dallas Mavericks       | San Antonio Spurs      | No       |
| 15908676 | 2025-03-12 | Atlanta Hawks           | Charlotte Hornets        | Atlanta Hawks          | Atlanta Hawks          | Yes      |
| 15908683 | 2025-03-12 | Denver Nuggets          | Minnesota Timberwolves   | Denver Nuggets         | Minnesota Timberwolves | No       |


Out of 9 games, the model correctly predicted 6 games, yielding an accuracy of approximately **67%**. 

This performance is consistent with test metrics and suggests that the tuned **XGBoost model** generalizes reasonably well to upcoming NBA games. While there is still room for improvement, using this model for future game outcome prediction appears to be a viable strategy.

## 📌 Insights & Conclusions

- ELO rating and player absence are strong predictors of game outcome.
- Features with temporal context like rolling averages and streaks add predictive signal.
- A model trained on 6000+ historical games achieves up to **67.5% accuracy** on unseen games.
- Retraining isn't necessary daily, but weekly or after every ~100 games is a reasonable strategy.
- The model's performance was competitive even compared to basic sports betting odds.


## 📌 Future Plans

- Automate the daily retrieval of new NBA game results and feature updates via incremental data retrieval script
- Automate game outcome predictions for games scheduled the next day  
- Retrain the model automatically after every 100 new games are added to the dataset  
- Integrate MLflow to monitor model training history, performance, and potential drift  
- Develop a Streamlit dashboard to display:
  - Recent predictions vs. actual outcomes  
  - Upcoming game predictions  
  - Model performance metrics  
  - Last retrained date and model version
- Experiment with more data and deep learning for improved prediction
- Incorporate betting market data and train on maximizing ROI
- Fully automated and scalable ml pipeline  

---
<br>

# 🏀 NBA Data Fetcher (BallDontLie API) 

This script automates the collection and preparation of NBA data using the [balldontlie API](https://www.balldontlie.io/). It pulls key datasets such as games, advanced stats, box scores, injuries, player rosters, and team standings, then stores them locally in CSV and JSON formats for analysis or machine learning projects. 

Note: "GOAT" paid membership is required by balldontlie to access advanced game stats and box score data.

---

## 📂 What It Does

1. **Authenticates** using your API key from `.env`
2. **Downloads:**
   - Game advanced stats
   - Game metadata
   - Player-level box scores (daily)
   - Player injuries
   - Team standings
   - Active players
3. **Cleans & combines** data into structured CSVs
4. **Deletes temporary JSON files** to save space

---

## 🧠 Key Features

- **Rate-limit handling**: Waits and retries if the API limit is hit
- **Dynamic date filtering**: Only fetches games before today's date
- **Reusable functions**: For both paginated and single-page API endpoints
- **Flat nested API responses**: Ensures clean tabular output

---

## ✅ Requirements

Install dependencies:

```bash
pip install pandas python-dotenv balldontlie
```

Create a `.env` file:

```env
BALLDONTLIE_API_KEY=your_api_key_here
```

---

## 🗂️ Output Files

All files are saved to the `./New_data/` folder:

| File | Description |
|------|-------------|
| `nba_games_<season>.csv` | Metadata for each NBA game |
| `nba_game_advanced_stats_<season>.csv` | Team-level advanced stats |
| `nba_box_scores_combined_<season>.csv` | Player-level game stats |
| `nba_active_players.csv` | Current active players |
| `nba_player_injuries.csv` | Raw injury reports |
| `injured_players_cleaned.csv` | Players marked as "Out" |
| `nba_team_standings_<season>.csv` | Final standings per team |

---

## ⚙️ Customization

To change the NBA seasons pulled, edit this line near the top of the script:

```python
seasons = [2020, 2021, 2022, 2023, 2024]
```

---

## 🧼 Cleanup Behavior

At the end of the run:

- Merges all JSON box scores into one CSV
- Deletes all intermediate JSON files to avoid clutter

---

## ✅ Output

After running, you'll have a full-season dataset — player box scores, team stats, and injuries — all ready for modeling, dashboarding, or analysis. 🎯

---
<br>

# How to Run

This repository contains code to fetch NBA game data, perform data cleaning and feature engineering, train machine learning models to predict NBA game outcomes, and generate predictions for upcoming games.

## Setup Instructions

Follow these steps to download the repo and run the project:

1. **Clone the Repository**

    git clone https://github.com/AHijazi11/nba-game-outcome-ml.git
    cd your-repo

2. **Set Up a Virtual Environment**
   - Create a virtual environment (using venv, for example):
    
        python -m venv venv

   - Activate the virtual environment:
     - **On Windows:**
       
           venv\Scripts\activate
       
     - **On macOS/Linux:**
       
           source venv/bin/activate

3. **Install Dependencies**
   - Install all required packages using the provided requirements.txt file:
    
        pip install -r requirements.txt

4. **Download Historical NBA Data**
   - Run the script get_all_nba_data_api.py to fetch data for specified seasons, by default seasons are 2020 through 2024 (inclusive)

5. **Train Your Models**
   - Open and run the notebook nba_game_data_ml_training.ipynb:
     - This notebook imports the data, performs cleaning and feature engineering, and trains various models (including classic classifiers and RNNs).

6. **Make Predictions for Upcoming Games**
   - Open and run the notebook predicting_nba_game_outcomes.ipynb:
     - Update the list of upcoming games as needed.
     - Run the notebook to generate predictions, which will be displayed at the end.
     - **Important:** Predictions for games scheduled more than 30 days out may be less accurate.

## Summary

- **Data Collection:**  
  The get_all_nba_data_api.py script retrieves NBA game data (default: 2020 through 2024 season).

- **Model Training:**  
  The nba_game_data_ml_training.ipynb notebook cleans the data, engineers features (including advanced metrics like ELO, rest days, absent players, travel distance, and rolling stats), and trains various machine learning models.

- **Predictions:**  
  The predicting_nba_game_outcomes.ipynb notebook is used to predict winners in upcoming games for specified date. Update the date as needed before running the notebook.

By following these instructions, you can set up the environment, train the models, and generate predictions for NBA game outcomes.
