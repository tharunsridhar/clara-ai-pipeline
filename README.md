# Clara AI - Voice Agent Configuration Pipeline

![Banner](assets/banner.png)

---

## Demo Video

[Watch the pipeline in action](https://www.loom.com/share/3c9c151e09fc426ababd08efeb5c35d6)

---

## What This Does

This pipeline automates the full configuration lifecycle of Clara AI voice agents for service trade businesses.

It takes raw call transcripts and turns them into production-ready AI agent configurations — automatically, cleanly, and repeatably.

```
Demo Call Transcript       ->   Preliminary Agent (v1)
Onboarding Call Transcript ->   Updated Agent (v2) + Changelog
```

---

## Architecture

```
clara_pipeline/
|
|-- src/
|   |-- __init__.py            <- Makes src a Python package
|   |-- extractor.py           <- Gemini LLM extracts structured data from transcripts
|   |-- agent_generator.py     <- Builds full Retell Agent Spec from extracted memo
|   |-- versioning.py          <- Merges v1 + onboarding -> v2, generates changelog
|   `-- pipeline_processor.py  <- Orchestrates the full pipeline per account
|
|-- sample_inputs/             <- Put your transcript .txt files here
|   |-- demo_call_1.txt
|   |-- onboarding_call_1.txt
|   `-- ... (up to 5 pairs)
|
|-- outputs/                   <- Auto-generated results
|   `-- client_1/
|       |-- v1/
|       |   |-- account_memo.json
|       |   `-- agent_spec.json
|       |-- v2/
|       |   |-- account_memo.json
|       |   `-- agent_spec.json
|       `-- changelog.json
|
|-- run_pipeline.py            <- Entry point, run this
|-- .env                       <- Your Gemini API key, never commit this
|-- .gitignore
`-- requirements.txt
```

---

## Data Flow

```
  [demo_call_N.txt]
        |
  [extractor.py]  <-  Gemini 2.0 Flash LLM
        |
  [account_memo v1]
        |
  [agent_generator.py]
        |
  [agent_spec v1]  ->  saved to outputs/client_N/v1/


  [onboarding_call_N.txt]
        |
  [extractor.py]  <-  Gemini 2.0 Flash LLM
        |
  [updated_memo]
        |
  [versioning.py]  <-  merge v1 + updates
        |
  [account_memo v2]
        |
  [agent_generator.py]
        |
  [agent_spec v2]  ->  saved to outputs/client_N/v2/
        |
  [changelog.json] ->  saved to outputs/client_N/
```

---

## Workflow Architecture

### Why Python Instead of n8n

This pipeline was built using pure Python instead of n8n or Make.

Python was chosen because:
- Full control over every step of the pipeline
- No third party orchestration tool needed
- Easier to debug and extend
- Zero cost and fully reproducible on any machine

### Equivalent n8n Flow (For Reference)

If this were built in n8n, the nodes would be:

| n8n Node | Python Equivalent |
|---|---|
| Read File | read_transcript() in pipeline_processor.py |
| HTTP Request (Gemini) | extract_information() in extractor.py |
| Function (parse JSON) | find_json_in_text() in extractor.py |
| Function (build spec) | generate_agent_spec() in agent_generator.py |
| Function (merge) | merge_memos() in versioning.py |
| Function (diff) | generate_changelog() in versioning.py |
| Write File | save_json() in pipeline_processor.py |
| Loop | for i in range() in run_pipeline.py |

---

## How To Run

### Step 1 - Clone or download the project

```bash
git clone https://github.com/yourusername/clara_pipeline.git
cd clara_pipeline
```

### Step 2 - Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 - Add your Gemini API key

Open .env and add your key:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free key at: https://aistudio.google.com

### Step 4 - Add transcript files

Put your files inside sample_inputs/ named like this:

```
sample_inputs/
|-- demo_call_1.txt
|-- onboarding_call_1.txt
|-- demo_call_2.txt
|-- onboarding_call_2.txt
```

### Step 5 - Run the pipeline

```bash
python run_pipeline.py
```

Or with custom paths:

```bash
python run_pipeline.py --input ./sample_inputs --output ./outputs --pairs 5
```

---

## Output Format

### account_memo.json

Structured extraction of all business configuration:

```json
{
    "account_id": "client_1",
    "company_name": "Apex Fire Protection",
    "business_hours": "Monday to Friday 8 AM to 5 PM",
    "services_supported": ["sprinkler systems", "fire alarms"],
    "emergency_definition": ["sprinkler leaks", "fire alarm triggers"],
    "emergency_routing_rules": ["transfer to dispatch immediately"],
    "questions_or_unknowns": []
}
```

### agent_spec.json

Full Retell Agent configuration:

```json
{
    "agent_name": "Apex_Fire_Protection_Clara_Agent",
    "version": "v1",
    "voice_style": "professional",
    "system_prompt": "...",
    "business_hours_flow": ["..."],
    "after_hours_flow": ["..."],
    "call_transfer_protocol": "...",
    "fallback_protocol": "..."
}
```

### changelog.json

Diff between v1 and v2:

```json
{
    "total_changes": 2,
    "changes": [
        {
            "field": "business_hours",
            "old_value": "8 AM to 5 PM",
            "new_value": "7 AM to 6 PM",
            "change_type": "updated"
        }
    ]
}
```

---

## How Extraction Works

The extractor sends each transcript to Gemini 2.0 Flash with a strict prompt:

- Extract ONLY what is clearly stated
- No hallucination, no assumptions
- Missing fields are flagged in questions_or_unknowns
- Returns structured JSON matching a predefined schema

The parser handles all Gemini response formats:
1. Direct JSON
2. JSON wrapped in markdown fences
3. JSON buried inside surrounding text

---

## Versioning Logic

| Situation | Behaviour |
|---|---|
| New scalar value in onboarding | Overrides demo value |
| New list items in onboarding | Merged with demo list, no duplicates |
| Field missing in onboarding | Demo value is preserved |
| questions_or_unknowns | Replaced by onboarding version (old questions resolved) |

---

## Known Limitations

- Gemini free tier has rate limits (15 requests per minute, daily quota)
- If quota is exceeded, extraction falls back to empty schema with error logged
- Transcripts with no company name will have company_name as null in memo
- Pipeline processes .txt files only

---

## What I Would Improve With Production Access

- Add a task tracker integration (Asana API) to create a card per account
- Add a Retell API integration to push agent specs directly
- Add retry and exponential backoff for API rate limit errors
- Build a simple web dashboard to view all account memos and diffs
- Add support for audio files via Whisper transcription
- Store outputs in Supabase instead of local JSON files
- Add a conflict resolution layer for onboarding data that contradicts demo

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | Core language |
| Google Gemini 2.0 Flash | LLM extraction |
| google-genai | Gemini SDK |
| python-dotenv | Environment variable management |
| JSON files | Output storage |

---

## Environment Variables

| Variable | Description |
|---|---|
| GEMINI_API_KEY | Your Google Gemini API key from aistudio.google.com |

---

*Built as part of the Clara AI Technical Associate assignment.*
