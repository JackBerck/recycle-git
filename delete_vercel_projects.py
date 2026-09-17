import os
import sys
import json
import urllib.request
import urllib.error
import getpass
import re
from datetime import datetime

VERCEL_API_URL = "https://api.vercel.com"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Vercel-Project-Deleter-Script"
    }

def request_api(url, token, method="GET", data=None):
    headers = get_headers(token)
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode("utf-8")
    
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

def fetch_all_projects(token, team_id=None):
    projects = []
    until = None
    print("\n🔍 Scanning Vercel projects...")
    
    while True:
        url = f"{VERCEL_API_URL}/v9/projects?limit=100"
        if team_id:
            url += f"&teamId={team_id}"
        if until:
            url += f"&until={until}"
            
        status, data = request_api(url, token)
        
        if status != 200:
            err_msg = data.get("error", {}).get("message") if isinstance(data, dict) and "error" in data else (data.get("message") if isinstance(data, dict) else data)
            print(f"❌ Failed to fetch Vercel projects (HTTP {status}): {err_msg}")
            sys.exit(1)
            
        if not data or "projects" not in data:
            break
            
        fetched = data.get("projects", [])
        if not fetched:
            break
            
        projects.extend(fetched)
        
        pagination = data.get("pagination", {})
        until = pagination.get("next")
        if not until or len(fetched) < 100:
            break
            
    return projects

def parse_selection(input_str, max_index, projects_dict):
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
            
        # Check by project name (exact or substring match)
        matched = False
        for idx, prj in projects_dict.items():
            if token.lower() == prj["name"].lower():
                selected_indices.add(idx)
                matched = True
        if not matched:
            # Substring match fallback
            for idx, prj in projects_dict.items():
                if token.lower() in prj["name"].lower():
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

def format_date(ms_timestamp):
    if not ms_timestamp:
        return "N/A"
    try:
        dt = datetime.fromtimestamp(ms_timestamp / 1000.0)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return "N/A"

def main():
    load_env()
    clear_screen()
    print("=" * 65)
    print(" 📐  VERCEL PROJECT BATCH DELETER")
    print("=" * 65)

    # 1. Get Token
    token = os.environ.get("VERCEL_TOKEN")
    if not token:
        token = getpass.getpass("🔑 Enter Vercel Access Token (hidden input): ").strip()
        
    if not token:
        print("❌ Vercel Token is required. Exiting.")
        sys.exit(1)

    team_id = os.environ.get("VERCEL_TEAM_ID")

    # 2. Verify user / token
    status, user_info = request_api(f"{VERCEL_API_URL}/v2/user", token)
    if status != 200:
        err_msg = user_info.get("error", {}).get("message") if isinstance(user_info, dict) and "error" in user_info else "Invalid token"
        print(f"❌ Invalid Vercel token or API error (HTTP {status}): {err_msg}")
        sys.exit(1)

    user_obj = user_info.get("user", user_info)
    username = user_obj.get("username") or user_obj.get("email") or "Vercel User"

    # 3. Interactive Loop
    while True:
        clear_screen()
        print("=" * 65)
        team_str = f" | Team ID: {team_id}" if team_id else ""
        print(f" 📐  VERCEL PROJECT BATCH DELETER | User: {username}{team_str}")
        print("=" * 65)

        # Fetch projects
        projects = fetch_all_projects(token, team_id)
        if not projects:
            print("ℹ️ No Vercel projects found.")
            break

        print(f"\n📦 Found {len(projects)} Vercel projects:\n")
        print(f"{'No.':<5} {'Project Name':<32} {'Framework':<14} {'Updated':<12}")
        print("-" * 65)

        projects_dict = {}
        for idx, prj in enumerate(projects, 1):
            projects_dict[idx] = prj
            name = prj.get("name", "Unnamed")
            framework = prj.get("framework") or "other"
            updated = format_date(prj.get("updatedAt"))
            print(f"{idx:<5} {name:<32} {framework:<14} {updated:<12}")

        print("\n" + "=" * 65)
        print("Selection Options:")
        print(" - Single or multiple: 1, 3, 5  | Range: 2-5")
        print(" - Project names: my-app       | All projects: all")
        print("=" * 65)

        selection_input = input("\n👉 Enter numbers/names of projects to DELETE (or 'q' to quit): ").strip()
        if selection_input.lower() in ['q', 'quit', 'exit', '']:
            print("Operation canceled. Exiting.")
            break

        selected_indices = parse_selection(selection_input, len(projects), projects_dict)

        if not selected_indices:
            input("❌ No valid projects selected. Press Enter to try again...")
            continue

        selected_projects = [projects_dict[i] for i in selected_indices]

        print("\n" + "⚠️ " * 20)
        print("  WARNING: THE FOLLOWING VERCEL PROJECTS WILL BE PERMANENTLY DELETED!")
        print("⚠️ " * 20 + "\n")
        for prj in selected_projects:
            print(f"  • {prj['name']} (ID: {prj['id']})")

        print(f"\nTotal projects to delete: {len(selected_projects)}")
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

        for prj in selected_projects:
            name = prj["name"]
            prj_id = prj["id"]
            print(f"Deleting project {name} ({prj_id})...", end=" ")
            
            del_url = f"{VERCEL_API_URL}/v9/projects/{prj_id}"
            if team_id:
                del_url += f"?teamId={team_id}"
                
            del_status, del_resp = request_api(del_url, token, method="DELETE")
            
            if del_status in (200, 204):
                print("✅ SUCCESS")
                success_count += 1
            else:
                err_msg = "Unknown error"
                if isinstance(del_resp, dict):
                    err_msg = del_resp.get("error", {}).get("message") or del_resp.get("message", "Unknown error")
                print(f"❌ FAILED (HTTP {del_status}: {err_msg})")
                fail_count += 1

        print("\n" + "=" * 50)
        print(f"Done! Successfully deleted: {success_count} | Failed: {fail_count}")
        print("=" * 50)

        again = input("\n👉 Do you want to delete more projects? (y/N): ").strip().lower()
        if again not in ['y', 'yes']:
            print("Done. Goodbye!")
            break

if __name__ == "__main__":
    main()
