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

    # アイドル名の五十音順に基づくソート順を生成
    sorted_idol_names = idol_name_df["アイドル名"].dropna().tolist()

    # Streamlitアプリタイトル
    st.title("アイドル管理システム")

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
        selected_idol_names = st.multiselect(
            "アイドル名で絞り込む",
            options=[name for name in sorted_idol_names if name in df["アイドル名"].unique()],
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

    if selected_idol_names:
        filtered_df = filtered_df[filtered_df["アイドル名"].isin(selected_idol_names)]

    # 属性の表示順を設定
    attribute_order = {"Cu": 0, "Co": 1, "Pa": 2}
    filtered_df["属性順"] = filtered_df["属性"].map(attribute_order).fillna(99)

    # デフォルトの特化列名
    default_columns = ["ボーカル", "ダンス", "ビジュアル"]
    default_colors = {"ボーカル": "#ffe4e1", "ダンス": "#add8e6", "ビジュアル": "#ffffe0"}

    # 特化ステータス例外
    custom_vertical_axes = {
        "ドミナント・ハーモニー": ["ボーカル&ダンス", "ダンス&ビジュアル", "ビジュアル&ボーカル"],
        "ミューチャル": ["ボーカル&ダンス", "ダンス&ビジュアル", "ビジュアル&ボーカル"]
    }

    # 確率の並び順
    probability_order = {"低": 0, "中": 1, "高": 2}

    # スキルごとにテーブルを表示
    for skill in filtered_df["スキル"].unique():
        st.markdown(f"### スキル: {skill}")

        # スキル詳細を取得
        skill_detail = skill_info_df.loc[skill_info_df["スキル"] == skill, "スキル詳細"].values
        if len(skill_detail) > 0:
            st.markdown(
                f"<p style='font-size: 20px; font-style: italic; color: gray;'>{skill_detail[0]}</p>",
                unsafe_allow_html=True,
            )

        skill_df = filtered_df[filtered_df["スキル"] == skill].copy()

        # 特化ステータス例外の適用
        columns = custom_vertical_axes.get(skill, default_columns)

        # 秒数確率で並べ替え
        skill_df["秒数確率"] = skill_df["秒数"].astype(str) + skill_df["確率"]
        skill_df["確率ソート"] = skill_df["確率"].map(probability_order)

        seconds_probs = sorted(
            skill_df["秒数確率"].dropna().unique(),
            key=lambda x: (
                int(''.join(ch for ch in x if ch.isdigit())),  # 秒数部分を数値に
                probability_order.get(''.join(ch for ch in x if not ch.isdigit()), 0)  # 低/中/高の並び
            )
        )

        if not skill_df.empty:
            # 特化ラベルを一度だけ表示
            st.markdown(
                f"<div style='display: flex; justify-content: space-around; padding: 10px; background-color: #f5f5f5; border-radius: 5px;'>"
                + "".join([
                    f"<div style='background-color: {default_colors.get(col, '#ffffff')}; padding: 5px; text-align: center;'>{col}</div>"
                    for col in columns
                ])
                + "</div>",
                unsafe_allow_html=True,
            )

            # 秒数ごとにデータを取得し横並び
            for sec_prob in seconds_probs:
                st.markdown(
                    f"""
                    <p style="font-size: 30px; font-weight: bold; color: black; margin: 10px 0;">
                        秒数: {sec_prob}
                    </p>
                    """,
                    unsafe_allow_html=True,
                )
                cols = st.columns(len(columns))
                for i, col_name in enumerate(columns):
                    with cols[i]:
                        # 特化ごとのアイドルを表示
                        idols = skill_df[(skill_df["秒数確率"] == sec_prob) & (skill_df["特化"] == col_name)]
                        if not idols.empty:
                            idols = idols.sort_values(by="属性順")  # 属性順でソート
                            for _, idol in idols.iterrows():
                                # --------------------------------
                                # 1) ローカル画像パスで表示(従来処理)
                                # --------------------------------
                                image_path = idol["画像パス"]
                                if os.path.exists(image_path):
                                    st.image(image_path, width=100, use_container_width=False)

                                    # カード名とアイドル名を表示
                                    st.markdown(
                                        f"""
                                        <div style="text-align: left; margin: 0;">
                                            <!-- カード名 -->
                                            <p style="font-size: 14px; margin: 0;">
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
                                else:
                                    st.error(f"画像が見つかりません: {image_path}")

                                # --------------------------------
                                # 2) 詳細情報 (Expander) 内で
                                #    特訓前URL / 特訓後URL を表示
                                # --------------------------------
                                with st.expander("詳細"):
                                    st.write(f"**属性**: {idol['属性']}")
                                    st.write(f"**特化**: {idol['特化']}")
                                    st.write(f"**秒数**: {idol['秒数']} 秒")
                                    st.write(f"**確率**: {idol['確率']}")
                                    st.write(f"**スキル**: {idol['スキル']}")
                                    st.write(f"**スキル名**: {idol['スキル名']}")
                                    st.write(f"**センター効果**: {idol['センター効果']}")
                                    st.write(f"**Vo**: {idol['Vo']}")
                                    st.write(f"**Da**: {idol['Da']}")
                                    st.write(f"**Vi**: {idol['Vi']}")
                                    st.write(f"**メモリアルガシャ**: {idol['メモリアルガシャ'] if pd.notna(idol['メモリアルガシャ']) else 'データなし'}")

                                    if skill == "ドミナント・ハーモニー":
                                        st.write(f"**副属性**: {idol['副属性']}")
                                        st.write(f"**ドミナント**: {idol['ドミナント']}")

                                    # =========== 追加部分 ===========

                                    # 特訓前URL
                                    tokkun_mae_url = idol.get("特訓前URL", None)
                                    if pd.notna(tokkun_mae_url) and str(tokkun_mae_url).strip():
                                        link_html_mae = f'<a href="{tokkun_mae_url}" target="_blank">特訓前画像URLを開く</a>'
                                        st.markdown(link_html_mae, unsafe_allow_html=True)
                                    else:
                                        st.write("特訓前画像URLは設定されていません")

                                    # 特訓後URL
                                    tokkun_ato_url = idol.get("特訓後URL", None)
                                    if pd.notna(tokkun_ato_url) and str(tokkun_ato_url).strip():
                                        link_html_ato = f'<a href="{tokkun_ato_url}" target="_blank">特訓後画像URLを開く</a>'
                                        st.markdown(link_html_ato, unsafe_allow_html=True)
                                    else:
                                        st.write("特訓後画像URLは設定されていません")

                        else:
                            st.write("該当するアイドルがいません")