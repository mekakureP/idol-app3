import os
import pandas as pd
import streamlit as st

def idol_skill_app(idol_list_path, skill_info_path, idol_name_path):
    # CSVファイルの読み込み
    if not idol_list_path or not skill_info_path or not idol_name_path:
        st.error("ファイルパスが指定されていません！")
        return

    try:
        df = pd.read_csv(idol_list_path, encoding="shift_jis")
        skill_info_df = pd.read_csv(skill_info_path, encoding="shift_jis")
        idol_name_df = pd.read_csv(idol_name_path, encoding="shift_jis")
    except FileNotFoundError as e:
        st.error(f"{e.filename} が見つかりません！")
        return

    # Streamlitアプリタイトル
    st.title("アイドル管理システム")

    # アイドル名を五十音順に並べ替え
    idol_name_df = idol_name_df.sort_values("あいどるめい")
    idol_name_options = idol_name_df["アイドル名"].tolist()

    # フィルタリングセクション
    st.subheader("絞り込み条件を選択してください")
    col1, col2 = st.columns(2)
    with col1:
        selected_skills = st.multiselect(
            "スキルで絞り込む",
            options=df["スキル"].unique(),
            default=[]
        )
        selected_categories = st.multiselect(
            "スキル分類で絞り込む",
            options=sorted(
                set(category for categories in skill_info_df["スキル分類"].dropna() for category in categories.split(","))
            ),
            default=[]
        )
    with col2:
        selected_seconds = st.multiselect(
            "秒数で絞り込む",
            options=sorted(df["秒数"].unique()),
            default=[]
        )
        selected_idols = st.multiselect(
            "アイドル名で絞り込む",
            options=idol_name_options,
            default=[]
        )

    # フィルタリング処理
    filtered_df = df.copy()

    # スキル分類でのフィルタリング
    if selected_categories:
        valid_skills = skill_info_df[
            skill_info_df["スキル分類"].str.contains("|".join(selected_categories), na=False)
        ]["スキル"]
        filtered_df = filtered_df[filtered_df["スキル"].isin(valid_skills)]

    if selected_skills:
        filtered_df = filtered_df[filtered_df["スキル"].isin(selected_skills)]

    if selected_seconds:
        filtered_df = filtered_df[filtered_df["秒数"].isin(selected_seconds)]

    if selected_idols:
        filtered_df = filtered_df[filtered_df["アイドル名"].isin(selected_idols)]

    # 特化ラベルの設定
    default_columns = ["ボーカル", "ダンス", "ビジュアル"]
    default_colors = {"ボーカル": "#ffe4e1", "ダンス": "#add8e6", "ビジュアル": "#ffffe0"}
    custom_vertical_axes = {
        "ドミナント・ハーモニー": ["ボーカル&ダンス", "ダンス&ビジュアル", "ビジュアル&ボーカル"],
        "ミューチャル": ["ボーカル&ダンス", "ダンス&ビジュアル", "ビジュアル&ボーカル"]
    }

    # スキルごとにテーブルを表示
    for skill in filtered_df["スキル"].unique():
        skill_df = filtered_df[filtered_df["スキル"] == skill]
        if skill_df.empty:
            continue

        st.markdown(f"### スキル: {skill}")

        # スキル詳細を取得
        skill_detail = skill_info_df.loc[skill_info_df["スキル"] == skill, "スキル詳細"].values
        if len(skill_detail) > 0:
            st.markdown(
                f"<p style='font-size: 20px; font-style: italic; color: gray;'>{skill_detail[0]}</p>",
                unsafe_allow_html=True,
            )

        # 特化ステータス例外の適用
        columns = custom_vertical_axes.get(skill, default_columns)

        # 特化ラベルを一度だけ表示
        st.markdown(
            f"<div style='display: flex; justify-content: space-around; padding: 10px; background-color: #f5f5f5; border-radius: 5px;'>"
            + "".join([f"<div style='background-color: {default_colors.get(col, '#ffffff')}; padding: 5px; text-align: center;'>{col}</div>" for col in columns])
            + "</div>",
            unsafe_allow_html=True,
        )

        # 詳細情報を表示
        for _, idol in skill_df.iterrows():
            image_path = idol["画像パス"]
            if os.path.exists(image_path):
                st.image(image_path, width=100, use_container_width=False)

                # カード名とアイドル名を表示
                st.markdown(
                    f"""
                    <div style="text-align: left; margin: 0;">
                        <!-- カード名 -->
                        <p style="font-size: 12px; margin: 0;">
                            {idol["カード名"]}
                        </p>
                        <!-- アイドル名 -->
                        <p style="font-size: 14px; margin: 0;">
                            {idol["アイドル名"]}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # 詳細情報を表示
                with st.expander("詳細"):
                    st.write(f"**属性**: {idol['属性']}")
                    st.write(f"**特化**: {idol['特化']}")
                    st.write(f"**秒数**: {idol['秒数']} 秒")
                    st.write(f"**確率**: {idol['確率']}")
                    st.write(f"**スキル**: {idol['スキル']}")
                    st.write(f"**センター効果**: {idol['センター効果']}")
                    st.write(f"**Vo**: {idol['Vo']}")
                    st.write(f"**Da**: {idol['Da']}")
                    st.write(f"**Vi**: {idol['Vi']}")
                    st.write(f"**メモリアルガシャ**: {idol['メモリアルガシャ'] if pd.notna(idol['メモリアルガシャ']) else 'データなし'}")
                    if skill == "ドミナント・ハーモニー":
                        st.write(f"**副属性**: {idol['副属性']}")
                        st.write(f"**ドミナント**: {idol['ドミナント']}")
            else:
                st.error(f"画像が見つかりません: {image_path}")