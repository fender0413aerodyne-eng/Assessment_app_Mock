import re
import json
from datetime import datetime, timezone
import streamlit as st

RELEVANT_KEYWORDS = [
    "看護", "患者", "診断", "目標", "介入", "評価", "アセスメント", "SOAP", "計画", "根拠", "要点",
    "NANDA", "NANDA-I", "NIC", "NOC"
]

def ensure_session_state():
    st.session_state.setdefault("last_outputs", None)   # 直近の結果（Q&Aのコンテキスト用）
    st.session_state.setdefault("history", [])          # セッション内のみ保持する会話履歴（生成・Q&A）
    st.session_state.setdefault("followup_q", "")       # フォローアップ質問欄の入力内容（送信後にクリア）

def save_last_outputs(result, patient_text, output_format):
    st.session_state["last_outputs"] = {
        "patient_text": patient_text,
        "output_format": output_format,
        "soap": result.get("soap"),
        "plan_table": result.get("plan_table"),
        "reasoning_summary": result.get("reasoning_summary")
    }

def has_last_outputs():
    return st.session_state.get("last_outputs") is not None

def is_relevant_question(q: str) -> bool:
    q = q.strip()
    if not q: return False
    return any(k.lower() in q.lower() for k in RELEVANT_KEYWORDS)

def json_loads_safe(s: str):
    try:
        return json.loads(s)
    except Exception:
        # 可能な範囲で修復: コードフェンスや余分なカンマを除去
        s = re.sub(r"^```(json)?|```$", "", s.strip(), flags=re.MULTILINE)
        s = re.sub(r",\s*([}\]])", r"\1", s)
        try:
            return json.loads(s)
        except Exception:
            return None

# ===== Session-scoped conversation history =====
def append_history_generation(patient_text: str, output_format: str, result: dict):
    entry = {
        "type": "generation",
        "ts": now_iso(),
        "payload": {
            "patient_text": patient_text,
            "output_format": output_format,
            "soap": result.get("soap"),
            "plan_table": result.get("plan_table"),
            "reasoning_summary": result.get("reasoning_summary"),
        }
    }
    st.session_state["history"].append(entry)

def append_history_followup(question: str, answer: str):
    entry = {
        "type": "followup",
        "ts": now_iso(),
        "payload": {
            "question": question,
            "answer": answer
        }
    }
    st.session_state["history"].append(entry)

def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
