import os
import json
import copy
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCHEMA = {
    "account_id": None,
    "company_name": None,
    "office_address": None,
    "business_hours": None,
    "services_supported": [],
    "emergency_definition": [],
    "emergency_routing_rules": [],
    "non_emergency_routing_rules": [],
    "call_transfer_rules": [],
    "integration_constraints": [],
    "after_hours_flow_summary": None,
    "office_hours_flow_summary": None,
    "notes": [],
    "questions_or_unknowns": []
}


def find_json_in_text(text):
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return None


def extract_information(transcript):

    prompt = (
        "You are an information extraction system.\n\n"
        "Extract ONLY information that is clearly stated in the transcript.\n"
        "Do NOT guess or make up any values.\n"
        "If a field is not mentioned in the transcript set it to null or empty list.\n"
        "Your entire response must be a single JSON object and nothing else.\n"
        "No markdown. No code fences. No explanation. Just the JSON.\n\n"
        "Use exactly this schema:\n"
        + json.dumps(SCHEMA, indent=2)
        + "\n\nTranscript:\n"
        + transcript
    )

    print("[INFO] Sending transcript to Gemini...")

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        raw = response.text.strip()

        print("[DEBUG] Gemini response preview:", raw[:200])

        # Step 1: try parsing directly
        try:
            memo = json.loads(raw)
            print("[INFO] Extraction successful.")

        except json.JSONDecodeError:

            # Step 2: strip markdown fences if present
            if "```" in raw:
                parts = raw.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"):
                        part = part[4:].strip()
                    try:
                        memo = json.loads(part)
                        print("[INFO] Extraction successful after stripping fences.")
                        break
                    except:
                        continue
                else:
                    raise ValueError("Could not parse after stripping fences")

            else:
                # Step 3: find JSON by locating first { and last }
                extracted = find_json_in_text(raw)
                if extracted:
                    memo = json.loads(extracted)
                    print("[INFO] Extraction successful after finding JSON block.")
                else:
                    raise ValueError("No JSON object found in response")

    except Exception as e:
        print("[ERROR] Could not parse Gemini response:", e)
        memo = copy.deepcopy(SCHEMA)
        memo["questions_or_unknowns"].append("LLM response could not be parsed: " + str(e))

    # Flag missing critical fields
    critical_fields = [
        "company_name",
        "business_hours",
        "emergency_definition",
        "emergency_routing_rules",
        "after_hours_flow_summary"
    ]

    for key in critical_fields:
        value = memo.get(key)
        is_missing = (value is None or value == [] or value == "")
        already_flagged = any(key in q for q in memo.get("questions_or_unknowns", []))

        if is_missing and not already_flagged:
            memo["questions_or_unknowns"].append(key + " is missing from transcript")

    return memo
