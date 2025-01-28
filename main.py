import streamlit as st
import importlib.util

# ページ幅を最大化
st.set_page_config(layout="wide")

# ファイルパスの指定
IDOL_LIST_FILE = "idol-list.csv"
SKILL_INFO_FILE = "skill_info.csv"
IDOL_NAME_FILE = "idol_name.csv"
IDEAL_TEAM_FILE = "ideal_team.csv"  # ideal_team.csv の追加

# タブ設定
tab1, tab2 = st.tabs(["アイドル管理システム", "理想編成アプリ"])

# タブ1: アイドル管理システム
with tab1:
    spec_idol = importlib.util.spec_from_file_location("idol_skill", "idol_skill.py")
    idol_skill = importlib.util.module_from_spec(spec_idol)
    spec_idol.loader.exec_module(idol_skill)

    # アイドル管理システムの関数を呼び出し
    idol_skill.idol_skill_app(IDOL_LIST_FILE, SKILL_INFO_FILE, IDOL_NAME_FILE)

# タブ2: 理想編成アプリ
with tab2:
    spec_ideal = importlib.util.spec_from_file_location("ideal_team", "ideal_team.py")
    ideal_team = importlib.util.module_from_spec(spec_ideal)
    spec_ideal.loader.exec_module(ideal_team)

    # 理想編成アプリの関数を呼び出し
    ideal_team.ideal_team_app(IDOL_LIST_FILE, IDEAL_TEAM_FILE)  # ideal_team.csv を渡す
