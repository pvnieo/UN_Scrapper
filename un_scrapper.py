import re
from collections import defaultdict
from itertools import islice
import urllib
import bs4
from tqdm import tqdm


regex = re.compile(r"\[\d+\]")
root_url = 'http://en.wikipedia.org'
page_url = root_url + '/wiki/Member_states_of_the_United_Nations'

def get_description(url):
  with urllib.request.urlopen(url) as response:
    country = response.read()
    soup = bs4.BeautifulSoup(country, "lxml")
    return regex.sub("", soup.find("div", {'class': 'mw-parser-output'}).find_all('p')[1].get_text())

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
    name = cols[1].get_text()
    url = root_url + cols[1].find_all("a")[0].get("href")
    date_of_admission = cols[2].find_all("span")[1].get_text()
    country_infos[name] = {"birth": date_of_admission, "url": url}

  for url, name in tqdm(list(map(lambda x: (x[1]["url"], x[0]), country_infos.items()))):
    country_infos[name]['description'] = get_description(url)
  dump(country_infos)


if __name__ == "__main__":
  main()