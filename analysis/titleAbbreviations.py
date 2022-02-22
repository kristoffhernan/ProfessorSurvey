
import requests
import re


def getAbbreviations():
    # api parameters
    params = {
        'action': 'parse',
        'page': 'Appendix:Academic degrees',
        'prop': 'wikitext',
        'format': 'json',
    }

    # request the api
    r = requests.get("https://wiktionary.org/w/api.php",
                     params=params, headers={'accept': 'application/json'})

    data = r.json()

    list = data['parse']['wikitext']['*']

    abbr = re.findall("\[([^:[\]]*)\]", list)

    return abbr


def main():
    abbr = getAbbreviations()
    print(abbr)


main()
