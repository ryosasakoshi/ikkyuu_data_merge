import streamlit as st
import pandas as pd
import numpy as np
import readfile_qudo
import readfile_ikkyu
import add_video_url
import os


def merge_game_data(game_id, filepath_ikkyu, filepath_qd, youtube_id, start_timestamp):
    """
    ゲームデータを結合する関数

    Args:
        game_id (str): 試合ID
        filepath_ikkyu (str): 一球速報のCSVファイルパス
        filepath_qd (str): Qudoのファイルパス
        youtube_id (str): YouTubeビデオID
        start_timestamp (str): 開始タイムスタンプ

    Returns:
        pd.DataFrame: 結合されたデータフレーム
    """
    try:
        # 一球速報のファイルを読み込む
        ikkyu_df = readfile_ikkyu.read_ikkyu(game_id, filepath_ikkyu)
        print(ikkyu_df)
        st.write(f"一球速報データ: {ikkyu_df.shape}")

        # QUDOデータの読み込み（ファイルがある場合のみ）
        qd_df = None
        if filepath_qd is not None:
            try:
                qd_df = readfile_qudo.read_qudo(game_id, filepath_qd)
            except Exception as e:
                st.warning(f"QUDOファイルの読み込みに失敗しました: {e}")

            st.write(f"Qudoデータ: {qd_df.shape}")

        # ファイル同士を結合
        df_gamedata = pd.merge(
            ikkyu_df,
            qd_df,
            left_on=[
                "inning",
                "top_bottom",
                "pa_of_inning",
                "pitches_of_pa",
                "game_id",
            ],
            right_on=[
                "inning",
                "top_bottom",
                "pa_of_inning",
                "pitches_of_pa",
                "game_id",
            ],
            how="left",
        ).reset_index(drop=True)

        # Check if merge changed the number of rows
        if len(df_gamedata) != len(ikkyu_df):
            st.warning(f"警告: マージ後の行数が変更されました。元の行数: {len(ikkyu_df)}, マージ後の行数: {len(df_gamedata)}")

        df_gamedata["timestamp"] = df_gamedata["timestamp"].replace(
            "窶ｯ", " ", regex=True
        )
        df_gamedata = add_video_url.add_video_url(
            df_gamedata, youtube_id, start_timestamp
        )
        st.write(f"Youtube タイムスタンプ: {df_gamedata.shape}")
        
        # Check if adding video URLs changed the number of rows
        if len(df_gamedata) != len(ikkyu_df):
            st.warning(f"警告: タイムスタンプ追加後の行数が変更されました。元の行数: {len(ikkyu_df)}, 現在の行数: {len(df_gamedata)}")

        return df_gamedata


    except Exception as e:
        st.error(f"データのマージ中にエラーが発生しました: {e}")
        return None


def main():
    st.title("Ikkyu-QoDO")

    # 入力セクション
    col1, col2 = st.columns(2)

    with col1:
        # ゲームID入力
        game_id = st.text_input("試合IDを入力", placeholder="例: 2024112803")

    with col2:
        # YouTubeビデオID入力
        youtube_id = st.text_input("YouTubeビデオID", placeholder="例: dQw4w9WgXcQ")

    # タイムスタンプ入力
    start_timestamp = st.text_input(
        "開始タイムスタンプ",
        placeholder="例: 123",
        help="動画の開始時間を秒数で入力してください",
    )
    if start_timestamp != "":
        start_timestamp = int(start_timestamp)

    # ファイルアップロード
    col3, col4 = st.columns(2)

    with col3:
        # 一球速報ファイルアップロード
        ikkyu_file = st.file_uploader("一球速報のCSVファイル", type=["csv"])

    with col4:
        # Qudoファイルアップロード
        qudo_file = st.file_uploader("Qudoのデータファイル", type=["csv"])

    # マージボタン
    if st.button("データを結合する"):
        # 入力バリデーション
        if not all([game_id, youtube_id, start_timestamp, ikkyu_file, qudo_file]):
            st.warning("すべての情報を入力してください。")
            return

    # 一時ファイルパスの作成
        temp_ikkyu_path = f"temp_{ikkyu_file.name}"
        temp_qudo_path = f"temp_{qudo_file.name}"

        try:
            # 一時ファイルに保存
            with open(temp_ikkyu_path, "wb") as f:
                f.write(ikkyu_file.getbuffer())

            with open(temp_qudo_path, "wb") as f:
                f.write(qudo_file.getbuffer())

            # データのマージ
            with st.spinner("データをマージしています..."):
                merged_df = merge_game_data(
                    game_id,
                    temp_ikkyu_path,
                    temp_qudo_path,
                    youtube_id,
                    start_timestamp,
                )

            if merged_df is not None:
                st.success(f"データマージが完了しました。行数: {len(merged_df)}")

                # 最初の数行を表示
                st.write("### マージされたデータの最初の10行")
                st.dataframe(merged_df.head(10))

                # CSVとして保存するオプション
                output_path = f"Output/{game_id}_gamedata_jwl.csv"
                os.makedirs("Output", exist_ok=True)
                merged_df.to_csv(output_path, encoding="UTF-8", index=False)

                # ファイルを開かずにダイレクトにダウンロードボタンを作成
                st.download_button(
                    label="紐付けされたデータをダウンロード",
                    data=merged_df.to_csv(index=False, encoding="UTF-8"),
                    file_name=f"{game_id}_gamedata_jwl.csv",
                    mime="text/csv"
                    )


        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

        finally:
            # 一時ファイルの削除
            if os.path.exists(temp_ikkyu_path):
                os.remove(temp_ikkyu_path)
            if os.path.exists(temp_qudo_path):
                os.remove(temp_qudo_path)


if __name__ == "__main__":
    main()
