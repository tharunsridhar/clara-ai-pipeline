import json

def merge_memos(old_memo, new_memo):

    merged = old_memo.copy()

    all_keys = set(list(old_memo.keys()) + list(new_memo.keys()))

    for key in all_keys:

        old_value = old_memo.get(key)
        new_value = new_memo.get(key)

        # questions_or_unknowns should be replaced not merged
        # onboarding resolves old questions so we dont carry them forward
        if key == "questions_or_unknowns":
            if new_value:
                merged[key] = new_value
            else:
                merged[key] = []
            continue

        if isinstance(new_value, list):
            if isinstance(old_value, list):
                old_list = old_value
            else:
                old_list = []

            # Merge lists without duplicates and without using set()
            # set() crashes if list contains dicts
            combined = old_list + new_value
            seen = []
            for item in combined:
                if item not in seen:
                    seen.append(item)
            merged[key] = seen

        elif new_value is not None and new_value != "":
            # New value exists so onboarding overrides demo
            merged[key] = new_value

        else:
            # New value is empty so keep old value
            merged[key] = old_value

    return merged


def generate_changelog(old_memo, new_memo):

    changes = []

    all_keys = set(list(old_memo.keys()) + list(new_memo.keys()))

    for key in sorted(all_keys):

        old_value = old_memo.get(key)
        new_value = new_memo.get(key)

        if old_value != new_value:

            # Figure out what kind of change this is
            if old_value is None or old_value == [] or old_value == "":
                change_type = "added"
            elif new_value is None or new_value == [] or new_value == "":
                change_type = "removed"
            else:
                change_type = "updated"

            changes.append({
                "field": key,
                "old_value": old_value,
                "new_value": new_value,
                "change_type": change_type
            })

    result = {
        "total_changes": len(changes),
        "changes": changes
    }

    return result


def save_changelog(changelog, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(changelog, f, indent=4)
    print("[INFO] Changelog saved to:", path)
