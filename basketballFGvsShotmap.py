from datetime import datetime, timedelta
import psycopg2
import requests

now = datetime.now()
last72h = (now - timedelta(hours=72)).strftime("%Y-%m-%d %H:%M:%S")

connDB = psycopg2.connect(database="sofascore", user="support", password="3F3tg9LwCKGQaN", host="127.0.0.1", port="5432")
cursor = connDB.cursor()
cursor.execute("select id from season where uniquetournament_id = 132 order by enddate desc limit 1")
season_id = str(cursor.fetchall()[0][0])
cursor.execute("select id from event where season_id = " + season_id + " and status_type = 'finished' and startdate > '" + last72h + "'")
event_list = cursor.fetchall()
conn.close()

for event in event_list:
    responseEvent = requests.get("https://www.sofascore.com/api/v1/event/" + event)
    apiEvent = responseEvent.json()
    homeTeamID, awayTeamID = apiEvent["event"]["homeTeam"]["id"], apiEvent["event"]["awayTeam"]["id"]
    eventTeams = [str(homeTeamID), str(awayTeamID)]
    responseStatistics = requests.get("https://api.sofascore.com/api/v1/event/" + event + "/statistics")
    apiStatistics = responseStatistics.json()
    period = next(p for p in apiStatistics["statistics"] if p["period"] == "ALL")
    statgroup = next(g for g in period["groups"] if g["groupName"] == "Scoring")
    fieldgoals = next(f for f in statgroup["statisticsItems"] if f["name"] == "Field goals")
    homeScored, homeShots = fieldgoals["homeValue"], fieldgoals["homeTotal"]
    awayScored, awayShots = fieldgoals["awayValue"], fieldgoals["awayTotal"]
    counterHomeShots, counterHomeMade = 0, 0
    counterAwayShots, counterAwayMade = 0, 0
    responseHomeShotmap = requests.get("https://api.sofascore.com/api/v1/event/" + event + "/shotmap/" + str(homeTeamID))
    responseAwayShotmap = requests.get("https://api.sofascore.com/api/v1/event/" + event + "/shotmap/" + str(awayTeamID))
    if responseHomeShotmap.status_code == 404 or responseAwayShotmap.status_code == 404:
        continue
    apiHomeTeamShotmap, apiAwayTeamShotmap = responseHomeShotmap.json(), responseAwayShotmap.json()
    for shot in apiHomeTeamShotmap["shotmap"]:
        counterHomeShots += shot["made"] + shot["missed"]
        if shot["made"] != 0: counterHomeMade += shot["made"]
    for shot in apiAwayTeamShotmap["shotmap"]:
        counterAwayShots += shot["made"] + shot["missed"]
        if shot["made"] != 0: counterAwayMade += shot["made"]
    if counterHomeShots != homeShots or counterAwayShots != awayShots:
        print(event, "HomeStatTotal: ",homeShots, "HomeShotmapTotal: ", counterHomeShots, "AwayStatTotal: ",awayShots, "AwayShotmapTotal: ",counterAwayShots)
    if counterHomeMade != homeScored or counterAwayMade != awayScored:
        print(event, "HomeStatScored: ",homeShots, "HomeShotmapMade: ",counterHomeShots, "AwayStatMade: ",awayShots, "AwayShotmapScored: ",counterAwayShots)
    print(counterHomeShots, counterHomeMade, homeShots, homeScored, counterAwayShots, counterAwayMade, awayShots, awayScored)












