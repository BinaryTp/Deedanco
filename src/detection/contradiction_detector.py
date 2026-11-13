import os
import re
import json
from itertools import combinations
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You are a contradiction detection engine for company policy claims.
You will be given two claims extracted from company documents. Each claim has a topic, entity, value, and condition.

Determine the relationship between Claim A and Claim B. Respond with ONLY valid JSON in this format:
{
  "relationship": "contradiction" | "agreement" | "unrelated",
  "explanation": "one or two sentence plain-language explanation",
  "confidence": a number between 0 and 1
}

Rules:
- "contradiction": the claims state incompatible rules (different numeric values, conflicting permissions) for the same topic and entity.
- "agreement": the claims state the same or fully compatible rules.
- "unrelated": the claims are not about the same topic/rule.

IMPORTANT — how to treat conditions:
- A condition that changes WHO the rule applies to (e.g. "for senior staff", "during probation", "for remote employees") can make two differing values NOT a contradiction, since they govern different groups.
- A condition that is merely a VERSION LABEL or TIMING reference (e.g. "updated policy", "revised policy", "effective 2026", "new circular", "as per the latest memo") does NOT resolve a contradiction. Two documents stating different values for the same rule, even if one claims to be "updated", represent exactly the kind of real-world policy conflict this system must flag. In this case, still classify as "contradiction" and explain that multiple documents disagree on the same rule.
- Never assume a newer-sounding label automatically overrides an older one — your job is to flag the disagreement for human review, not resolve it yourself.
"""


def _extract_number(value_str):
    """Pull out the first number found in a value string, or None."""
    if not value_str:
        return None
    match = re.search(r"[-+]?\d*\.?\d+", value_str)
    return float(match.group()) if match else None


def _normalize_entity(e):
    return e.strip().lower() if e else ""


def _entities_match(a, b):
    return _normalize_entity(a) == _normalize_entity(b)


def _is_subgroup(a, b):
    na, nb = _normalize_entity(a), _normalize_entity(b)
    if not na or not nb or na == nb:
        return False
    return na in nb or nb in na


def _rule_based_check(claim_a, claim_b):
    if claim_a["topic"] != claim_b["topic"]:
        return None

    entity_a, entity_b = claim_a["entity"], claim_b["entity"]

    if not _entities_match(entity_a, entity_b):
        if _is_subgroup(entity_a, entity_b):
            return {
                "relationship": "agreement",
                "explanation": f"'{entity_a}' and '{entity_b}' are different scopes (one is a subgroup of the other), so differing values for this topic do not necessarily conflict.",
                "confidence": 0.85,
                "method": "rule-based-scope"
            }
        return None  # genuinely different entities — let the LLM reason about it

    num_a = _extract_number(claim_a["value"])
    num_b = _extract_number(claim_b["value"])

    if num_a is None or num_b is None:
        return None

    if claim_a.get("condition") or claim_b.get("condition"):
        return None

    if num_a != num_b:
        return {
            "relationship": "contradiction",
            "explanation": f"Same topic '{claim_a['topic']}' for '{claim_a['entity']}' states different values: {claim_a['value']} vs {claim_b['value']}.",
            "confidence": 0.95,
            "method": "rule-based"
        }
    else:
        return {
            "relationship": "agreement",
            "explanation": "Both claims state the same value for the same topic and entity.",
            "confidence": 0.95,
            "method": "rule-based"
        }


def _llm_check(claim_a, claim_b):
    """Fallback: ask the LLM to reason about the relationship."""
    user_prompt = f"""Claim A: {json.dumps(claim_a)}
Claim B: {json.dumps(claim_b)}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw_output)
        result["method"] = "llm"
        return result
    except json.JSONDecodeError:
        return {
            "relationship": "unrelated",
            "explanation": "Could not parse LLM response.",
            "confidence": 0.0,
            "method": "llm-error",
            "_raw_error": raw_output
        }


def detect_contradiction(claim_a, claim_b):
    """Check two claims for contradiction: rule-based first, LLM as fallback."""
    result = _rule_based_check(claim_a, claim_b)
    if result is not None:
        return result
    return _llm_check(claim_a, claim_b)


def detect_contradictions_in_clusters(clusters):
    """
    For each cluster with 2+ claims, compares every pair within it
    and returns the relationship result for each pair.
    """
    results = []

    for cluster_index, cluster in enumerate(clusters):
        claims = cluster["claims"]
        if len(claims) < 2:
            continue

        for claim_a, claim_b in combinations(claims, 2):
            result = detect_contradiction(claim_a, claim_b)
            results.append({
                "cluster_index": cluster_index,
                "claim_a": claim_a,
                "claim_b": claim_b,
                **result
            })

    return results