import requests
import json
import os

from pprint import pprint
from datetime import datetime, timedelta, timezone

booster_name = {
                    3: "Double Power", 12: "Triple Captain", 9: "Foreign Stars",    # Working Fine
                    10: "Indian Warriors", 11: "Free Hit",                          # Working Fine
                    1: "Wild Card", 2: "Game Changer",
}
API_KEY = os.getenv("CRICKET_API_KEY")
if not API_KEY:
    raise Exception("API key not found")
url_headers = '{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0"}'
headers = json.loads(url_headers)
headers.update({"Host": "fantasy.iplt20.com"})
headers.update({"Cookie": API_KEY})

with requests.session() as s:
    # # For getting match number:
    url_matches = "https://fantasy.iplt20.com/classic/api/live/score"
    res_matches = s.get(url_matches, headers=headers)
    matches = res_matches.json()['Data']['Value']['matches']
    teams = []

    for match in matches:
        # print(match)
        if match['event_state'] != 'R':
            teams.append(match['participants'][0]['short_name'])
            teams.append(match['participants'][1]['short_name'])
            match_number = int(match['event_name'].split(" ")[-1])
            # print(match['event_state'], match['participants'][0]['short_name'], match['participants'][1]['short_name'])
            print(f"Match {match_number}: {teams[0]} vs {teams[1]}: {match['start_date'].split('T')[0]}\n")
            # pprint(match)
            break
    print()
    # print(f"Match {match_number}: {teams[0]} vs {teams[1]}: {start_date}\n")
    # match_number
    # print(teams)

    # Get players list for current match
    url1 = f"https://fantasy.iplt20.com/classic/api/feed/gamedayplayers?lang=en&tourgamedayId={match_number}&teamgamedayId={match_number}"
    res = s.get(url1, headers=headers)
    players = res.json()['Data']['Value']['Players']
    curr_match_players = {}
    for player in players:
        if player['TeamShortName'] in teams:
            curr_match_players[player['Id']] = player['Name']
    # pprint(curr_match_players)
    # print(len(curr_match_players))

    # Get frnds names and player ids
    league_id_1 = 9340109 #Cricket Punters
    league_id_2 = 28750107 #Gully Boys
    url_punters_league = f"https://fantasy.iplt20.com/classic/api/user/leagues/6300106/leaderboard?optType=1&gamedayId={match_number}&phaseId=1&pageNo=1&topNo=100&pageChunk=100&pageOneChunk=100&minCount=9&leagueId={league_id_1}"
    res_league = s.get(url_punters_league, headers=headers)
    frnds = res_league.json()['Data']['Value']
    output = {}
    boosters_used_today = False
    output_boosters = []
    for frnd in frnds:
        url_frnds_team = f"https://fantasy.iplt20.com/classic/api/user/guid/lb-team-get?optType=1&gamedayId={match_number}&tourgamedayId={match_number}&teamId={frnd['temid']}&socialId={frnd['usrscoid']}"
        url_booster = f"https://fantasy.iplt20.com/classic/api/user/live/guid/lb-team/overall-get?optType=1&teamgamedayId={match_number}&arrtourGamedayId={match_number}&phaseId=1&teamId={frnd['temid']}&socialId={frnd['usrscoid']}"
        frnd_team = s.get(url_frnds_team, headers=headers).json()['Data']['Value']
        frnd_booster = s.get(url_booster, headers=headers).json()['Data']['Value']['teams'][0]['boosterid']
        if frnd_booster != 0:
            boosters_used_today = True
            output_boosters.append(f"{frnd['temname']} used booster: {booster_name[frnd_booster]}")

        if not frnd_team:
            print("Match not started yet!")
            break
        for player_id in frnd_team['plyid']:
            if player_id in curr_match_players:
                player_name = curr_match_players[player_id]

                ans = frnd['temname']
                if frnd_team['mcapt'] == player_id:
                    ans = ans + "(C)"
                if frnd_team['vcapt'] == player_id:
                    ans = ans + "(VC)"

                if player_name in output:
                    output[player_name].append(ans)
                else:
                    output[player_name] = [ans]

    res = {key: val for key, val in sorted(output.items(), key=lambda ele: len(ele[1]), reverse=True)}

    for player in res:
        print(f"{player} : {len(res[player])} : {res[player]}\n")

if res:
    print("--- Matchday Booster Usage Summary ---")
    if boosters_used_today:
        for op in output_boosters:
            print(op)
    else:
        print("No boosters reported used for this matchday")


india_tz = datetime.now(timezone(timedelta(hours=5, minutes=30)))
india_time = india_tz.strftime("%Y-%m-%d %H:%M:%S")
print(f"Last Updated on {india_time} IST")