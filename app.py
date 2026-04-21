import streamlit as st
import pandas as pd
import random
import re

# --- 1. データの読み込み ---
@st.cache_data
def load_data():
    try:
        # UTF-8 (BOM付き) で読み込み、エラー行はスキップ
        df = pd.read_csv('final_tango_list.csv', on_bad_lines='skip', engine='python', encoding='utf-8-sig')
        return df
    except FileNotFoundError:
        return None

df = load_data()

# --- 2. 画面設定 ---
st.set_page_config(page_title="英単語 文脈攻略マシン", layout="centered")

# 行間を広くして読みやすくするカスタムCSS
st.markdown("""
    <style>
    .stMarkdown p { line-height: 1.8; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📘 シス単が手元にないときに使うやつ")

if df is None:
    st.error("⚠️ CSVファイル 'final_tango_list.csv' が見つかりません。プログラムと同じフォルダに配置してください。")
    st.stop()

# --- 3. サイドバー設定（Allモード追加） ---
st.sidebar.header("⚙️ 学習設定")

unique_levels = df['level'].unique().tolist() if 'level' in df.columns else []
level_options = ["All (1-2027)"] + unique_levels
level = st.sidebar.selectbox("レベルを選択してください", level_options)

# データのフィルタリング
if level == "All (1-2027)":
    current_df = df
else:
    current_df = df[df['level'] == level]

# セッション状態の初期化
if 'last_level' not in st.session_state or st.session_state.last_level != level:
    st.session_state.last_level = level
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.questions = current_df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True
    st.session_state.answered = False

# サイドバーに現在の進捗を表示
st.sidebar.divider()
st.sidebar.write(f"**選択中:** {level}")
st.sidebar.write(f"**問題数:** {len(st.session_state.questions)}問")
if st.session_state.idx > 0:
    accuracy = (st.session_state.score / st.session_state.idx) * 100
    st.sidebar.metric("正答率", f"{accuracy:.1f}%")

# --- 4. クイズ本編 ---
if len(st.session_state.questions) == 0:
    st.warning("このレベルには単語が含まれていません。CSVを確認してください。")
elif st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    
    st.progress((st.session_state.idx + 1) / len(st.session_state.questions))
    st.caption(f"進捗: {st.session_state.idx + 1} / {len(st.session_state.questions)}")

    st.write("### 下の文の赤字単語の意味は？")
    
    sentence = str(row['sentence']) if pd.notna(row.get('sentence')) else ""
    target = str(row['question'])
    
    # 例文ハイライト表示（大文字小文字を区別せずに置換）
    pattern = re.compile(re.escape(target), re.IGNORECASE)
    highlighted = pattern.sub(f'<span style="color:red; font-weight:bold; border-bottom:2px solid red;">{target}</span>', sentence)

    st.markdown(f"""
        <div style="background-color:#f9f9f9; padding:25px; border-radius:15px; border-left:10px solid red; margin-bottom:20px;">
            <p style="font-size:22px; color:#333;">{highlighted}</p>
        </div>
    """, unsafe_allow_html=True)

    # 選択肢作成
    if st.session_state.new_ques:
        raw_dummies = str(row['dummy_pool']) if pd.notna(row.get('dummy_pool')) else ""
        dummies = [d.strip() for d in raw_dummies.split(',') if d.strip()]
        
        # 正解とダミーを混ぜる（最大4択）
        choices = [str(row['all_answers'])] + dummies[:3]
        while len(choices) < 4:
            choices.append("---")
        random.shuffle(choices)
        
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    # 回答ボタンの生成
    cols = st.columns(1)
    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            if choice == str(row['all_answers']):
                st.session_state.last_result = "correct"
                st.session_state.score += 1
            else:
                st.session_state.last_result = "incorrect"
            st.rerun()

    # 回答後の表示
    if st.session_state.answered:
        if st.session_state.last_result == "correct":
            st.success("✨ **正解！**")
        else:
            st.error(f"❌ **不正解...** 正解は「 **{row['all_answers']}** 」でした。")
        
        with st.expander("📖 詳しい解説・訳を見る", expanded=True):
            st.write(f"**【和訳】**\n{row['translation'] if pd.notna(row.get('translation')) else '訳が登録されていません。'}")
            if pd.notna(row.get('exam_info')):
                st.info(f"🎓 **出題実績:** {row['exam_info']}")

        if st.button("次の問題へ 👉", type="primary"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.session_state.answered = False
            st.rerun()
else:
    st.balloons()
    st.write("## 🎊 セクション完了！")
    st.write(f"最終スコア: {st.session_state.score} / {len(st.session_state.questions)}")
    if st.button("もう一度最初から解く", type="primary"):
        st.session_state.idx = 0
        st.session_state.score = 0
        st.session_state.questions = current_df.sample(frac=1).reset_index(drop=True)
        st.session_state.new_ques = True
        st.session_state.answered = False
        st.rerun()
