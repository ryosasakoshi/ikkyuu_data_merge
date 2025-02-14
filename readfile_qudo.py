import pandas as pd
import numpy as np
import glob


top_bottom_dic = {"T": 0, "B": 1}


def read_qudo(game_id, filepath_qudo=None):
    # Check if filepath is provided
    if filepath_qudo is None:
        # Create an empty DataFrame with the desired columns
        columns = [
            "game_id", "sessionId", "inning", "batterIndex", "pitchCount",
            "timestamp", "speed", "finalSpeed", "duration", "moveV", "moveH",
            "releasePointX", "releasePointY", "releasePointZ",
            "strikePointX", "strikePointY", "strikePointZ",
            "spin", "spinTilt", "spinEfficency",
            "spinAxisX", "spinAxisY", "spinAxisZ",
            "exitSpeed", "exitAngle", "exitDirection",
            "exitVelocityX", "exitVelocityY", "exitVelocityZ",
            "hitPointX", "hitPointY", "hitPointZ",
            "top_bottom", "pa_of_inning", "pitches_of_pa"
        ]

        # Create an empty DataFrame with the specified columns
        df_qudo = pd.DataFrame(columns=columns)

        # Add game_id as the first column
        df_qudo.insert(0, "game_id", game_id)

        return df_qudo

    # Existing code for file reading remains the same
    # Construct the full file path using glob
    matching_files = glob.glob(f"{filepath_qudo}")

    if not matching_files:
        raise FileNotFoundError(f"No file found matching pattern: {filepath_qudo}")

    # Take the first matching file
    file_path = matching_files[0]
    
    
    try:
        # CSVファイルを読み込む
        df_qudo = pd.read_csv(file_path, engine='python', encoding="shift-jis")
    
        # ナロースペース (U+202F) を半角スペース (U+0020) に変換
        df_qudo["timestamp"] = df_qudo["timestamp"].str.replace("\u202F", " ", regex=True)
    
        # 文字化け「窶ｯPM」を「 PM」に修正
        df_qudo["timestamp"] = df_qudo["timestamp"].replace("窶ｯPM", " PM", regex=True)
    
        # 0時台の "PM" だけを "12:XX AM" に修正 (AM のデータには影響しない)
        df_qudo["timestamp"] = df_qudo["timestamp"].replace(
            r"\b0:(\d{2}:\d{2}) PM\b", r"12:\1 AM", regex=True
        )
    
        # 変換前のデータを確認（デバッグ用）
        print("Unique timestamps before conversion:")
        print(df_qudo["timestamp"].unique())
    
        # timestamp を datetime に変換
        df_qudo["timestamp"] = pd.to_datetime(df_qudo["timestamp"], format="%Y-%m-%d %I:%M:%S %p", errors="coerce")
    
        # 変換後のデータを確認（デバッグ用）
        # print("Converted timestamps:")
        # print(df_qudo["timestamp"].head())
    
        # Print file info for debugging
        # print(f"Read file: {file_path}")
        # print(f"DataFrame shape: {df_qudo.shape}")
    
        df_qudo["inn"] = df_qudo["inning"].astype(str).str[0]
        df_qudo["top_bottom"] = df_qudo["inning"].astype(str).str[1]
        df_qudo["inning"] = df_qudo["inn"].astype(int)
    
        df_qudo["top_bottom"] = df_qudo["top_bottom"].replace(top_bottom_dic)
    
        df_qudo["pa_of_inning"] = df_qudo["batterIndex"] + 1
        df_qudo["pitches_of_pa"] = df_qudo["pitchCount"] + 1
    
        df_qudo = df_qudo[df_qudo["batterIndex"] != 99]
        df_qudo = df_qudo[df_qudo["sessionId"] != 0]
    
        # 変換後のデータを確認
        print(df_qudo.head())





        df_qudo = df_qudo[
            [
                "sessionId", "inning", "batterIndex", "pitchCount",
                "timestamp", "speed", "finalSpeed", "duration", "moveV", "moveH",
                "releasePointX", "releasePointY", "releasePointZ",
                "strikePointX", "strikePointY", "strikePointZ",
                "spin", "spinTilt", "spinEfficency",
                "spinAxisX", "spinAxisY", "spinAxisZ",
                "exitSpeed", "exitAngle", "exitDirection",
                "exitVelocityX", "exitVelocityY", "exitVelocityZ",
                "hitPointX", "hitPointY", "hitPointZ",
                "top_bottom", "pa_of_inning", "pitches_of_pa"
            ]
        ]

        # 先頭列に試合IDを追加する
        df_qudo.insert(0, "game_id", game_id)

        return df_qudo

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        raise
