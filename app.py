import streamlit as st
import pandas as pd
import random

# --- 1. データの読み込み ---
try:
    # 新しく作ったCSVファイルを読み込む（文字化け対策込み）
    df = pd.read_csv('final_tango_list.csv', on_bad_lines='skip', engine='python', encoding='utf-8-sig')
except FileNotFoundError:
    st.error("CSVファイル 'final_tango_list.csv' が見つかりません。")
    st.stop()

# --- 2. 画面設定 ---
st.set_page_config(page_title="英単語 文脈攻略マシン", layout="centered")
st.title("📘 シス単が手元にないときに使うやつ")

# --- 3. サイドバー設定（レベルはCSVの'level'列で判定） ---
st.sidebar.header("学習設定")
unique_levels = df['level'].unique().tolist() if 'level' in df.columns else ["Fundamental (1-600)"]
level = st.sidebar.selectbox("レベルを選択してください", unique_levels)

# データのフィルタリング
current_df = df[df['level'] == level] if 'level' in df.columns else df

# セッション状態の初期化
if 'last_level' not in st.session_state or st.session_state.last_level != level:
    st.session_state.last_level = level
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.questions = current_df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True
    st.session_state.answered = False

# --- 4. クイズ本編 ---
if len(st.session_state.questions) == 0:
    st.warning("このレベルには単語が含まれていません。CSVを確認してください。")
elif st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    
    st.progress((st.session_state.idx + 1) / len(st.session_state.questions))
    st.caption(f"進捗: {st.session_state.idx + 1} / {len(st.session_state.questions)}")

    st.write("### 下の文の赤字単語の意味は？")
    
    sentence = str(row['sentence']) if 'sentence' in row and pd.notna(row['sentence']) else ""
    target = str(row['question'])
    
    # 例文ハイライト表示
    if target in sentence:
        highlighted = sentence.replace(target, f'<span style="color:red; font-weight:bold; border-bottom:2px solid red;">{target}</span>')
    else:
        highlighted = f'<span style="color:red; font-weight:bold;">{target}</span>'

    st.markdown(f"""
        <div style="background-color:#f9f9f9; padding:20px; border-radius:15px; border-left:10px solid red; margin-bottom:20px;">
            <p style="font-size:24px; line-height:1.6; color:#333;">{highlighted}</p>
        </div>
    """, unsafe_allow_html=True)

    # 選択肢作成
    if st.session_state.new_ques:
        raw_dummies = str(row['dummy_pool']) if 'dummy_pool' in row and pd.notna(row['dummy_pool']) else ""
        dummies = [d.strip() for d in raw_dummies.split(',') if d.strip()]
        choices = [str(row['all_answers'])] + dummies[:3]
        while len(choices) < 4: choices.append("（なし）")
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    # 回答ボタン
    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            if choice == str(row['all_answers']):
                st.session_state.last_result = "correct"
                st.session_state.score += 1
            else:
                st.session_state.last_result = "incorrect"

    # 回答後の表示
    if st.session_state.answered:
        if st.session_state.last_result == "correct":
            st.success("✨ **正解！**")
        else:
            st.error(f"❌ **不正解...** 正解は「 **{row['all_answers']}** 」でした。")
        
        with st.expander("📖 詳しい解説・訳を見る", expanded=True):
            st.write(f"**【和訳】**\n{row['translation'] if 'translation' in row else ''}")
            if 'exam_info' in row:
                st.info(f"🎓 **出題実績:** {row['exam_info']}")

        if st.button("次の問題へ 👉", type="primary"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.rerun()
else:
    st.balloons()
    st.write("## セクション完了！")
    st.button("最初から解く", on_click=lambda: st.session_state.clear())
