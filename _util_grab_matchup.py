# /heroes/lycanthrope/tooltip
tooltip_stub = "https://dotabuff.com/heroes/"
tooltip_tail = "/matchups?date=current_patch"


from heroes import heroes
from urls import urls
import sys
import mechanize
import string
import re
import pprint
pp = pprint.PrettyPrinter(indent = 4)

# override mechanize's history behavior
class NoHistory(object):
  def add(self, *a, **k): pass
  def clear(self): pass



br = mechanize.Browser(factory=mechanize.RobustFactory(), history=NoHistory())

matchup = {}


for h in heroes.iterkeys():
    hn = heroes[h]
    if hn in urls:
        hn = urls[hn]
    hn = string.replace(hn, '-', '')
    hn = string.replace(hn, '\'', '')
    hn = string.replace(hn, ' ', '-')
    hn = hn.lower()
    url = tooltip_stub + hn + tooltip_tail
    print >> sys.stderr, url

    response = br.open(url)

    
    data = response.read()
    
    data = data.replace('&#x27;', "'")
    
    # we want to rip out winrates
    regex = 'class="hero-link">([\w\-\s\d\']*)</a></td><td><div>([\d]*\.[\d]*)%'
    match = re.findall(regex, data)
    
    winrates = {}
    for a in match:
      winrates[a[0]] = float(a[1])/100.0

    matchup[heroes[h]] = winrates

    print >> sys.stderr, heroes[h], winrates


pp.pprint(matchup)
