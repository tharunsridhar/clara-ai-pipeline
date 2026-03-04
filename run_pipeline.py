import os
import argparse
from dotenv import load_dotenv
from src.pipeline_processor import process_transcripts

# Load .env so GEMINI_API_KEY is available
load_dotenv()


def validate_file(path):

    if not os.path.exists(path):
        print("[ERROR] File not found:", path)
        return False

    if not os.path.isfile(path):
        print("[ERROR] Not a valid file:", path)
        return False

    if os.path.getsize(path) == 0:
        print("[ERROR] File is empty:", path)
        return False

    return True


def run_all(input_folder, output_folder, num_pairs):

    print("\n" + "=" * 50)
    print("  CLARA AI - Voice Agent Configuration Pipeline")
    print("=" * 50)
    print("  Input folder :", input_folder)
    print("  Output folder:", output_folder)
    print("  Pairs to run :", num_pairs)
    print("=" * 50)

    success_count = 0
    skip_count    = 0
    fail_count    = 0

    for i in range(1, num_pairs + 1):

        demo_path       = os.path.join(input_folder, "demo_call_" + str(i) + ".txt")
        onboarding_path = os.path.join(input_folder, "onboarding_call_" + str(i) + ".txt")
        account_id      = "client_" + str(i)

        print("\n" + "-" * 50)
        print("  ACCOUNT:", account_id)
        print("-" * 50)

        demo_valid       = validate_file(demo_path)
        onboarding_valid = validate_file(onboarding_path)

        if not demo_valid or not onboarding_valid:
            print("[SKIPPED]", account_id, "- missing or invalid transcript file")
            skip_count = skip_count + 1
            continue

        try:
            process_transcripts(
                demo_input       = demo_path,
                onboarding_input = onboarding_path,
                output_dir       = output_folder,
                account_id       = account_id,
                input_type       = "file"
            )
            print("[SUCCESS]", account_id, "completed")
            success_count = success_count + 1

        except Exception as e:
            print("[ERROR]", account_id, "failed")
            print("  Reason:", str(e))
            fail_count = fail_count + 1
            continue

    print("\n" + "=" * 50)
    print("  PIPELINE COMPLETE")
    print("=" * 50)
    print("  Success:", success_count)
    print("  Skipped:", skip_count)
    print("  Failed :", fail_count)
    print("  Outputs saved to:", output_folder)
    print("=" * 50)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Clara AI Pipeline")

    parser.add_argument(
        "--input",
        default="sample_inputs",
        help="Folder with demo_call_N.txt and onboarding_call_N.txt files"
    )
    parser.add_argument(
        "--output",
        default="outputs",
        help="Folder where results will be saved"
    )
    parser.add_argument(
        "--pairs",
        type=int,
        default=5,
        help="Number of pairs to process"
    )

    args = parser.parse_args()

    run_all(args.input, args.output, args.pairs)
