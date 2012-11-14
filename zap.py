# Finalizer

from heroes import heroes
from lanes import lanes
from roles import roles
from roles import known_roles
from alpha import alpha
from rotation import rotation
from pickbans import pickbans
from unwon import unwon
from aliases import aliases
from ranged_heroes import ranged_heroes
from new_counters import new_counters
from initds import initds
from friends import friends
from underfive import underfive

from winrate_76c import winrate
from matchup_76c import matchup

import argparse
import pprint
import string
import math

# melee rangedx

pp = pprint.PrettyPrinter(indent = 4)

parser = argparse.ArgumentParser(description='lane advisor for dota2')
parser.add_argument('heroes', metavar='heroes', type=str, nargs='+', help='your team')
parser.add_argument('-e', '--enemy', metavar='enemy', type=str, nargs='+', help='the other team', default='')
parser.add_argument('-c', '--consider', type=str, help='special, alpha, unwon, or rotation, initds', default='special')
args = parser.parse_args()
pp.pprint(args)

def display_counters(eh, set):
    them = parse_heroes(eh)
    if them == []:
        return 0

    counterables = {}
    for h in alpha:
        counterables[h] = 0
    
    for h in them:
        for z in new_counters[h]:
            if z in set:
                counterables[z] += new_counters[h][z]

    sorted_counterables = sorted(counterables.iteritems(), key=lambda (k,v): (v,k), reverse=True)

    for k, v in sorted_counterables:
        if v>=3: # this is a good counter to the enemy hero
            print "   ",str(round(v,1)).rjust(5), str(k).ljust(20),
            for e in them:
                if e in new_counters[k]:
                    print str(round(-new_counters[k][e],1)).rjust(5),
                    print str(e),
            print

def melee_ranged(a):
    mod = 0
    if a["Melee"] >= 3:
        mod += -10 * (a["Melee"]-2)

    return mod

def matchup_mod(ah, eh):
    us = parse_heroes(ah)
    them = parse_heroes(eh)

    if us == []:
        return []

    if them == []:
        return []
    

    mod = []
    for h in us:
        minimod = []
        for e in them:
            minimod += [matchup[h][e]]
        mod += [numpy.average(minimod)]
    
    return mod

def winrate_mod(ah, eh):
    us = parse_heroes(ah)
    mod = []
    for h in us:
        mod += [winrate[h]]

    return mod


def nc_mod(h, eh):
    them = parse_heroes(eh)
    s =  0
    for e in them:
        s += matchup[h][e] - winrate[h]
#        s += - matchup[e][h] + winrate[e]
        
    if s < 0:
        s -= 10
    return s


def lane_mod(a, n_heroes = 0):
    mod = 0
    if a["Solo Mid"] < 1:
        mod += -25 # want a solo mid hero if we don't have one
    if a["Solo Mid"] >= 2:
        mod += (1-a["Solo Mid"]) # slight dissuade for multiple solo mids
    if a["Solo Side"] < 1:
        if a["Jungler"] > 0:
            mod += -25 # do not want a jungler if we have a solo side
    if a["Jungler"] >= 1:
        if a["Solo Side"] < 1:
            mod += -25 # want a solo side if we have a jungler
    if a["Hard Lane"] < 1:
        # always want at least a hard lane hero
        # unless we have a jungler and a solo side
        if not(a["Jungler"] > 0 and a["Solo Side"] > 0):
            mod += -25 
        
    
    # lane configs
    # mid, jungle, solo, two
    # or mid, top, hard hard
        
    # disable lane mod for now
    if n_heroes == 5:
        return mod

    mod = 0
      
    return mod
        

def utility_mod(a):
    modifier = 0
    factor = 5

    if a["Carry"] >= 3:
        modifier += -factor*factor*(a["Carry"]-2)
       
    if a["Jungler"] >= 2:
        modifier += -factor*factor*(a["Jungler"]-1)

       
    modifier += a["Support"]

    # want at least 1 carry
    if a["Carry"] < 1:
        modifier += -10

    # want at least 2 supports (and more is merrier)
    if a["Support"] >= 2:
        modifier += 2 * factor * a["Support"]

    # want at least a pusher (and more is merrier)
    if a["Pusher"] >= 1:
        modifier += factor * a["Pusher"]

    # want at least an initiator (and more is merrier)
    if a["Initiator"] >= 1:
        modifier += factor * a["Initiator"]

    # want at least 2 disablers (and more is merrier)
    if a["Disabler"] >= 2:
        modifier += factor * a["Disabler"]
    
        
         
    return modifier


def counter_mod(ah, eh):
    mod = 0
    us = parse_heroes(ah)
    them = parse_heroes(eh)
    if them == []:
        return 0
    
    for h in them:
        for z in new_counters[h]:
            if z in us:
                mod += new_counters[h][z]
        
    return mod

def pickban_mod(ah):
    mod = 0

    infog = {}
    for h in parse_heroes(ah):
        infog[h] = pickbans.index(h)

    cutoff = math.ceil((float(len(alpha))/5))
    for h in parse_heroes(ah):
        tier = math.ceil(float(infog[h]+1)/cutoff)
        mod += (math.ceil(tier)-1)

    # calculate tier
  
        

    return -mod*2

def get_hero_tier(hero):
    cutoff = math.ceil(float(len(alpha))/5)
    tier = math.ceil(float(pickbans.index(hero)+1)/cutoff)
    return int(tier)

    



def radar_area(a):
    a = a.values()
    area = 0
    i = 0
    for i in range(1, len(a)):
        area += a[i-1] * a[i] * math.sin(2 * math.pi / len(a)) * 0.5
    area += a[len(a)-1] * a[0] * math.sin(2*math.pi/len(a)) * 0.5

    return area 


def lane_check(a):
    print
    if a["Solo Mid"] < 1:
        print "*** No Solo Mid"
    if a["Jungler"] >= 1 and a["Solo Side"] < 1:
        print "*** Jungler(s) but no Solo Side"        
    if a["Solo Side"] < 1 and a["Jungler"] < 1:
        print "*** No Solo Side (Do not pick a Jungler)"
    if a["Hard Lane"] < 1:
        print "*** No Hard Lane"
    print

def lane_analysis(ah):
    la = {}
    la["Jungler"] = 0
    la["Solo Mid"] = 0
    la["Solo Side"] = 0
    la["Hard Lane"] = 0
    la["Lane Support"] = 0
    us = parse_heroes(ah)
    for h in us:
        if "Jungler" in roles[h]:
            # is there a jungler?
            la["Jungler"] += 1
        if h in lanes["Solo Mid"]:
            la["Solo Mid"] += 1
        if h in lanes["Solo Side"]:
            la["Solo Side"] += 1
        if h in lanes["Hard Lane"]:
            la["Hard Lane"] += 1
        if "Lane Support" in roles[h]:
            la["Lane Support"] += 1
    return la

def melee_ranged_analysis(ah):
    mra = {}
    mra["Melee"] = 0
    mra["Ranged"] = 0
    us = parse_heroes(ah)
    for h in us:
        if h in ranged_heroes:
            mra["Ranged"] += 1
        else:
            mra["Melee"] += 1
    return mra


    

        

def parse_heroes(ah):
    us = []
    for i in range(0,5):
        if i < len(ah):
            h  = ah[i]
            hero = ""
            if h == "*" or h =="?":
                continue
            for z in heroes.itervalues():
                if h == z.lower():
                    hero = z
                elif h == z:
                    hero = z
            if h in aliases:
                hero = aliases[h]
            if hero == "":
                print "Unknown hero", h
                continue
            us += [hero]
    return us


def get_values(ah, verbose = False, enemy=False):
    us = parse_heroes(ah)

    usa = {}
    for k in known_roles:
        usa[k] = 0

    for u in us:
        if verbose:
            if enemy:
                print str("enemy").rjust(5),
            else:
                print str("").rjust(5),
            print str(u).ljust(20), 
            if u in lanes["Solo Mid"]:
                print "Solo Mid ",
            elif u in lanes["Solo Side"]:
                print "Solo Side",
            elif u in lanes["Hard Lane"]:
                print "Hard Lane",
            else:
                if "Jungler" in roles[u]:
                    print "Jungler  ",
                else:
                    print "         ",
            print get_hero_tier(u),
            print roles[u]


        for r in roles[u]:
            if r in usa:
                usa[r] += 1
            else:
                usa[r] = 1

    return usa


special = ["Chaos Knight",
           "Windrunner", 
           "Dark Seer",
           "Shadow Demon",
           "Enigma",
           "Venomancer"]

consider_these_heroes = []

if args.consider == "initds":
    consider_these_heroes = initds
elif args.consider == "alpha":
    consider_these_heroes = alpha
elif args.consider == "unwon":
    consider_these_heroes = unwon
elif args.consider == "rotation":
    consider_these_heroes = rotation
elif args.consider == "special" or args.consider=="alcaras" or args.consider=="alc":
    consider_these_heroes = special
elif args.consider == "underfive" or args.consider=="five":
    consider_these_heroes = underfive
elif args.consider in friends:
    consider_these_heroes = friends[args.consider]
else:
    print "unknown args.consider", args.consider
    exit()

ra = get_values(args.heroes, verbose=False)
la = lane_analysis(args.heroes)
mra = melee_ranged_analysis(args.heroes)
print args.consider, len(consider_these_heroes)

pp.pprint(ra) 
pp.pprint(la)
pp.pprint(mra)
if args.enemy != "":
    print
    get_values(args.enemy, verbose=True, enemy=True)
#    display_counters(args.enemy, consider_these_heroes)
    print 
else:
    print

get_values(args.heroes, verbose=True)
lane_check(la)
rai = radar_area(ra) + utility_mod(ra) + lane_mod(la, len(args.heroes)) + melee_ranged(mra) + counter_mod(args.heroes, args.enemy) + pickban_mod(args.heroes)


scores = {}

for hh in consider_these_heroes:
    if hh in parse_heroes(args.heroes):
        continue
    if hh in parse_heroes(args.enemy):
        continue
    foo = get_values(args.heroes + [hh])
    fool = lane_analysis(args.heroes+[hh])
    foomra = melee_ranged_analysis(args.heroes+[hh])
    diff = (nc_mod(hh, args.enemy)*100+radar_area(foo)+utility_mod(foo)+lane_mod(fool, len(args.heroes+[hh]))+melee_ranged(foomra)+counter_mod(args.heroes+[hh], args.enemy) + pickban_mod(args.heroes+[hh])) - rai
    scores[hh] = diff

sorted_scores = sorted(scores.iteritems(), key=lambda (k,v): (v,k), reverse=True)

displayed = 10
for s in sorted_scores:
    if displayed == 0 or (s[1]<-500 and displayed < 4):
        break
    displayed -= 1
    print str(round(s[1],1)).rjust(7), str(s[0]).ljust(20), 
    if s[0] in lanes["Solo Mid"]:
        print "Solo Mid ",
    elif s[0] in lanes["Solo Side"]:
        print "Solo Side",
    elif s[0] in lanes["Hard Lane"]:
        print "Hard Lane",
    else:
        if "Jungler" in roles[s[0]]:
            print "Jungler  ",
        else:
            print "         ",
    print get_hero_tier(s[0]),
    print str(nc_mod(s[0], args.enemy)*100).rjust(6),
    print roles[s[0]]

    
                       

    


