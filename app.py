import streamlit as st
import pandas as pd
import random

# 1. データの読み込み
try:
    df = pd.read_csv('final_tango_list.csv', on_bad_lines='skip', engine='python')
except FileNotFoundError:
    st.error("CSVファイル 'final_tango_list.csv' が見つかりません。")
    st.stop()

st.title("シス単完全カバーの４択マシン")

# --- サイドバーでレベル選択 ---
st.sidebar.header("設定")
level = st.sidebar.selectbox(
    "レベルを選択してください",
    ["Fundamental (1-600)", "Essential (601-1200)", "Advanced (1201-1800)", "Final (1801-2027)", "All Words (1-2027)"]
)

# 選択されたレベルに応じてデータをフィルタリング (Pythonのindexは0から始まるので-1調整)
if level == "Fundamental (1-600)":
    current_df = df.iloc[0:600]
elif level == "Essential (601-1200)":
    current_df = df.iloc[600:1200]
elif level == "Advanced (1201-1800)":
    current_df = df.iloc[1200:1800]
elif level == "Final (1801-2027)":
    current_df = df.iloc[1800:]
else:
    current_df = df

# レベルが変更されたらリセット
if 'last_level' not in st.session_state or st.session_state.last_level != level:
    st.session_state.last_level = level
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.questions = current_df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True

# --- クイズ本編 ---
if len(st.session_state.questions) == 0:
    st.warning("このレベルには単語が含まれていません。CSVを確認してください。")
elif st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    
    st.subheader(f"Level: {level.split(' ')[0]}") # 表示をスッキリ
    st.info(f"第 {st.session_state.idx + 1} 問 / 全 {len(st.session_state.questions)} 問")
    st.write(f"### この単語の意味は？: **{row['question']}**")

    if st.session_state.new_ques:
        # dummy_poolの分解と整形
        raw_dummies = str(row['dummy_pool']) if pd.notna(row['dummy_pool']) else ""
        dummies = [d.strip() for d in raw_dummies.split(',') if d.strip()]
        
        # 選択肢の構築
        choices = [row['all_answers']] + dummies[:3]
        while len(choices) < 4:
            choices.append("（なし）")
            
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    # 回答ボタンの作成
    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            if choice == row['all_answers']:
                st.success("✨ 正解！！")
                st.session_state.score += 1
            else:
                st.error(f"❌ 残念！ 正解は「{row['all_answers']}」でした。")
            st.write("---")

    # 回答後のアクション
    if st.session_state.answered:
        if st.button("次の問題へ"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.rerun()

else:
    st.balloons()
    st.write(f"## {level.split(' ')[0]} 完了！")
    st.write(f"### 正解数: {st.session_state.score} / {len(st.session_state.questions)}")
    if st.button("もう一度最初から解く"):
        st.session_state.idx = 0
        st.session_state.score = 0
        st.session_state.new_ques = True
        st.session_state.questions = current_df.sample(frac=1).reset_index(drop=True)
        st.rerun()
