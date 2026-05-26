#!/usr/bin/env python3
"""
Apollo Research — Discovery Call Prep
Looks up a person and their company from an email address or name+domain.

Usage:
    python3 apollo_research.py "bruno.frade@okegroup.de"
    python3 apollo_research.py "Bruno" "Frade" "okegroup.de"

Output: JSON with person + company data for prep notes.

Requires: APOLLO_API_KEY environment variable
"""

import sys
import os
import json
import requests
import warnings
warnings.filterwarnings("ignore")

API_KEY = os.environ.get("APOLLO_API_KEY", "")
if not API_KEY:
    print(json.dumps({"error": "APOLLO_API_KEY environment variable not set"}))
    sys.exit(1)

BASE    = "https://api.apollo.io/api/v1"
HDRS    = {"Content-Type": "application/json", "Cache-Control": "no-cache", "X-Api-Key": API_KEY}

def person_match(first, last, domain, email=None):
    body = {"first_name": first, "last_name": last, "domain": domain,
            "reveal_personal_emails": True, "reveal_work_email": True}
    if email:
        body["email"] = email
    try:
        r = requests.post(f"{BASE}/people/match", headers=HDRS, json=body, timeout=15)
        if r.status_code == 200:
            return r.json().get("person", {})
    except Exception:
        pass
    return {}

def org_enrich(domain):
    try:
        r = requests.get(f"{BASE}/organizations/enrich", headers=HDRS,
                         params={"domain": domain}, timeout=15)
        if r.status_code == 200:
            org = r.json().get("organization", {})
            if org.get("name"):
                return org
    except Exception:
        pass
    return {}

def org_search_by_name(company_name):
    """Fallback: search by company name when domain enrichment fails."""
    try:
        r = requests.post(f"{BASE}/mixed_companies/search", headers=HDRS,
                          json={"q_organization_name": company_name, "per_page": 1}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            orgs = data.get("organizations") or data.get("accounts") or []
            if orgs:
                return orgs[0]
    except Exception:
        pass
    return {}

def main():
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "provide email or first last domain"}))
        sys.exit(1)

    # Parse args: either single email or first last domain
    if len(args) == 1 and "@" in args[0]:
        email = args[0]
        parts = email.split("@")
        domain = parts[1]
        # Try to split local part into first/last
        local = parts[0].replace(".", " ").replace("-", " ").replace("_", " ").split()
        first = local[0].capitalize() if local else ""
        last  = local[-1].capitalize() if len(local) > 1 else ""
    elif len(args) >= 3:
        first, last, domain = args[0], args[1], args[2]
        email = None
    else:
        print(json.dumps({"error": "usage: email OR first last domain"}))
        sys.exit(1)

    # If domain doesn't look like a real domain (no dot, or is a company name),
    # resolve it via company search first
    company_name_hint = args[3] if len(args) >= 4 else ""
    if "." not in domain:
        org = org_search_by_name(domain) or org_search_by_name(company_name_hint)
        if org.get("primary_domain"):
            domain = org["primary_domain"]
    else:
        org = {}

    person = person_match(first, last, domain, email)

    # Try enriching by email domain first; fall back to person's org domain if different
    if not org.get("name"):
        org = org_enrich(domain)
    if not org.get("name") and person.get("organization", {}).get("primary_domain"):
        org = org_enrich(person["organization"]["primary_domain"])
    if not org.get("name") and person.get("organization", {}).get("name"):
        org = org_search_by_name(person["organization"]["name"])
    if not org.get("name") and company_name_hint:
        org = org_search_by_name(company_name_hint)

    # Extract the fields we care about
    technologies = org.get("technologies", []) or []
    tech_names = [t.get("name", "") for t in technologies if t.get("name")][:8]

    result = {
        "person": {
            "name":       f"{person.get('first_name',first)} {person.get('last_name',last)}".strip(),
            "title":      person.get("title", ""),
            "seniority":  person.get("seniority", ""),
            "linkedin":   person.get("linkedin_url", ""),
            "email":      person.get("email", ""),
            "city":       person.get("city", ""),
            "country":    person.get("country", ""),
        },
        "company": {
            "name":             org.get("name", ""),
            "domain":           domain,
            "industry":         org.get("industry", ""),
            "sub_industry":     org.get("subindustry", ""),
            "headcount":        org.get("estimated_num_employees", ""),
            "revenue":          org.get("estimated_annual_revenue", ""),
            "description":      org.get("short_description", ""),
            "hq_city":          org.get("city", ""),
            "hq_country":       org.get("country", ""),
            "founded":          org.get("founded_year", ""),
            "technologies":     tech_names,
            "keywords":         (org.get("keywords") or [])[:6],
        }
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
