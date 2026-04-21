# --- 3. サイドバー設定 ---
st.sidebar.header("学習設定")

# 選択肢のリストを作成
if 'level' in df.columns:
    unique_levels = df['level'].unique().tolist()
    level_options = ["All (1-2027)"] + unique_levels
else:
    level_options = ["All (1-2027)"]

level = st.sidebar.selectbox("レベルを選択してください", level_options)

# データのフィルタリング
if level == "All (1-2027)":
    current_df = df
else:
    current_df = df[df['level'] == level]

# セッション状態の初期化（levelが変わったらリセット）
if 'last_level' not in st.session_state or st.session_state.last_level != level:
    st.session_state.last_level = level
    st.session_state.idx = 0
    st.session_state.score = 0
    # 選択されたレベルからランダムに全問抽出
    st.session_state.questions = current_df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True
    st.session_state.answered = False
