from openai import OpenAI
from utils import json_loads_safe
from prompts import build_generation_prompt, build_followup_prompt

MODEL = "gpt-4o-mini"
TEMPERATURE = 0.1

def generate_care_plan(client: OpenAI, patient_text: str, output_format: str):
    try:
        messages = build_generation_prompt(patient_text, output_format)
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=messages,
            response_format={"type":"json_object"}
        )
        content = resp.choices[0].message.content
        data = json_loads_safe(content)
        if not data:
            return {"error": "出力の解析に失敗しました。入力内容を見直すか、再度実行してください。"}
        data.setdefault("soap", {"assessment":[], "plan":[]})
        data.setdefault("plan_table", {"problems":[], "assessments":[], "goals":[], "interventions":[], "evaluation":[]})
        data.setdefault("reasoning_summary", {"key_findings":[], "rationales":[], "differentials":[]})
        return data
    except Exception as e:
        return {"error": f"生成に失敗しました: {e}"}

def answer_followup(client: OpenAI, last_outputs: dict, question: str):
    try:
        context = {
            "patient_text": last_outputs.get("patient_text"),
            "soap": last_outputs.get("soap"),
            "plan_table": last_outputs.get("plan_table"),
            "reasoning_summary": last_outputs.get("reasoning_summary")
        }
        messages = build_followup_prompt(context, question)
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=messages
        )
        content = resp.choices[0].message.content
        return {"answer": content}
    except Exception as e:
        return {"error": f"回答生成に失敗しました: {e}"}
