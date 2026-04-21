import streamlit as st
import pandas as pd
import random

# --- 1. データの読み込み ---
try:
    # 読み込むファイル名は適宜変更してください
    df = pd.read_csv('final_tango_list.csv', on_bad_lines='skip', engine='python')
except FileNotFoundError:
    st.error("CSVファイル 'final_tango_list.csv' が見つかりません。")
    st.stop()

# --- 2. 画面タイトルと設定 ---
st.set_page_config(page_title="英単語 文脈攻略マシン", layout="centered")
st.title("🎓 シス単：例文・文脈攻略マシン")

# --- 3. サイドバーでレベル選択 ---
st.sidebar.header("学習設定")
level_options = ["Fundamental (1-600)", "Essential (601-1200)", "Advanced (1201-1800)", "Final (1801-2027)", "All Words (1-2027)"]
level = st.sidebar.selectbox("レベルを選択してください", level_options)

# フィルタリング処理
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

# レベル変更時のリセット処理
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
    
    # プログレスバー
    progress = (st.session_state.idx + 1) / len(st.session_state.questions)
    st.progress(progress)
    st.caption(f"進捗: {st.session_state.idx + 1} / {len(st.session_state.questions)}")

    # --- 例文の強調表示 ---
    st.write("### 下の文の赤字単語の意味は？")
    
    sentence = str(row['sentence']) if pd.notna(row['sentence']) else ""
    target = str(row['question'])
    
    # 例文の中にターゲット単語があれば赤字でハイライト
    if target in sentence:
        highlighted = sentence.replace(target, f'<span style="color:red; font-weight:bold; border-bottom:2px solid red;">{target}</span>')
    else:
        # 例文がない、またはターゲットが含まれない場合のバックアップ表示
        highlighted = f'<span style="color:red; font-weight:bold;">{target}</span> (例文なし)'

    # HTMLを使って大きく、綺麗に表示
    st.markdown(f"""
        <div style="background-color:#f9f9f9; padding:20px; border-radius:15px; border-left:10px solid red; margin-bottom:20px;">
            <p style="font-size:24px; line-height:1.6; color:#333;">{highlighted}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 選択肢の構築 ---
    if st.session_state.new_ques:
        # ダミーの処理（カンマ区切りの文字列をリスト化）
        raw_dummies = str(row['dummy_pool']) if pd.notna(row['dummy_pool']) else ""
        dummies = [d.strip() for d in raw_dummies.split(',') if d.strip()]
        
        # 正解とダミーを混ぜる
        choices = [str(row['all_answers'])] + dummies[:3]
        while len(choices) < 4:
            choices.append("（なし）")
        
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    # --- 回答ボタン ---
    cols = st.columns(1) # 1列に1ボタンで大きく表示
    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            if choice == str(row['all_answers']):
                st.session_state.last_result = "correct"
                st.session_state.score += 1
            else:
                st.session_state.last_result = "incorrect"

    # --- 回答後の表示 ---
    if st.session_state.answered:
        if st.session_state.last_result == "correct":
            st.success("✨ **正解！** その調子です。")
        else:
            st.error(f"❌ **不正解...** 正解は「 **{row['all_answers']}** 」でした。")
        
        # 解説セクション
        with st.expander("📖 詳しい解説・訳を見る", expanded=True):
            st.write(f"**【和訳】**")
            st.write(f"{row['translation'] if pd.notna(row['translation']) else '和訳データがありません。'}")
            
            if 'exam_info' in row and pd.notna(row['exam_info']):
                st.info(f"🎓 **出題実績:** {row['exam_info']}")

        if st.button("次の問題へ 👉", type="primary"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.rerun()

else:
    # --- 全問終了 ---
    st.balloons()
    st.write(f"## {level.split(' ')[0]} セクション完了！")
    st.metric(label="最終正解率", value=f"{st.session_state.score} / {len(st.session_state.questions)}", 
              delta=f"{int(st.session_state.score/len(st.session_state.questions)*100)}%")
    
    if st.button("もう一度最初から解く"):
        st.session_state.idx = 0
        st.session_state.score = 0
        st.session_state.new_ques = True
        st.rerun()
