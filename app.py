import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import streamlit.components.v1 as components

# --- 1. 広告コードの準備 ---
# サイドバー用（はらぺこあおむしなど）
ad_sidebar = """<table border="0" cellpadding="0" cellspacing="0"><tr><td><div style="border:1px solid #95A5A6;border-radius:.75rem;background-color:#FFFFFF;width:280px;margin:0px;padding:5px;text-align:center;overflow:hidden;"><table><tr><td style="width:128px"><a href="https://hb.afl.rakuten.co.jp/ichiba/13f1038a.0b9b3333.13f1038b.1111a3c1/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fbook%2F768643%2F&link_type=picttext&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0dGV4dCIsInNpemUiOiIxMjh4MTI4IiwibmFtIjoxLCJuYW1wIjoicmlnaHQiLCJjb20iOjEsImNvbXAiOiJkb3duIiwicHJpY2UiOjEsImJvciI6MSwiY29sIjoxLCJiYnRuIjoxLCJwcm9kIjowLCJhbXAiOmZhbHNlfQ%3D%3D" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://hbb.afl.rakuten.co.jp/hgb/13f1038a.0b9b3333.13f1038b.1111a3c1/?me_id=1213310&item_id=10547021&pc=https%3A%2F%2Fthumbnail.image.rakuten.co.jp%2F%400_mall%2Fbook%2Fcabinet%2F9516%2F9784062619516.jpg%3F_ex%3D128x128&s=128x128&t=picttext" border="0" style="margin:2px" alt="[商品価格に関しましては、リンクが作成された時点と現時点で情報が変更されている場合がございます。]" title="[商品価格に関しましては、リンクが作成された時点と現時点で情報が変更されている場合がございます。]"></a></td><td style="vertical-align:top;width:136px;display: block;"><p style="font-size:12px;line-height:1.4em;text-align:left;margin:0px;padding:2px 6px;word-wrap:break-word"><a href="https://hb.afl.rakuten.co.jp/ichiba/13f1038a.0b9b3333.13f1038b.1111a3c1/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fbook%2F768643%2F&link_type=picttext&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0dGV4dCIsInNpemUiOiIxMjh4MTI4IiwibmFtIjoxLCJuYW1wIjoicmlnaHQiLCJjb20iOjEsImNvbXAiOiJkb3duIiwicHJpY2UiOjEsImJvciI6MSwiY29sIjoxLCJiYnRuIjoxLCJwcm9kIjowLCJhbXAiOmZhbHNlfQ%3D%3D" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;">にじいろのさかな （にじいろのさかなブック　世界の絵本（新）） [ マーカス・フィスター ]</a><br><span >価格：1,980円（税込、送料無料)</span> <span style="color:#BBB">(2026/4/5時点)</span></p></td></tr></table></div><br><p style="color:#000000;font-size:12px;line-height:1.4em;margin:5px;word-wrap:break-word"></p></td></tr></table>"""

# メイン画面上部用（エプロンや新作絵本など）
ad_main_top = """（別の楽天のコード：widthを100%に書き換えたもの）"""

# ★ メイン画面上部の広告
with st.container():
    st.caption("PR: 【新年度】読み聞かせに迷ったら")
    components.html(ad_main_top, height=250)

st.divider()

st.set_page_config(page_title="保育士掲示板", layout="centered")
st.title("☕ ほっと一息 掲示板")



# --- 2. サイドバーの表示 ---
with st.sidebar:
    st.header("⚙️ 設定・お知らせ")
    
    # サイドバー広告
    st.caption("PR: 先生におすすめのアイテム")
    components.html(ad_sidebar, height=300)
    
    st.divider()
    st.link_button("📝 書類作成に戻る", "https://hoiku-shido-keikaku-snpsbrrtescryaamjootdg.streamlit.app/")
    # ここに既存の「設定項目」などがあれば続ける

# --- 1. スプレッドシートへの接続 ---
# Secretsに書いた情報を使って接続します
conn = st.connection("gsheets", type=GSheetsConnection)

# データを読み込む（キャッシュを使わないようにttl=0を設定）
df = conn.read(ttl=0)

# --- 2. 投稿フォーム ---
# clear_on_submit=True を追加することで、投稿後に中身を自動で消去します
with st.form(key="bbs_form", clear_on_submit=True):
    name = st.text_input("ニックネーム")
    admin_pass = st.text_input("管理者パスワード（※管理人のみ入力）", type="password")
    message = st.text_area("メッセージ")
    submit = st.form_submit_button("投稿する")

    if submit:
        if not name or not message:
            st.error("名前とメッセージを入力してください")
        elif name == "管理人" and admin_pass != "yktk591108":
            st.error("🚨 パスワードが違います。管理人以外は『管理人』という名前を使えません。")
        else:
            # --- 日本時間（JST）を取得する処理 ---
            # UTC（世界標準時）に9時間を加算して日本時間にします
            t_delta = datetime.timedelta(hours=9)
            JST = datetime.timezone(t_delta, 'JST')
            now = datetime.datetime.now(JST).strftime("%Y/%m/%d %H:%M")
            
            # 新しいデータをデータフレームに追加
            new_data = pd.DataFrame(
                [{"date": now, "name": name, "message": message}]
            )
            
            # 既存のデータと結合
            updated_df = pd.concat([new_data, df], ignore_index=True)
            
            # スプレッドシートを更新
            conn.update(data=updated_df)
            
            st.success("投稿しました！")
            # 画面をリロードして最新の投稿を表示させる
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
