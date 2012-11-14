# /heroes/lycanthrope/tooltip
page = "https://dotabuff.com/heroes/winning?date=current_patch"


from heroes import heroes
from urls import urls
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

roles = {}


response = br.open(page)

data = response.read()

data = data.replace('&#x27;', "'")

# we want to rip out winrates
regex = 'class="hero-link">([\w\-\s\d\']*)</a></td><td><div>([\d]*\.[\d]*)%'
match = re.findall(regex, data)

winrates = {}
for a in match:
  winrates[a[0]] = float(a[1])/100.0



pp.pprint(winrates)


