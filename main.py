import requests
import json
import os
import time

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
    "yasnagat", "vampire-yuta", "debdutdeb", "casalsgh", "[bot]"
}

def fetch_category(query_suffix, stat_key, stats):
    url = "https://api.github.com/search/issues"
    query = f"org:{ORG} created:>={START_DATE} {query_suffix}"
    params = {"per_page": 100, "page": 1, "q": query}
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

    while True:
        resp = requests.get(url, params=params, headers=headers)
        
        if resp.status_code == 403:
            time.sleep(60)
            continue
        
        data = resp.json()
        items = data.get('items', [])
        if not items:
            break
        
        for item in items:
            author = item['user']['login']
            if author in EXCLUDED_USERS or "[bot]" in author.lower():
                continue
            
            if author not in stats:
                stats[author] = {"author": author, "open_prs": 0, "merged_prs": 0, "open_issues": 0}
            
            stats[author][stat_key] += 1
            
        if 'next' not in resp.links:
            break
        params['page'] += 1

def main():
    stats = {}
    
    search_configs = [
        ("is:pr is:merged", "merged_prs"),
        ("is:pr is:open", "open_prs"),
        ("is:issue is:open", "open_issues")
    ]
    
    for suffix, key in search_configs:
        fetch_category(suffix, key, stats)

    final_list = sorted(
        stats.values(), 
        key=lambda x: (
            -x["merged_prs"], 
            -x["open_prs"], 
            -x["open_issues"], 
            x["author"].lower()
        )
    )

    with open('data.json', 'w') as f:
        json.dump(final_list, f, indent=4)

if __name__ == "__main__":
    main()

