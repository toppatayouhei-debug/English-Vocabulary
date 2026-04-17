import streamlit as st
import pandas as pd
import random

# 1. データの読み込み（ファイル名を先ほど作成したものに変更）
try:
    df = pd.read_csv('final_tango_list.csv')
except FileNotFoundError:
    st.error("CSVファイル 'final_tango_list.csv' が見つかりません。プログラムと同じフォルダに置いてください。")
    st.stop()

st.title("シス単全レベル完全カバーの４択アプリ")

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
        # 修正：dummy_pool（カンマ区切りの文字列）をリストに分割
        dummies = [d.strip() for d in str(row['dummy_pool']).split(',')]
        
        # 正解とダミー3つを合わせる（もしダミーが足りない場合も考慮）
        choices = [row['all_answers']] + dummies[:3]
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    # 4択ボタン
    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            if choice == row['all_answers']:
                st.success("✨ 正解！！")
                st.session_state.score += 1
            else:
                st.error(f"❌ 残念！ 正解は「{row['all_answers']}」でした。")
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
        st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
        st.rerun()
