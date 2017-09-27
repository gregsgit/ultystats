#!/usr/bin/env python3

import csv
import json
import sys
import re

players = {}

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

def usage():
    print("""Usage: {} <filename>.
       will read <filename>.json according to format described in README, 
       and will generate <filename>.csv with rows for each player and
       columns for defensive plays, throws, bad throws, throwing percentage, drops, 
       catch percentage, assists, and scores.
    """.format(argv[0]))
    sys.exit()

def main(fname):
    with open("{}.json".format(fname), 'r') as f:
        data = json.load(f)
        plays = data['game']['plays']
        us_score = 0
        them_score = 0
        for play in plays:
            if isinstance(play, dict) and 'note' in play:
                print("note: {}".format(play['note']))
            elif play == "V":
                them_score = them_score + 1
            elif play == "T":
                print("timeout")
            elif isinstance(play, list):
                tcount = 0          # number of throws
                player = ""
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
                        player = re.match("D-(.*)", t).group(1)
                        increment_ds(player)
                    # score: 
                    elif tcount == len(play) and re.match("(.*)-!", t):
                        player = re.match("(.*)-!", t).group(1)
                        increment_scores(player)
                        increment_assists(prev)
                        us_score = us_score + 1
                    # drop:
                    elif tcount == len(play) and re.match("(.*)-D", t):
                        player = re.match("(.*)-D", t).group(1)
                        increment_drops(player)
                    # bad throw:
                    elif tcount == len(play) and t == "X":
                        player = "" # not strictly necessary 
                        increment_bad_throws(prev)
                    # a receiver who then throws
                    else:
                        player = t
                        increment_catches(player)
                        increment_throws(player)

    print("Final score: Us = {}, Them = {}.".format(us_score, them_score))


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
