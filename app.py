import streamlit as st
import pandas as pd
import random

# 1. データの読み込み（エラー対策を追加）
try:
    # on_bad_lines='skip' を入れることで、形式がおかしい行を飛ばして読み込みます
    df = pd.read_csv('final_tango_list.csv', on_bad_lines='skip', engine='python')
except FileNotFoundError:
    st.error("CSVファイル 'final_tango_list.csv' が見つかりません。")
    st.stop()
except Exception as e:
    st.error(f"読み込みエラーが発生しました: {e}")
    st.stop()

st.title("シス単完全カバーの４択マシン")

# --- 以下は前のコードと同じ ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True

if st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    st.subheader(f"第 {st.session_state.idx + 1} 問 / 全 {len(st.session_state.questions)} 問")
    st.write(f"### この単語の意味は？: **{row['question']}**")

    if st.session_state.new_ques:
        # dummy_poolが空の場合の対策を追加
        raw_dummies = str(row['dummy_pool']) if pd.notna(row['dummy_pool']) else ""
        dummies = [d.strip() for d in raw_dummies.split(',') if d.strip()]
        
        # 選択肢が4つに満たない場合の予備ダミー
        while len(dummies) < 3:
            dummies.append("（なし）")
            
        choices = [row['all_answers']] + dummies[:3]
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            if choice == row['all_answers']:
                st.success("✨ 正解！！")
                st.session_state.score += 1
            else:
                st.error(f"❌ 残念！ 正解は「{row['all_answers']}」でした。")
            st.write("---")

    if st.session_state.answered:
        if st.button("次の問題へ"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.rerun()
else:
    st.balloons()
    st.write(f"## 全問終了！正解数: {st.session_state.score} / {len(st.session_state.questions)}")
    if st.button("最初からやり直す"):
        st.session_state.idx = 0
        st.session_state.score = 0
        st.session_state.new_ques = True
        st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
        st.rerun()
