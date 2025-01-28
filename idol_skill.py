import os
import pandas as pd
import streamlit as st


def idol_skill_app(idol_list_path, skill_info_path):
    # CSVファイルの読み込み
    if not idol_list_path or not skill_info_path:
        st.error("ファイルパスが指定されていません！")
        return

    try:
        df = pd.read_csv(idol_list_path, encoding="shift_jis")
        skill_info_df = pd.read_csv(skill_info_path, encoding="shift_jis")
    except FileNotFoundError as e:
        st.error(f"{e.filename} が見つかりません！")
        return

    # Streamlitアプリタイトル
    st.title("アイドル管理システム")

    # フィルタリングセクション
    st.subheader("絞り込み条件を選択してください")
    col1, col2 = st.columns(2)
    with col1:
        selected_skills = st.multiselect(
            "スキルで絞り込む", options=df["スキル"].unique(), default=[]
        )
        selected_categories = st.multiselect(
            "スキル分類で絞り込む",
            options=sorted(
                set(
                    category
                    for categories in skill_info_df["スキル分類"].dropna()
                    for category in categories.split(",")
                )
            ),
            default=[],
        )
    with col2:
        selected_seconds = st.multiselect(
            "秒数で絞り込む", options=sorted(df["秒数"].unique()), default=[]
        )

    # フィルタリング処理
    filtered_df = df.copy()

    # スキル分類でのフィルタリング
    if selected_categories:
        valid_skills = skill_info_df[
            skill_info_df["スキル分類"].str.contains(
                "|".join(selected_categories), na=False
            )
        ]["スキル"]
        filtered_df = filtered_df[filtered_df["スキル"].isin(valid_skills)]

    if selected_skills:
        filtered_df = filtered_df[filtered_df["スキル"].isin(selected_skills)]

    if selected_seconds:
        filtered_df = filtered_df[filtered_df["秒数"].isin(selected_seconds)]

    # 属性の表示順を設定
    attribute_order = {"Cu": 0, "Co": 1, "Pa": 2}
    filtered_df["属性順"] = filtered_df["属性"].map(attribute_order)

    # デフォルトの特化列名
    default_columns = ["ボーカル", "ダンス", "ビジュアル"]
    default_colors = {
        "ボーカル": "#ffe4e1",
        "ダンス": "#add8e6",
        "ビジュアル": "#ffffe0",
    }

    # 特化ステータス例外
    custom_vertical_axes = {
        "ドミナント・ハーモニー": [
            "ボーカル&ダンス",
            "ダンス&ビジュアル",
            "ビジュアル&ボーカル",
        ],
        "ミューチャル": ["ボーカル&ダンス", "ダンス&ビジュアル", "ビジュアル&ボーカル"],
    }

    # 確率の並び順
    probability_order = {"低": 0, "中": 1, "高": 2}

    # スキルごとにテーブルを表示
    for skill in filtered_df["スキル"].unique():
        st.markdown(f"### スキル: {skill}")

        # スキル詳細を取得
        skill_detail = skill_info_df.loc[
            skill_info_df["スキル"] == skill, "スキル詳細"
        ].values
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
            key=lambda x: (int(x[:-1]), probability_order.get(x[-1], 0)),
        )

        if not skill_df.empty:
            # 特化ラベルを一度だけ表示
            st.markdown(
                f"<div style='display: flex; justify-content: space-around; padding: 10px; background-color: #f5f5f5; border-radius: 5px;'>"
                + "".join(
                    [
                        f"<div style='background-color: {default_colors.get(col, '#ffffff')}; padding: 5px; text-align: center;'>{col}</div>"
                        for col in columns
                    ]
                )
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
                        idols = skill_df[
                            (skill_df["秒数確率"] == sec_prob)
                            & (skill_df["特化"] == col_name)
                        ]
                        if not idols.empty:
                            idols = idols.sort_values(by="属性順")  # 属性順でソート
                            for _, row in idols.iterrows():
                                # 画像を確実に表示
                                image_path = row["画像パス"]
                                if os.path.exists(image_path):
                                    st.image(
                                        image_path, width=100, use_container_width=False
                                    )

                                    # アイドル名を独立したテキスト要素で表示（改行をサポート）
                                    st.markdown(
                                        f"""
                                        <p style="text-align: left; margin: 0;">
                                            {row["アイドル名"].replace("<br>", "<br />")}
                                        </p>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                                else:
                                    st.error(f"画像が見つかりません: {image_path}")

                                # 詳細情報を表示
                                with st.expander("詳細"):
                                    st.write(f"**属性**: {row['属性']}")
                                    st.write(f"**特化**: {row['特化']}")
                                    st.write(f"**秒数**: {row['秒数']} 秒")
                                    st.write(f"**確率**: {row['確率']}")
                                    st.write(f"**スキル**: {row['スキル']}")
                                    st.write(f"**センター効果**: {row['センター効果']}")
                                    st.write(f"**Vo**: {row['Vo']}")
                                    st.write(f"**Da**: {row['Da']}")
                                    st.write(f"**Vi**: {row['Vi']}")
                                    st.write(
                                        f"**メモリアルガシャ**: {row['メモリアルガシャ'] if pd.notna(row['メモリアルガシャ']) else 'データなし'}"
                                    )
                                    if skill == "ドミナント・ハーモニー":
                                        st.write(f"**副属性**: {row['副属性']}")
                                        st.write(f"**ドミナント**: {row['ドミナント']}")
