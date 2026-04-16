import streamlit as st
import pandas as pd
import random

# データの読み込み
df = pd.read_csv('english.csv')

st.title("🔤 英単語4択マスター")

# セッション状態の初期化
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True

# クイズ中
if st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    
    st.subheader(f"第 {st.session_state.idx + 1} 問 / 全 {len(st.session_state.questions)} 問")
    st.write(f"### この単語の意味は？: **{row['question']}**")

    # 選択肢の作成とシャッフル
    if st.session_state.new_ques:
        choices = [row['answer'], row['dummy1'], row['dummy2'], row['dummy3']]
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    # 4択ボタン
    for choice in st.session_state.shuffled_choices:
        # すでに回答した後はボタンを押せなくする
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            if choice == row['answer']:
                st.success("✨ 正解！！")
                st.session_state.score += 1
            else:
                st.error(f"❌ 残念！ 正解は「{row['answer']}」でした。")
            st.write("---")

    # 回答した後に「次へ」ボタンを出す
    if st.session_state.answered:
        if st.button("次の問題へ"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.rerun()

# 全問終了
else:
    st.balloons()
    st.write(f"## 全問終了！正解数: {st.session_state.score} / {len(st.session_state.questions)}")
    if st.button("最初からやり直す"):
        st.session_state.idx = 0
        st.session_state.score = 0
        st.session_state.new_ques = True
        st.rerun()
