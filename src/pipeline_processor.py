import os
import json

from src.extractor import extract_information
from src.agent_generator import generate_agent_spec
from src.versioning import merge_memos, generate_changelog, save_changelog


def read_transcript(input_data, input_type):

    if input_type == "file":
        f = open(input_data, "r", encoding="utf-8")
        transcript = f.read()
        f.close()
        return transcript

    elif input_type == "text":
        return input_data

    else:
        raise ValueError("input_type must be file or text")


def save_json(data, path):
    f = open(path, "w", encoding="utf-8")
    json.dump(data, f, indent=4)
    f.close()


def process_transcripts(demo_input, onboarding_input, output_dir, account_id, input_type):

    print("\n[PIPELINE] Starting for account:", account_id)

    # Read both transcripts
    demo_transcript = read_transcript(demo_input, input_type)
    onboarding_transcript = read_transcript(onboarding_input, input_type)

    print("[INFO] Demo transcript loaded,", len(demo_transcript), "chars")
    print("[INFO] Onboarding transcript loaded,", len(onboarding_transcript), "chars")

    # ── STEP 1: Extract memo from demo call and generate v1 ──────────────────

    print("\n[STEP 1] Extracting from demo transcript...")
    memo_v1 = extract_information(demo_transcript)

    # Set account_id manually since LLM cannot know it
    memo_v1["account_id"] = account_id

    agent_spec_v1 = generate_agent_spec(memo_v1, "v1")

    # Create v1 output folder
    v1_path = os.path.join(output_dir, account_id, "v1")
    os.makedirs(v1_path, exist_ok=True)

    memo_v1_file  = os.path.join(v1_path, "account_memo.json")
    agent_v1_file = os.path.join(v1_path, "agent_spec.json")

    save_json(memo_v1, memo_v1_file)
    save_json(agent_spec_v1, agent_v1_file)

    print("[INFO] V1 memo saved:", memo_v1_file)
    print("[INFO] V1 agent spec saved:", agent_v1_file)
    print("[V1] Company:", memo_v1.get("company_name"))
    print("[V1] Business hours:", memo_v1.get("business_hours"))
    print("[V1] Unknowns:", memo_v1.get("questions_or_unknowns"))

    # ── STEP 2: Extract from onboarding and merge into v2 ────────────────────

    print("\n[STEP 2] Extracting from onboarding transcript...")
    updated_memo = extract_information(onboarding_transcript)
    updated_memo["account_id"] = account_id

    print("\n[STEP 3] Merging v1 memo with onboarding updates...")
    memo_v2 = merge_memos(memo_v1, updated_memo)

    agent_spec_v2 = generate_agent_spec(memo_v2, "v2")

    # Create v2 output folder
    v2_path = os.path.join(output_dir, account_id, "v2")
    os.makedirs(v2_path, exist_ok=True)

    memo_v2_file  = os.path.join(v2_path, "account_memo.json")
    agent_v2_file = os.path.join(v2_path, "agent_spec.json")

    save_json(memo_v2, memo_v2_file)
    save_json(agent_spec_v2, agent_v2_file)

    print("[INFO] V2 memo saved:", memo_v2_file)
    print("[INFO] V2 agent spec saved:", agent_v2_file)
    print("[V2] Company:", memo_v2.get("company_name"))
    print("[V2] Business hours:", memo_v2.get("business_hours"))
    print("[V2] Unknowns:", memo_v2.get("questions_or_unknowns"))

    # ── STEP 3: Generate and save changelog ──────────────────────────────────

    print("\n[STEP 4] Generating changelog...")
    changelog = generate_changelog(memo_v1, memo_v2)

    changelog_file = os.path.join(output_dir, account_id, "changelog.json")
    save_changelog(changelog, changelog_file)

    print("[CHANGELOG]", changelog["total_changes"], "field(s) changed from v1 to v2")
    print("\n[PIPELINE] Done for account:", account_id)
    print("Output folder:", os.path.join(output_dir, account_id))
