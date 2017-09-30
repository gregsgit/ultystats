#!/usr/bin/env python3

import csv
import json
import sys
import re

players = {}
abbrevs = {}

# note that 'throws' includes both bad and good throws.
# whereas 'catches' is only good catches (didn't drop).

def incr_player(player, key):
    if not player in players:
        players[player] = { 'name' : player, 'ds' : 0, 
                            'throws' : 0, 'bad_throws' : 0, 
                            'catches' : 0, 'drops' : 0, 
                            'assists' : 0, 'scores' : 0}
        players[player][key] = 1
    else:
        players[player][key] = players[player][key] + 1

def increment_ds(player):
    incr_player(player, 'ds')

def increment_throws(player):
    incr_player(player, 'throws')
    
def increment_bad_throws(player):
    incr_player(player, 'bad_throws')

def increment_catches(player):
    incr_player(player, 'catches')

def increment_drops(player):
    incr_player(player, 'drops')

def increment_assists(player):
    incr_player(player, 'assists')

def increment_scores(player):
    incr_player(player, 'scores')

def x(abbrev):
    if abbrev in abbrevs:
        return abbrevs[abbrev]
    else:
        print("{} not in abbrevs".format(abbrev))
        return abbrev

def usage():
    print("""Usage: {} <filename>.
       will read <filename>.json according to format described in README, 
       and will generate <filename>.csv with rows for each player and
       columns for defensive plays, throws, bad throws, throwing percentage, drops, 
       catch percentage, assists, and scores.
    """.format(argv[0]))
    sys.exit()

def main(fname):
    global players
    global abbrevs
    with open("{}.json".format(fname), 'r') as f:
        data = json.load(f)
        game = data['game']
        if 'abbrevs' in game:
            abbrevs = game['abbrevs'] 
        plays = game['plays']
        us_score = 0
        them_score = 0
        us_turns = 0
        them_turns = 0
        last_play = ""          # used for deducing turnovers
        for play in plays:
            if isinstance(play, dict) and 'note' in play:
                print("note: {}".format(play['note']))
            elif play == "V":
                them_score = them_score + 1
                print("opponents score ({}-{})".format(us_score, them_score))
                last_play = "V"
            elif play == "T":
                print("timeout")
            elif isinstance(play, list):
                # curious fact: if last play was a list, and now we have another
                #    list, the opponents must have lost possession.
                # that's because all lists end in either "-D" (for drop),
                # "-!" (for score), or "X" (for bad throw), all of which result in
                # opponent having possession.
                if isinstance(last_play, list):
                    print("turnover by opponent")
                    them_turns = them_turns + 1
                tcount = 0          # number of throws
                player = ""
                last_play = play
                for t in play:  # t for "throw"
                    tcount = tcount + 1
                    prev = player
                    if isinstance(t, dict) and 'note' in t:
                        print("play note: {}".format(t['note']))
                    elif not isinstance(t, str):
                        # what is this? not a string
                        print("Unidentified element (not a string) of play sequence: {}".format(t))
                        sys.exit()
                    # defensive play:
                    elif tcount == 1 and re.match("D-(.*)", t):
                        player = x(re.match("D-(.*)", t).group(1))
                        increment_ds(player)
                        print("Defensive play by {}!".format(player))
                        player = ""
                    # score: 
                    elif tcount == len(play) and re.match("(.*)-!", t):
                        player = x(re.match("(.*)-!", t).group(1))
                        increment_scores(player)
                        increment_assists(prev)
                        us_score = us_score + 1
                        print("to {} for the SCORE! ({}-{})".
                              format(player, us_score, them_score))
                    # drop:
                    elif tcount == len(play) and re.match("(.*)-D", t):
                        player = x(re.match("(.*)-D", t).group(1))
                        print("to {} - dropped.".
                              format(player))
                        increment_drops(player)
                        us_turns = us_turns + 1
                    # bad throw:
                    elif tcount == len(play) and t == "X":
                        player = "" # not strictly necessary 
                        print("bad throw.")
                        increment_bad_throws(prev)
                        us_turns = us_turns + 1
                    # a receiver who then throws
                    else:
                        player = x(t)
                        if prev == "":
                            print("{}".format(player), end=" ")
                        else:
                            print("to {},". format(player), end=" ")
                        increment_catches(player)
                        increment_throws(player)

    print("Final score: Us = {}, Them = {}.".format(us_score, them_score))
    print("Total turnover by us: {}. Total turnovers by them: {}.".format(us_turns, them_turns))

    with open("{}.csv".format(fname), 'w') as csvfile:
        fieldnames = ['name', 'ds', 'throws', 'bad_throws', 'throw_percentage', 
                      'catches', 'drops', 'catch_percentage', 'assists', 'scores']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for name, stats in players.items():
            if stats['throws'] > 0:
                stats['throw_percentage'] = "{:.2f}".format((1 - (stats['bad_throws'] / stats['throws'])) * 100)
            else:
                stats['throw_percentage'] = 0
            if stats['catches'] > 0:
                stats['catch_percentage'] = "{:.2f}".format((stats['catches'] / (stats['catches'] + 
                                                                                stats['drops'])) * 100)
            else:
                stats['catch_percentage'] = 0
            writer.writerow(stats)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()                 # exits
    main(sys.argv[1])
