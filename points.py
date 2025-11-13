#!/usr/bin/env python3
import os, sys, requests
from collections import defaultdict

API = "https://fantasy.premierleague.com/api"
BOOTSTRAP = f"{API}/bootstrap-static/"
FIXTURES = lambda gw: f"{API}/fixtures/?event={gw}"
PICKS = lambda e, gw: f"{API}/entry/{e}/event/{gw}/picks/"

HDRS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://fantasy.premierleague.com/",
}

def get(url):
    r = requests.get(url, headers=HDRS, timeout=30)
    if r.status_code in (403, 404): return None
    r.raise_for_status()
    return r.json()

def fdr_mult(d):
    return {1:1.15, 2:1.08, 3:1.00, 4:0.93, 5:0.86}.get(int(d), 1.0)

def form(x):
    try: return float(x.get("form") or 0.0)
    except: return 0.0

def play_prob(x):
    p = x.get("chance_of_playing_next_round")
    try: return 1.0 if p is None else max(0, min(1, float(p)/100))
    except: return 1.0

def team_fixtures(fixtures):
    by = defaultdict(list)
    for f in fixtures or []:
        by[f["team_h"]].append({"opp": f["team_a"], "home": True,  "d": f.get("team_h_difficulty", 3)})
        by[f["team_a"]].append({"opp": f["team_h"], "home": False, "d": f.get("team_a_difficulty", 3)})
    return by

def public_picks(entry, gw):
    data = get(PICKS(entry, gw))
    if data and data.get("picks"): return gw, data["picks"]
    for g in range(gw-1, 0, -1):
        d = get(PICKS(entry, g))
        if d and d.get("picks"): return g, d["picks"]
    return None, []

def proj_gw(entry, gw):
    bs = get(BOOTSTRAP)
    if not bs:
        print("bootstrap-static failed", file=sys.stderr); return
    elements = {e["id"]: e for e in bs["elements"]}
    teams = {t["id"]: t for t in bs["teams"]}
    fixes = team_fixtures(get(FIXTURES(gw)) or [])
    gw_used, picks = public_picks(entry, gw)
    if not picks:
        print(f"[GW{gw}] no picks available publicly."); return

    cap = next((p["element"] for p in picks if p.get("is_captain")), None)
    tot = tot_c = 0.0

    print(f"\nFPL ID {entry} — GW{gw}")
    print("-"*88)
    print(f"{'Player':28}  {'Team':15}  {'Opponent(s)':30}  {'Prediction':>9}")
    print("-"*88)

    for p in picks:
        pid = p["element"]
        e = elements.get(pid)
        if not e: continue
        name = f"{e['first_name']} {e['second_name']}"
        t_id = e["team"]; t_name = teams[t_id]["name"]
        fm, prob = form(e), play_prob(e)
        fs = fixes.get(t_id, [])
        if not fs:
            xp, opps = 0.0, "—"
        else:
            xp, parts = 0.0, []
            for fx in fs:
                xp += fm * fdr_mult(fx["d"]) * prob
                parts.append(f"{teams[fx['opp']]['name']} ({'H' if fx['home'] else 'A'}, FDR {fx['d']})")
            opps = " + ".join(parts)
        c = " (C)" if pid == cap else ""
        print(f"{(name+c)[:28]:28}  {t_name[:15]:15}  {opps[:30]:30}  {xp:9.2f}")
        tot += xp; tot_c += xp * (2 if pid == cap else 1)

    print("-"*88)
    print(f"Squad total (no captain): {tot:.2f}")
    print(f"Squad total (with C x2):  {tot_c:.2f}")

if __name__ == "__main__":
    try:
        entry = int(input("FPL ID: ").strip())
    except Exception:
        print("Invalid FPL ID"); sys.exit(1)
    gws_in = input("Gameweek(s) (e.g. 12 or 14,15,16): ").strip()
    try:
        gws = sorted({int(x) for x in gws_in.split(",") if x.strip()})
    except Exception:
        print("Invalid GW list"); sys.exit(1)
    for gw in gws:
        proj_gw(entry, gw)
