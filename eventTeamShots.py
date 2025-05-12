import requests

event_list = ['10385473']
for event in event_list:
    response1 = requests.get("https://api.sofascore.com/api/v1/event/" + event + "/shotmap")
    api1 = response1.json()
    counterTotalHome, counterTargetHome, counterBlockedHome, counterMissedHome = 0, 0, 0, 0
    counterTotalAway, counterTargetAway, counterBlockedAway, counterMissedAway = 0, 0, 0, 0
    for shot in api1["shotmap"]:
        if shot["situation"] != "shootout" and shot["isHome"] is True:
            counterTotalHome += 1
        if shot["situation"] != "shootout" and shot["isHome"] is False:
            counterTotalAway += 1
        if shot["situation"] != "shootout" and shot["isHome"] is True and shot["shotType"] in ("save", "goal"):
            counterTargetHome += 1
        if shot["situation"] != "shootout" and shot["isHome"] is False and shot["shotType"] in ("save", "goal"):
            counterTargetAway += 1
        if shot["situation"] != "shootout" and shot["isHome"] is True and shot["shotType"] in ("miss", "post"):
            counterMissedHome += 1
        if shot["situation"] != "shootout" and shot["isHome"] is False and shot["shotType"] in ("miss", "post"):
            counterMissedAway += 1
        if shot["situation"] != "shootout" and shot["isHome"] is True and shot["shotType"] == "block":
            counterBlockedHome += 1
        if shot["situation"] != "shootout" and shot["isHome"] is False and shot["shotType"] == "block":
            counterBlockedAway += 1
    response2 = requests.get("https://api.sofascore.com/api/v1/event/" + event + "/statistics")
    api2 = response2.json()
    period = next(p for p in api2["statistics"] if p["period"] == "ALL")
    shotgroup = next(g for g in period["groups"] if g["groupName"] == "Shots")
    total_shots = next(s for s in shotgroup["statisticsItems"] if s["name"] == "Total shots")
    target_shots = next(t for t in shotgroup["statisticsItems"] if t["name"] == "Shots on target")
    missed_shots = next(m for m in shotgroup["statisticsItems"] if m["name"] == "Shots off target")
    blocked_shots = next(b for b in shotgroup["statisticsItems"] if b["name"] == "Blocked shots")
    if counterTotalHome == int(total_shots["home"]) or counterTotalAway == int(total_shots["away"]):
        print(event, counterTotalHome, total_shots["home"], counterTotalAway, total_shots["away"])
    if counterTargetHome == int(target_shots["home"]) or counterTargetAway == int(target_shots["away"]):
        print(event, counterTargetHome, target_shots["home"], counterTargetAway, target_shots["away"])
    if counterMissedHome == int(missed_shots["home"]) or counterMissedAway == int(missed_shots["away"]):
        print(event, counterMissedHome, missed_shots["home"], counterMissedAway, missed_shots["away"])
    if counterBlockedHome == int(blocked_shots["home"]) or counterBlockedAway == int(blocked_shots["away"]):
        print(event, counterBlockedHome, blocked_shots["home"], counterBlockedAway, blocked_shots["away"])