import requests
import json
import os

TOKEN = os.getenv("GH_TOKEN")
ORG = "RocketChat"
START_DATE = "2025-12-01"
EXCLUDED_USERS = {
    "KevLehman", "tassoevan", "pierre-lehnen-rc", "ggazzo", "gabriellsh", 
    "dionisio-bot", "diegolmello", "sampaiodiego", "MartinSchoeler", 
    "Rohit3523", "dougfabris", "aleksandernsilva", "ricardogarim", 
    "Roxie-32", "lucas-a-pelegrino", "juliajforesti", "jeanfbrito", 
    "dependabot", "cardoso", "d-gubert", "OtavioStasiak", "yash-rajpal", 
    "rocketchat-github-ci", "julio-rocketchat", "Copilot", "rodrigok", 
    "rachana-visavadiya", "geekgonecrazy", "Dnouv", "nazabucciarelli", 
    "lingohub", "jonasflorencio", "jessicaschelly", "github-actions", 
    "dhairyashiil", "cubic-dev-ai", "abhinavkrin", "dhulke", "gabrielpetry", 
    "yasnagat", "vampire-yuta", "[bot]"
}

def fetch_activity():
    stats = {}
    url = "https://api.github.com/search/issues"
    params = {"q": f"org:{ORG} created:>={START_DATE}", "per_page": 100, "page": 1}
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

    while True:
        resp = requests.get(url, params=params, headers=headers)
        items = resp.json().get('items', [])
        if not items: break
        
        for item in items:
            author = item['user']['login']
            if author in EXCLUDED_USERS or "[bot]" in author.lower(): 
                continue
                
            if author not in stats: 
                stats[author] = {"author": author, "open_prs": 0, "merged_prs": 0, "open_issues": 0}
            
            if "pull_request" in item:
                if item.get('pull_request', {}).get('merged_at'): 
                    stats[author]["merged_prs"] += 1
                elif item['state'] == "open": 
                    stats[author]["open_prs"] += 1
            else:
                if item['state'] == "open":
                    stats[author]["open_issues"] += 1
                    
        if 'next' not in resp.links: break
        params['page'] += 1

    filtered_stats = [
        user for user in stats.values() 
        if (user["open_prs"] + user["merged_prs"] + user["open_issues"]) > 0
    ]

    final_list = sorted(
        filtered_stats, 
        key=lambda x: (
            -x["merged_prs"],
            -x["open_prs"],
            -x["open_issues"],
            x["author"].lower()
        )
    )

    with open('data.json', 'w') as f:
        json.dump(final_list, f)

if __name__ == "__main__":
    fetch_activity()

