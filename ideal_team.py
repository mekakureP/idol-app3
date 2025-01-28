import os
import pandas as pd
import streamlit as st

def ideal_team_app(csv_file, ideal_team_file):
    # CSVファイルの読み込み
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding="shift_jis")
    else:
        st.error("CSVファイルが見つかりません！")
        return

    # 理想編成のCSVファイル読み込み
    if os.path.exists(ideal_team_file):
        ideal_team_df = pd.read_csv(ideal_team_file, encoding="shift_jis")
    else:
        st.error("理想編成CSVファイルが見つかりません！")
        return

    # Streamlitアプリタイトル
    st.title("理想編成アプリ")

    # 楽曲フィルタリングセクション
    st.subheader("対応楽曲で絞り込み")
    selected_songs = st.multiselect(
        "対応楽曲を選択してください",
        options=ideal_team_df["対応楽曲"].unique(),
        default=[]
    )

    # 楽曲フィルタリング処理
    if selected_songs:
        ideal_team_df = ideal_team_df[ideal_team_df["対応楽曲"].isin(selected_songs)]

    # 理想編成ごとに表示
    for _, row in ideal_team_df.iterrows():
        st.markdown(f"### {row['編成名']} ({row['対応楽曲']})")

        # スキルごとの列ラベル設定
        labels = ["センター", "アイドル2", "アイドル3", "アイドル4", "アイドル5", "ゲスト"]
        skills = [
            {"スキル": row["スキル1"], "秒数": row["秒数1"], "特化": row["特化1"], "属性": row["属性1"]},
            {"スキル": row["スキル2"], "秒数": row["秒数2"], "特化": row["特化2"], "属性": row["属性2"]},
            {"スキル": row["スキル3"], "秒数": row["秒数3"], "特化": row["特化3"], "属性": row["属性3"]},
            {"スキル": row["スキル4"], "秒数": row["秒数4"], "特化": row["特化4"], "属性": row["属性4"]},
            {"スキル": row["スキル5"], "秒数": row["秒数5"], "特化": row["特化5"], "属性": row["属性5"]},
            {"スキル": row["ゲストスキル"], "秒数": row["ゲスト秒数"], "特化": row["ゲスト特化"], "属性": row["ゲスト属性"]},
        ]

        # ラベルを表示
        col_labels = st.columns(len(labels))
        for i, label in enumerate(labels):
            with col_labels[i]:
                st.markdown(f"<h4 style='text-align: center;'>{label}</h4>", unsafe_allow_html=True)

        # 各スキルに該当するアイドルを表示
        cols = st.columns(len(skills))
        for i, skill_info in enumerate(skills):
            with cols[i]:
                # スキルを表示（スキル名のみ）
                if skill_info["スキル"]:
                    st.markdown(
                        f"<p style='text-align: left; font-weight: bold; font-size: 8.5px;'>{skill_info['スキル']}</p>",
                        unsafe_allow_html=True
                    )

                # フィルタリング条件を生成
                filtered_df = df.copy()
                filtered_df = filtered_df[filtered_df["スキル"] == skill_info["スキル"]]
                if "," in str(skill_info["秒数"]):
                    valid_seconds = list(map(int, skill_info["秒数"].split(",")))
                    filtered_df = filtered_df[filtered_df["秒数"].isin(valid_seconds)]
                else:
                    filtered_df = filtered_df[filtered_df["秒数"] == int(skill_info["秒数"])]

                if skill_info["属性"] == "全タイプ":
                    filtered_df = filtered_df
                else:
                    filtered_df = filtered_df[filtered_df["属性"] == skill_info["属性"]]

                filtered_df = filtered_df[filtered_df["特化"] == skill_info["特化"]]

                # アイドルを表示（ゲストアイドルは1人のみ、他は縦並び）
                if not filtered_df.empty:
                    if labels[i] == "ゲスト":
                        filtered_df = filtered_df.head(1)  # ゲストアイドルは1人のみ
                    for _, idol in filtered_df.iterrows():
                        image_path = idol["画像パス"]
                        if os.path.exists(image_path):
                            st.image(image_path, width=100, use_container_width=False)

                            # アイドル名と秒数を表示（左寄せで改行対応）
                            st.markdown(
                                f"""
                                <p style="text-align: left; margin: 0; font-size: 8px;">
                                    {idol["アイドル名"].replace("<br>", "<br />")}<br>
                                    <span style="background-color: black; color: white; padding: 2px; margin-top: 4px; display: inline-block;">
                                        {idol["特化"]} / {idol["秒数"]}秒
                                    </span>
                                </p>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.error(f"画像が見つかりません: {image_path}")
                else:
                    st.write("該当するアイドルがいません")

