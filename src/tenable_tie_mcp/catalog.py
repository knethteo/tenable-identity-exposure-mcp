"""Resource catalog for the Tenable Identity Exposure API.

Paths here were verified against a live TIE instance (v3.120.1 SaaS).
Flat resources support generic CRUD via `tie_resource_action`.
Nested resources (deviances, attacks, alerts lists, scores, widgets) live
under parent paths and are exposed through dedicated tools in server.py.
"""

from __future__ import annotations

# Flat resources: (path, supports_get_by_id, description)
# All verified to return HTTP 200 on a live instance.
TIE_RESOURCES: dict[str, tuple[str, bool, str]] = {
    "about":                ("/api/about",                 False, "Product version and build info"),
    "ad-objects":           ("/api/ad-objects",            True,  "Active Directory objects (users, computers, groups, OUs)"),
    "api-key":              ("/api/api-key",               False, "Current API key info"),
    "application-settings": ("/api/application-settings",  False, "Global application settings (GET/PATCH)"),
    "attack-type-configuration": ("/api/attack-type-configuration", False, "Attack type configuration (GET/PATCH)"),
    "attack-types":         ("/api/attack-types",          True,  "Attack (IoA) type definitions"),
    "categories":           ("/api/categories",            True,  "Indicator of Exposure (IoE) categories"),
    "checkers":             ("/api/checkers",              True,  "IoE checker definitions"),
    "cloud-statistics":     ("/api/cloud-statistics",      False, "Cloud deployment statistics"),
    "dashboards":           ("/api/dashboards",            True,  "Dashboard definitions"),
    "directories":          ("/api/directories",           True,  "Monitored AD directories"),
    "email-notifiers":      ("/api/email-notifiers",       True,  "Email notification configurations"),
    "infrastructures":      ("/api/infrastructures",       True,  "Monitored AD forests / infrastructures"),
    "ldap-configuration":   ("/api/ldap-configuration",    False, "LDAP bind configuration"),
    "license":              ("/api/license",               False, "License information"),
    "lockout-policy":       ("/api/lockout-policy",        False, "Account lockout policy"),
    "preferences":          ("/api/preferences",           False, "Current user preferences"),
    "profiles":             ("/api/profiles",              True,  "Security profiles (scope for IoE/IoA data)"),
    "reasons":              ("/api/reasons",               True,  "Deviance closure reasons"),
    "report-access-token":  ("/api/report-access-token",   False, "Token for embedded report access"),
    "roles":                ("/api/roles",                 True,  "Console user roles and permissions"),
    "saml-configuration":   ("/api/saml-configuration",    False, "SAML SSO configuration"),
    "syslogs":              ("/api/syslogs",               True,  "Syslog forwarding configurations"),
    "users":                ("/api/users",                 True,  "Console user accounts"),
}

# Nested resources exposed via dedicated tools. Documented here for discovery.
NESTED_ENDPOINTS: dict[str, str] = {
    "attacks":             "GET  /api/profiles/{profileId}/attacks   (requires resourceType + resourceValue)  -> use tie_attacks",
    "deviances (checker)": "POST /api/profiles/{profileId}/checkers/{checkerId}/deviances                     -> use tie_deviances_by_checker",
    "deviances (dir)":     "GET  /api/infrastructures/{infraId}/directories/{dirId}/deviances                 -> use tie_deviances_by_directory",
    "deviances (changed)": "GET  /api/deviances/changed   (bulk cursor-paginated stream)                      -> use tie_deviances_bulk",
    "alerts (list)":       "GET  /api/profiles/{profileId}/alerts                                             -> use tie_alerts",
    "alerts (single)":     "GET/PATCH /api/alerts/{id}                                                        -> use tie_request",
    "scores":              "GET  /api/profiles/{profileId}/scores                                             -> use tie_scores",
    "topology":            "GET  /api/profiles/{profileId}/topology  (AD trusts / relationships)             -> use tie_topology",
    "events (search)":     "POST /api/events/search  (needs profileId, directoryIds, dateStart/End)          -> use tie_search_events",
    "whoami":              "GET  /api/users/whoami   (current user + permissions)                            -> use tie_whoami",
    "widgets":             "GET/POST/PATCH/DELETE /api/dashboards/{dashboardId}/widgets[/{id}]               -> use tie_request",
    "checker-options":     "GET/POST /api/profiles/{profileId}/checkers/{checkerId}/checker-options          -> use tie_request",
    "attack-type-options": "GET/POST /api/profiles/{profileId}/attack-types/{attackTypeId}/attack-type-options -> use tie_request",
    "reasons (checker)":   "GET  /api/profiles/{profileId}/checkers/{checkerId}/reasons                       -> use tie_request",
    "ad-objects (search)": "POST /api/profiles/{profileId}/checkers/{checkerId}/ad-objects/search             -> use tie_request",
    "relays (linking)":    "GET  /api/relays/linking-key   (relay setup key)                                  -> use tie_request",
}


def catalog_as_text() -> str:
    lines = ["Flat resources (use with tie_resource_action):\n"]
    for name, (path, has_id, desc) in sorted(TIE_RESOURCES.items()):
        id_note = "  [get-by-id]" if has_id else ""
        lines.append(f"  {name:<22} {path:<32} {desc}{id_note}")
    lines.append("\nNested resources (use the dedicated tools noted):\n")
    for name, doc in NESTED_ENDPOINTS.items():
        lines.append(f"  {name:<20} {doc}")
    return "\n".join(lines)
