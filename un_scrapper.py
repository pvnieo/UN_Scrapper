import re
from collections import defaultdict
from itertools import islice, filterfalse
import urllib
import bs4
from tqdm import tqdm


regex = re.compile(r"\[\d+\]")
regex2 = re.compile(r"(\[.+\])|(\s+\(.+\))")
regex3 = re.compile(r".+\/(?P<name>[^\/]+)")
regex4 = lambda s, n: re.compile(r"(((t|T)he )?{})|{}".format(s, n))
root_url = 'http://en.wikipedia.org'
page_url = root_url + '/wiki/Member_states_of_the_United_Nations'

def get_description(url, name):
  with urllib.request.urlopen(url) as response:
    country = response.read()
    soup = bs4.BeautifulSoup(country, "lxml")
    condition = lambda s: not regex4(regex3.match(url).group('name').split('_')[0], name).match(s)
    p_starting_with_country_name = list(filterfalse(condition, map(lambda x: x.get_text(), soup.find("div", {'class': 'mw-parser-output'}).find_all('p'))))
    return regex.sub("", p_starting_with_country_name[0])

def dump(countries):
  with open("UN-description.md", "w") as f:
    print("# Countries Of the united nations", file=f)
    for country, info in countries.items():
      print("## {} (_{}_)".format(country, info["birth"]), file=f)
      print('\t{}'.format(info['description'].replace('\n', '\n\t')), file=f)

def main():
  with urllib.request.urlopen(page_url) as response:
    html = response.read()
  soup = bs4.BeautifulSoup(html, "lxml")
  country_infos = defaultdict(dict)
  countries = soup.find("table", {'class': 'sortable'})

  for row in islice(countries.find_all("tr"), 1, None):
    cols = row.find_all("td")
    name = regex2.sub('', cols[1].get_text())
    url = root_url + cols[1].find_all("a")[0].get("href")
    date_of_admission = cols[2].find_all("span")[1].get_text()
    country_infos[name] = {"birth": date_of_admission, "url": url}

  for url, name in tqdm(list(map(lambda x: (x[1]["url"], x[0]), country_infos.items()))):
    country_infos[name]['description'] = get_description(url, name)
  dump(country_infos)


if __name__ == "__main__":
  main()