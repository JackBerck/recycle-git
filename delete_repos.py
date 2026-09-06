import os
import sys
import json
import urllib.request
import urllib.error
import getpass
import re

GITHUB_API_URL = "https://api.github.com"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "GitHub-Repo-Deleter-Script"
    }

def request_api(url, token, method="GET", data=None):
    headers = get_headers(token)
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            if status == 204:
                return status, None
            response_body = resp.read().decode("utf-8")
            return status, json.loads(response_body) if response_body else None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(error_body)
        except Exception:
            err_json = {"message": error_body}
        return e.code, err_json
    except Exception as e:
        return 500, {"message": str(e)}

def fetch_all_repos(token):
    repos = []
    page = 1
    print("\n🔍 Scanning GitHub repositories...")
    
    while True:
        url = f"{GITHUB_API_URL}/user/repos?type=all&per_page=100&page={page}&sort=updated"
        status, data = request_api(url, token)
        
        if status != 200:
            err_msg = data.get("message") if isinstance(data, dict) else data
            print(f"❌ Failed to fetch repositories (HTTP {status}): {err_msg}")
            sys.exit(1)
            
        if not data:
            break
            
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
        
    return repos

def parse_selection(input_str, max_index, repos_dict):
    selected_indices = set()
    input_str = input_str.strip()
    
    if input_str.lower() in ['all', '*']:
        return list(range(1, max_index + 1))
    
    # Tokenize by replacing commas with spaces and splitting
    raw_tokens = [t.strip() for t in input_str.replace(",", " ").split() if t.strip()]
    
    for token in raw_tokens:
        # Check range (e.g. 2-5 or 2..5)
        range_match = re.match(r'^(\d+)[-..]+(\d+)$', token)
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            for idx in range(min(start, end), max(start, end) + 1):
                if 1 <= idx <= max_index:
                    selected_indices.add(idx)
            continue
            
        # Check if single digit
        if token.isdigit():
            idx = int(token)
            if 1 <= idx <= max_index:
                selected_indices.add(idx)
            continue
            
        # Check by repo name (exact or substring match)
        matched = False
        for idx, repo in repos_dict.items():
            if token.lower() in [repo["name"].lower(), repo["full_name"].lower()]:
                selected_indices.add(idx)
                matched = True
        if not matched:
            # Substring match fallback
            for idx, repo in repos_dict.items():
                if token.lower() in repo["name"].lower():
                    selected_indices.add(idx)
                    
    return sorted(list(selected_indices))

def load_env(env_path=".env"):
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and not os.environ.get(key):
                        os.environ[key] = val
    except Exception as e:
        print(f"⚠️ Warning: Could not read .env file: {e}")

def main():
    load_env()
    clear_screen()
    print("=" * 60)
    print(" 🗑️  GITHUB REPOSITORY BATCH DELETER")
    print("=" * 60)

    # 1. Get Token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        token = getpass.getpass("🔑 Enter GitHub Personal Access Token (hidden input): ").strip()
        
    if not token:
        print("❌ Token is required. Exiting.")
        sys.exit(1)

    # 2. Verify user
    status, user_info = request_api(f"{GITHUB_API_URL}/user", token)
    if status != 200:
        err_msg = user_info.get("message") if isinstance(user_info, dict) else user_info
        print(f"❌ Invalid token or API error (HTTP {status}): {err_msg}")
        sys.exit(1)

    username = user_info["login"]

    # 3. Interactive Loop
    while True:
        clear_screen()
        print("=" * 60)
        print(f" 🗑️  GITHUB REPOSITORY BATCH DELETER | User: {username}")
        print("=" * 60)

        # Fetch repos
        repos = fetch_all_repos(token)
        if not repos:
            print("ℹ️ No repositories found.")
            break

        # Filter repos owned by authenticated user
        owned_repos = [r for r in repos if r["owner"]["login"].lower() == username.lower()]

        if not owned_repos:
            print("ℹ️ No owned repositories remaining.")
            break

        print(f"\n📦 Found {len(owned_repos)} repositories owned by {username}:\n")
        print(f"{'No.':<5} {'Repository Name':<35} {'Visibility':<12} {'Stars':<8} {'Forks':<8}")
        print("-" * 70)

        repos_dict = {}
        for idx, repo in enumerate(owned_repos, 1):
            repos_dict[idx] = repo
            vis = "🔒 Private" if repo["private"] else "🌐 Public"
            stars = repo["stargazers_count"]
            forks = repo["forks_count"]
            print(f"{idx:<5} {repo['name']:<35} {vis:<12} {stars:<8} {forks:<8}")

        print("\n" + "=" * 70)
        print("Selection Options:")
        print(" - Single or multiple: 1, 3, 5  | Range: 2-5")
        print(" - Repo names: repo-a          | All repos: all")
        print("=" * 70)

        selection_input = input("\n👉 Enter numbers/names of repos to DELETE (or 'q' to quit): ").strip()
        if selection_input.lower() in ['q', 'quit', 'exit', '']:
            print("Operation canceled. Exiting.")
            break

        selected_indices = parse_selection(selection_input, len(owned_repos), repos_dict)

        if not selected_indices:
            input("❌ No valid repositories selected. Press Enter to try again...")
            continue

        selected_repos = [repos_dict[i] for i in selected_indices]

        print("\n" + "⚠️ " * 20)
        print("  WARNING: THE FOLLOWING REPOSITORIES WILL BE PERMANENTLY DELETED!")
        print("⚠️ " * 20 + "\n")
        for r in selected_repos:
            print(f"  • {r['full_name']} ({'Private' if r['private'] else 'Public'})")

        print(f"\nTotal repos to delete: {len(selected_repos)}")
        confirm = input("\nType 'DELETE' to confirm permanent deletion: ").strip()

        if confirm != "DELETE":
            retry = input("❌ Confirmation failed. Try again? (y/N): ").strip().lower()
            if retry == 'y':
                continue
            else:
                break

        print("\n🚀 Starting deletion process...\n")
        success_count = 0
        fail_count = 0

        for repo in selected_repos:
            full_name = repo["full_name"]
            print(f"Deleting {full_name}...", end=" ")
            del_status, del_resp = request_api(f"{GITHUB_API_URL}/repos/{full_name}", token, method="DELETE")
            
            if del_status == 204:
                print("✅ SUCCESS")
                success_count += 1
            else:
                err_msg = del_resp.get("message", "Unknown error") if isinstance(del_resp, dict) else "Unknown error"
                print(f"❌ FAILED (HTTP {del_status}: {err_msg})")
                fail_count += 1

        print("\n" + "=" * 50)
        print(f"Done! Successfully deleted: {success_count} | Failed: {fail_count}")
        print("=" * 50)

        again = input("\n👉 Do you want to delete more repositories? (y/N): ").strip().lower()
        if again not in ['y', 'yes']:
            print("Done. Goodbye!")
            break

if __name__ == "__main__":
    main()
