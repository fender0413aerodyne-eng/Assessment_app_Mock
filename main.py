import streamlit as st
from initialize import get_client, load_env, inject_base_styles
from components import (
    app_header, disclaimer, patient_input_form, format_selector,
    output_section_soap, output_section_plan_table, followup_box,
    end_session_box, show_toast
)
from inference import generate_care_plan, answer_followup
from utils import (
    ensure_session_state, is_relevant_question, save_last_outputs,
    has_last_outputs
)

# --- Page setup ---
st.set_page_config(page_title="看護診断/看護計画アシスタント", page_icon="🩺", layout="wide")
load_env()
ensure_session_state()

# --- Theme toggle first (so styles reflect current state) ---
with st.sidebar:
    st.markdown("### 表示設定")
    dark_mode = st.toggle("ダークモード", value=st.session_state.get("dark_mode", False))
    st.session_state["dark_mode"] = dark_mode

# Inject styles with current dark mode
inject_base_styles(dark_mode)

# --- Client ---
client = get_client()

# --- Header & Disclaimer ---
app_header()
disclaimer()

# --- Input area ---
st.markdown("### 📝 看護情報を入力")
patient_text = patient_input_form()

col1, col2 = st.columns([2, 1])
with col1:
    output_format = format_selector()
with col2:
    submit = st.button("🚀 送信", use_container_width=True)

if submit:
    if not patient_text.strip():
        show_toast("看護情報を入力してください。", variant="warn")
    else:
        with st.spinner("思考中… 看護診断と計画を整理しています"):
            result = generate_care_plan(client, patient_text, output_format)
        if result.get("error"):
            show_toast(result["error"], variant="error")
        else:
            # Persist last outputs for follow-ups
            save_last_outputs(result, patient_text, output_format)
            # Render outputs
            st.markdown("## 🧾 出力結果")
            if output_format in ("SOAP形式", "両方"):
                output_section_soap(result.get("soap"))
            if output_format in ("看護計画表形式", "両方"):
                output_section_plan_table(result.get("plan_table"))

# --- Follow-up Q&A ---
if has_last_outputs():
    st.markdown("---")
    st.markdown("### ❓ 出力結果に関するご質問")
    q = followup_box()
    ask = st.button("💬 質問する", use_container_width=True)
    if ask:
        if not q.strip():
            show_toast("質問内容を入力してください。", variant="warn")
        else:
            if not is_relevant_question(q):
                st.info("本件とは関係がない質問です。対象：『看護情報 → 看護診断 / 看護計画（SOAP / 計画表）』に関するご質問を受け付けます。")
            else:
                with st.spinner("思考中… 回答を準備しています"):
                    ans = answer_followup(
                        client=client,
                        last_outputs=st.session_state["last_outputs"],
                        question=q
                    )
                if ans.get("error"):
                    show_toast(ans["error"], variant="error")
                else:
                    st.markdown("#### 回答")
                    st.markdown(ans["answer"])

# --- End button ---
st.markdown("---")
if end_session_box():
    st.success("お疲れさまでした")
