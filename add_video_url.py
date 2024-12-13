import numpy as np
import pandas as pd
import datetime
import glob
import os


def add_video_url(df_gamedata, youtube_id=None, start_timestamp=None):
    """
    データフレームに動画URLを追加する関数

    Parameters:
    -----------
    df_gamedata : pandas.DataFrame
        元のデータフレーム
    youtube_id : str, optional
        YouTubeビデオID
    start_timestamp : int , optional
        動画の開始タイムスタンプ（秒単位）

    Returns:
    --------
    pandas.DataFrame
        動画URLが追加されたデータフレーム
    """
    # 引数がNoneの場合の処理
    if df_gamedata.empty:
        # 空のDataFrameの場合、youtube_timestampカラムを追加して返す
        df_gamedata['youtube_timestamp'] = np.nan
        return df_gamedata

    # デフォルト値と入力バリデーション
    rewind_time = -4  # 調整時間4秒前から再生

    # YouTube IDがない場合
    if youtube_id is None:
        df_gamedata['youtube_timestamp'] = np.nan
        return df_gamedata

    # YouTubeの埋め込みリンクテンプレート
    video_url_template = f"https://youtu.be/{youtube_id}?t="

    # start_timestampがNoneの場合は0を使用
    if start_timestamp is None:
        start_timestamp = 0

    try:
        # タイムスタンプをdatetimeに変換
        df_gamedata["dateTime_format"] = pd.to_datetime(
            df_gamedata["timestamp"], format="%Y-%m-%d %I:%M:%S %p", errors="coerce"
        )

        # 欠損値の補完 (前方補完)
        df_gamedata["dateTime_fill"] = df_gamedata["dateTime_format"].ffill()

        # 時間差の計算
        df_gamedata["diff"] = df_gamedata["dateTime_fill"].diff()

        # 累積秒数の計算
        df_gamedata["total_seconds"] = df_gamedata["diff"].dt.total_seconds().cumsum()
        df_gamedata["total_seconds"] = (
            df_gamedata["total_seconds"].fillna(0).astype(np.int64)
        )

        # 動画URLの生成
        df_gamedata["youtube_timestamp"] = video_url_template + (
            df_gamedata["total_seconds"] + start_timestamp + rewind_time
        ).astype(str)

    except ValueError as e:
        print(f"日付変換エラー: {e}")
        df_gamedata["youtube_timestamp"] = np.nan
    except Exception as e:
        print(f"予期せぬエラー: {e}")
        df_gamedata["youtube_timestamp"] = np.nan

    # 一時的な列の削除
    df_gamedata["timestamp"] = df_gamedata["dateTime_format"]
    columns_to_drop = ["dateTime_format", "dateTime_fill", "diff", "total_seconds"]
    df_gamedata = df_gamedata.drop(columns=columns_to_drop, axis=1, errors='ignore')

    return df_gamedata