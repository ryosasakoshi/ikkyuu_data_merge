import pandas as pd
import numpy as np
import glob
import os

def read_ikkyu(game_id, filepath_ikkyu):
    # Construct the full file path using glob
    matching_files = glob.glob(f"{filepath_ikkyu}")

    if not matching_files:
        raise FileNotFoundError(f"No file found matching pattern: {filepath_ikkyu}")

    # Take the first matching file
    file_path = matching_files[0]

    try:
        # Read the CSV file
        df_ikkyu = pd.read_csv(file_path, engine='python', encoding="shift_jis")

        # Print file info for debugging
        print(f"Read file: {file_path}")
        print(f"DataFrame shape: {df_ikkyu.shape}")
        print(df_ikkyu.head())

        df_ikkyu = df_ikkyu[df_ikkyu["pitched_result"]!="投手牽制"]
        df_ikkyu = df_ikkyu[df_ikkyu["pitched_result"]!="捕手牽制"]

        # Add game_id column
        df_ikkyu.insert(0, "game_id", game_id)

        # Add game_play_num column
        df_ikkyu.insert(1, "game_play_num", range(1, len(df_ikkyu.index) + 1))

        # Clean pitched_ball_type
        df_ikkyu["pitched_ball_type"] = df_ikkyu["pitched_ball_type"].str.split("(", expand=True)[0]

        # # Rename columns
        # df_ikkyu = df_ikkyu.rename(
        #     columns={
        #         "pitcher_id": "pitcher_id_s",
        #     }
        # )

        return df_ikkyu

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        raise
