from flask import Flask, render_template, request, jsonify
from operator import itemgetter
import json
import os
import time
import re
from rapidfuzz import fuzz

JSON_FILE_PATH = "azure_ips.json"
UPDATE_INTERVAL = 86400  # 24 hours in seconds

def get_last_updated_date():
    if os.path.exists(JSON_FILE_PATH):
        return time.ctime(os.path.getmtime(JSON_FILE_PATH))
    return "Unknown"

def load_json_data():
    with open(JSON_FILE_PATH, "r") as f:
        return json.load(f)

app = Flask(__name__)

@app.route("/")
def index():
    last_updated_date = get_last_updated_date()
    data = load_json_data()
    change_number = data.get("changeNumber", "Unknown")
    return render_template("index.html", last_updated_date=last_updated_date, change_number=change_number)

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    if not query:
        return jsonify({"error": "No query provided"})

    data = load_json_data()

    results = []
    unique_services = set()
    ip_services = {}
    region_services = set()

    ip_search = re.match(r'^\d', query) is not None

    if ip_search:
        for value in data["values"]:
            for prefix in value["properties"]["addressPrefixes"]:
                if prefix.startswith(query):
                    system_service = value["properties"].get("name", value["name"])
                    if system_service and system_service not in unique_services:
                        unique_services.add(system_service)
                        if prefix in ip_services:
                            ip_services[prefix].append(system_service)
                        else:
                            ip_services[prefix] = [system_service]

        for ip, services in ip_services.items():
            services = list(set(services))
            results.append({
                "name": ", ".join(services),
                "ipAddress": ip,
                "servicesForIP": services
            })
        return jsonify({"results": results})
    
    else:
        for value in data["values"]:
            system_service = value["properties"].get("name", value["name"])
            region = value["properties"].get("region", "")
            
            if system_service and system_service not in unique_services:
                score = fuzz.ratio(query.lower(), system_service.lower())
                if score >= 50:  # Threshold for fuzzy matching
                    unique_services.add(system_service)

            if region and query.lower() in region.lower() and region not in region_services:
                region_services.add(region)
                ips_for_region = []
                for prefix in value["properties"]["addressPrefixes"]:
                    ips_for_region.append(prefix)
                results.append({
                    "name": region,
                    "ipAddress": None,
                    "ipsForService": ", ".join(ips_for_region)
                })



        scored_results = []

        for service in sorted(unique_services, key=str.lower):
            ips_for_service = []
            for value in data["values"]:
                if service.lower() == value["properties"].get("name", value["name"]).lower():
                    ips_for_service.extend(value["properties"]["addressPrefixes"])
            token_set_score = fuzz.token_set_ratio(query.lower(), service.lower())
            token_sort_score = fuzz.token_sort_ratio(query.lower(), service.lower())
            score = max(token_set_score, token_sort_score)
            scored_results.append({
                "name": service,
                "ipAddress": None,
                "ipsForService": ", ".join(ips_for_service),
                "score": score
            })
    
        for region in sorted(region_services, key=str.lower):
            ips_for_region = []
            for value in data["values"]:
                if region.lower() == value["properties"].get("region", "").lower():
                    ips_for_region.extend(value["properties"]["addressPrefixes"])
            token_set_score = fuzz.token_set_ratio(query.lower(), region.lower())
            token_sort_score = fuzz.token_sort_ratio(query.lower(), region.lower())
            score = max(token_set_score, token_sort_score)
            scored_results.append({
                "name": region,
                "ipAddress": None,
                "ipsForService": ", ".join(ips_for_region),
                "score": score
            })
    
        def sort_key(result):
            starts_with = result["name"].lower().startswith(query.lower())
            return (not starts_with, -result["score"])
        
        scored_results.sort(key=sort_key)
        
        # Adjust threshold based on query length
        threshold = 45 if len(query) > 5 else 50
        
        results = [result for result in scored_results if result["score"] >= threshold]
    
        # Limit the number of results
        results = results[:20]
    
        return jsonify({"results": results})

# Run the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)