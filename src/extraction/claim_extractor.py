import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """You are a claim extraction engine for company policy documents.
Given a single sentence (clause) from a policy document, extract the atomic rule it contains.

Return ONLY valid JSON in this exact format, nothing else:
{
  "topic": "short topic name, e.g. 'annual leave'",
  "entity": "who the rule applies to, e.g. 'employees'",
  "value": "the numeric or specific value stated, e.g. '30 days'",
  "condition": "any condition/exception mentioned, or null if none"
}

If the sentence contains no extractable rule (e.g. it's a heading or irrelevant text), return:
{"topic": null, "entity": null, "value": null, "condition": null}

Examples:
Sentence: "Employees are entitled to 30 days of annual leave per year."
Output: {"topic": "annual leave", "entity": "employees", "value": "30 days", "condition": null}

Sentence: "Leave requests must be submitted at least 7 days in advance."
Output: {"topic": "leave request notice", "entity": "employees", "value": "7 days advance notice", "condition": null}

Sentence: "Employees are entitled to 24 days of annual leave per year according to the updated policy."
Output: {"topic": "annual leave", "entity": "employees", "value": "24 days", "condition": "updated policy"}
"""


def extract_claim(clause_text):
    """Send one clause to the LLM and get back a structured claim as a dict."""
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f'Sentence: "{clause_text}"\nOutput:'}
        ],
        temperature=0,
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {"topic": None, "entity": None, "value": None, "condition": None, "_raw_error": raw_output}


def extract_claims_from_chunks(chunks):
    """Takes chunker.py's output (list of {text, source}) and returns claims with source attached."""
    claims = []
    for chunk in chunks:
        claim = extract_claim(chunk["text"])
        claim["source"] = chunk["source"]
        claim["original_text"] = chunk["text"]
        claims.append(claim)
    return claims