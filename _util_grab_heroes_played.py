# /heroes/lycanthrope/tooltip
page = "https://dotabuff.com/players/"
page_post = "/heroes"


from heroes import heroes
from urls import urls
import mechanize
import string
import re
import pprint
pp = pprint.PrettyPrinter(indent = 4)
import argparse

parser = argparse.ArgumentParser(description='grab heroes played for an id')
parser.add_argument('id', help='player id')
parser.add_argument('--wr', help='winrate threshold', default=35)
parser.add_argument('--gp', help='games played threshold', default=5)
args = parser.parse_args()
print args

# override mechanize's history behavior
class NoHistory(object):
  def add(self, *a, **k): pass
  def clear(self): pass



br = mechanize.Browser(factory=mechanize.RobustFactory(), history=NoHistory())

roles = {}
url = page+args.id+page_post
print url
response = br.open(url)

data = response.read()

data = data.replace('&#x27;', "'")

# we want to rip out matches played and winrate
regex = 'class="hero-link">([\w\-\s\d\']*)<\/a><\/td><td><div>(\d*)<\/div><div><div class="bar bar-default"><div class="segment segment-game" style="width: [\d]*\.[\d]*%"><\/div><\/div><\/div><\/td><td><div>([\d]*\.[\d]*)%'
match = re.findall(regex, data)

heroes = []
for a in match:
  if float(a[2]) >= args.wr:
    if float(a[1]) >= args.gp:
      heroes += [a[0]]




pp.pprint(heroes)


