import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

def load_env():
    # Local: .env → os.environ / Deploy: Streamlit Secrets
    load_dotenv(override=False)
    if "OPENAI_API_KEY" not in os.environ and "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

def get_client():
    api_key = os.getenv("OPENAI_API_KEY", None)
    if not api_key:
        st.error("OpenAI APIキーが設定されていません。Secrets または .env を確認してください。")
        st.stop()
    return OpenAI(api_key=api_key)

def inject_base_styles():
    # ライトテーマ固定（ダークモード切替なし）
    st.markdown("""
    <style>
      :root{
        --primary:#0ea5a4;   /* teal-ish medical */
        --accent:#2563eb;
        --warn:#d97706;
        --error:#dc2626;
        --card-bg:#ffffff;
        --text:#111827;
        --muted:#6b7280;
        --border:#e5e7eb;
      }
      .app-title{font-weight:800;font-size:2rem;color:var(--primary);}
      .pill{display:inline-block;padding:.2rem .6rem;border-radius:9999px;background:var(--primary);color:#fff;font-weight:700}
      .card{background:var(--card-bg);border:1px solid var(--border);border-radius:14px;padding:16px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
      .muted{color:var(--muted)}
      .section-title{font-weight:800;border-left:4px solid var(--accent);padding-left:.5rem;margin:1rem 0 .5rem}
      .tag{display:inline-block;border:1px solid var(--border);border-radius:10px;padding:.2rem .5rem;margin-right:.3rem}
      .thinking{display:inline-block; font-weight:700}
      .thinking::after{content:""; display:inline-block; width:1em; text-align:left; animation: dots 1.2s steps(4,end) infinite}
      @keyframes dots{0%{content:""}25%{content:"."}50%{content:".."}75%{content:"..."}}
      .ok{color:var(--primary);font-weight:700}
      .warn{color:var(--warn);font-weight:700}
      .error{color:var(--error);font-weight:700}
      table.generated{width:100%; border-collapse:collapse}
      table.generated th, table.generated td{border:1px solid var(--border); padding:.5rem; vertical-align:top}
      table.generated th{background:rgba(37,99,235,0.08)}
      .bubble-u{background:#eef7f7;border:1px solid var(--border);padding:.6rem .8rem;border-radius:14px}
      .bubble-a{background:#f6f7ff;border:1px solid var(--border);padding:.6rem .8rem;border-radius:14px}
      .small-muted{color:var(--muted); font-size:.85rem}
      .chip{display:inline-block;background:rgba(14,165,164,0.1); color:#0ea5a4; border:1px solid #c7ecea; border-radius:999px; padding:.1rem .5rem; margin-left:.3rem}
    </style>
    """, unsafe_allow_html=True)
