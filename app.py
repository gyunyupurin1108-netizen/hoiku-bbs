import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

st.set_page_config(page_title="保育士掲示板", layout="centered")
st.title("☕ ほっと一息 掲示板")
st.sidebar.link_button("📝 書類作成に戻る", "https://hoiku-shido-keikaku-atiia9c6wehijrtmcptgpr.streamlit.app")

# --- 1. スプレッドシートへの接続 ---
# Secretsに書いた情報を使って接続します
conn = st.connection("gsheets", type=GSheetsConnection)

# データを読み込む（キャッシュを使わないようにttl=0を設定）
df = conn.read(ttl=0)

# --- 2. 投稿フォーム ---
# --- 2. 投稿フォーム ---
with st.form(key="bbs_form"):
    name = st.text_input("ニックネーム")
    
    # ▼▼ 追加①：パスワード入力欄 ▼▼
    admin_pass = st.text_input("管理者パスワード（※管理人のみ入力）", type="password")
    
    message = st.text_area("メッセージ")
    submit = st.form_submit_button("投稿する")

    if submit:
        if not name or not message:
            st.error("名前とメッセージを入力してください")
            
        # ▼▼ 追加②：名前が「管理人」で、かつパスワードが間違っている場合 ▼▼
        elif name == "管理人" and admin_pass != "yktk591108": # ← "hoiku2026"を好きなパスワードに変えてください
            st.error("🚨 パスワードが違います。管理人以外は『管理人』という名前を使えません。")
            
        else:
            # 現在時刻
            now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
            
            # 新しいデータをデータフレームに追加
            new_data = pd.DataFrame(
                [{"date": now, "name": name, "message": message}]
            )
            
            # 既存のデータと結合
            updated_df = pd.concat([new_data, df], ignore_index=True)
            
            # スプレッドシートを更新（書き込み）
            conn.update(data=updated_df)
            
            st.success("投稿しました！")
            # 画面をリロードして投稿を表示させる
            st.rerun()
            
           
# --- 3. 投稿一覧の表示 ---
st.divider()
st.subheader("みんなの声")

# データがない場合の処理
if df.empty:
    st.info("まだ投稿はありません。")
else:
    # 新しい順（上から順）に表示したい場合
    for index, row in df.iterrows():
        with st.chat_message("user"):
            st.write(f"**{row['name']}** ({row['date']})")
            st.write(row['message'])
