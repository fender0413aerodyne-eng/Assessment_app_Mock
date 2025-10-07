import streamlit as st
from initialize import get_client, load_env, inject_base_styles
from components import (
    app_header, disclaimer, patient_input_form, format_selector,
    output_section_soap, output_section_plan_table, followup_box,
    end_session_box, show_toast, history_timeline
)
from inference import generate_care_plan, answer_followup
from utils import (
    ensure_session_state, is_relevant_question, save_last_outputs,
    has_last_outputs, append_history_generation, append_history_followup
)

# --- Page setup ---
st.set_page_config(page_title="看護診断/看護計画アシスタント", page_icon="🩺", layout="wide")
load_env()
ensure_session_state()

# Inject styles（ライト固定・ダークモードなし）
inject_base_styles()

# --- Client ---
client = get_client()

# --- Header & Disclaimer ---
app_header()
disclaimer()

# --- Conversation history (always visible) ---
if st.session_state["history"]:
    st.markdown("## 🗂️ 会話履歴")
    history_timeline(st.session_state["history"])
    st.markdown("---")

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
        with st.spinner("思考中… "):
            result = generate_care_plan(client, patient_text, output_format)
        if result.get("error"):
            show_toast(result["error"], variant="error")
        else:
            # Persist last outputs for follow-ups & push to history
            save_last_outputs(result, patient_text, output_format)
            append_history_generation(
                patient_text=patient_text,
                output_format=output_format,
                result=result
            )
            # 直近の生成結果をその場で表示（履歴の末尾＝最新を単独レンダリング）
            show_toast("完了。下に結果を表示しました。", variant="ok")
            st.markdown("## 🧾 結果（今回）")
            history_timeline([st.session_state["history"][-1]])
            # 次の質問開始時に入力欄が空になるようにクリアして即リラン
            if "followup_q" in st.session_state:
                st.session_state["followup_q"] = ""
                st.rerun()

# --- Follow-up Q&A ---
if has_last_outputs():
    st.markdown("---")
    st.markdown("### ❓ 出力結果に関するご質問")
    q = followup_box()  # key="followup_q" で状態管理（components.py側）
    ask = st.button("💬 質問する", use_container_width=True)
    if ask:
        if not q.strip():
            show_toast("質問内容を入力してください。", variant="warn")
        else:
            if not is_relevant_question(q):
                st.info("本件とは関係がない質問です。対象：『看護情報 → 看護診断 / 看護計画（SOAP / 計画表）』に関するご質問を受け付けます。")
            else:
                with st.spinner("思考中… "):
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
                    append_history_followup(question=q, answer=ans["answer"])
                    # 入力欄を安全にクリア → すぐ再実行（UIと状態の不整合を防止）
                    if "followup_q" in st.session_state:
                        st.session_state["followup_q"] = ""
                        st.rerun()

# --- End button ---
st.markdown("---")
if end_session_box():
    st.success("お疲れさまでした")
