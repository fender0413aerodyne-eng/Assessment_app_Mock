# initialize.py
# -------------------------------------------------------------------
# 役割:
# - 環境変数/Secrets の読み込み（dotenv は任意依存）
# - OpenAI クライアントの生成（堅牢化: キー形式検証・依存不整合の検知）
# - ベースのスタイル（ライト/ダーク切替対応CSS）の注入
# -------------------------------------------------------------------

import os
import streamlit as st
from openai import OpenAI

# --- dotenv を任意依存にする（未インストールでも起動継続） ---
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    def load_dotenv(*args, **kwargs):
        return False


def load_env() -> None:
    """
    ローカル: .env を読み込む（失敗しても無視）
    本番（Streamlit Cloud）: st.secrets の OPENAI_API_KEY を最優先で環境変数に注入
    """
    try:
        load_dotenv(override=False)
    except Exception:
        # dotenv が無くても続行
        pass

    # Streamlit Secrets を最優先
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = str(st.secrets["OPENAI_API_KEY"])


def get_client() -> OpenAI:
    """
    OpenAI クライアントを初期化して返す。
    - APIキーの存在/型/書式（"sk-"）を検証
    - 依存不整合（httpx/httpcore）を検知したらわかりやすいメッセージを出す
    """
    api_key = os.getenv("OPENAI_API_KEY", "")

    # TOML誤設定や型崩れ（配列/数値など）を検知
    if not isinstance(api_key, str) or not api_key.strip().startswith("sk-"):
        st.error(
            "OpenAI APIキーが見つからないか不正です。Streamlitの Secrets に "
            '`OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"` を設定してください。'
        )
        st.stop()

    try:
        return OpenAI(api_key=api_key.strip())
    except TypeError:
        # 依存の不整合（httpx/httpcore）で起きやすい
        st.error(
            "OpenAI クライアント初期化に失敗しました。依存関係の不整合の可能性があります。\n\n"
            "対処: `requirements.txt` に以下を固定し、アプリを再起動してください。\n"
            "- openai==1.51.0\n- httpx==0.27.2\n- httpcore==0.17.3\n"
        )
        st.stop()


def inject_base_styles() -> None:
    """
    アプリ全体のベースCSSを注入。
    - 医療系ティール/ブルー基調
    - ダークモード風切替: .theme-toggle[data-dark="true"] をトリガーに変数を上書き
    - カード/テーブル/タグ/アニメーション等のユーティリティ
    """
    st.markdown(
        """
<style>
  :root{
    --primary:#0ea5a4; /* teal-ish medical */
    --accent:#2563eb;
    --warn:#d97706;
    --error:#dc2626;
    --card-bg:#ffffff;
    --text:#111827;
    --muted:#6b7280;
    --border:#e5e7eb;
  }
  /* ダーク切替（.theme-toggle[data-dark="true"] が描画ツリー内にあるとき） */
  .theme-toggle[data-dark="true"] ~ * :root,
  .theme-toggle[data-dark="true"] ~ * {
    --card-bg:#0b1220;
    --text:#f3f4f6;
    --muted:#9ca3af;
    --border:#1f2937;
  }

  .app-title{font-weight:800;font-size:2rem;color:var(--primary);}
  .pill{display:inline-block;padding:.2rem .6rem;border-radius:9999px;background:var(--primary);color:#fff;font-weight:700}
  .card{background:var(--card-bg);border:1px solid var(--border);border-radius:14px;padding:16px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
  .muted{color:var(--muted)}
  .section-title{font-weight:800;border-left:4px solid var(--accent);padding-left:.5rem;margin:1rem 0 .5rem}
  .tag{display:inline-block;border:1px solid var(--border);border-radius:10px;padding:.2rem .5rem;margin-right:.3rem}

  /* 思考中アニメーション（三点リーダ） */
  .thinking{display:inline-block; font-weight:700}
  .thinking::after{
    content:""; display:inline-block; width:1em; text-align:left; animation:dots 1.2s steps(4,end) infinite
  }
  @keyframes dots{0%{content:""}25%{content:"."}50%{content:".."}75%{content:"..."}}

  .ok{color:var(--primary);font-weight:700}
  .warn{color:var(--warn);font-weight:700}
  .error{color:var(--error);font-weight:700}

  table.generated{width:100%; border-collapse:collapse}
  table.generated th, table.generated td{border:1px solid var(--border); padding:.5rem; vertical-align:top}
  table.generated th{background:rgba(37,99,235,0.08)}
</style>
        """,
        unsafe_allow_html=True,
    )
