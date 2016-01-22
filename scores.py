import requests
import html
import datetime as dt
import argparse

TODAY = dt.date.today().strftime('%Y%m%d')

TODAY = dt.date.today()

parser = argparse.ArgumentParser(description='Get live NBA game updates.')
parser.add_argument('--d', dest="date", type=str,
                    help='the date for which scores will be shown (default: today)')
parser.add_argument('--a', dest='show_all', action='store_true',
                    help='choose to see all scores for given date (default: False)')
parser.set_defaults(show_all=False, date=TODAY)

args = parser.parse_args()
score_date, show_all = args.date, args.show_all  # default to TODAY, False if None


def serve(date):
    games = parse(fetch(validate_date(date)))

    # no games
    if len(games) == 0:
        return 'No games for provided date'

    if show_all:
        return stringify_all(games)

    prompt = ''
    for i in range(len(games)):
        prompt += '{0}: {1} @ {2} \n'.format(
            i + 1, games[i]['visitor']['abbr'], games[i]['home']['abbr'])
    prompt += '>>> '

    choice = input(prompt)
    while not choice.isnumeric() or int(choice) not in range(0, len(games) + 1):
        choice = input(prompt)

    if int(choice) ==  0:
        return stringify_all(games)
    else:
        return stringify_single(games[int(choice) - 1])


def validate_date(date):
    '''Determine if arg date is valid, else return TODAY.'''

    if date == 'y':
        return (TODAY - dt.timedelta(1)).strftime('%Y%m%d')

    try:
        dt.datetime.strptime(date, '%Y%m%d').date()
    except ValueError:
        return TODAY.strftime('%Y%m%d')

    return date


def fetch(date):
    return requests.get(URL.format(date)).json()


def parse(response):
    games = []
    for game in response['sports_content']['games']['game']:
        g = {
            'loc': '{} - {}, {}'.format(game['arena'], game['city'], game['state']),
            'date': game['date'], 'time': game['time'],
            'period_status': game['period_time']['period_status'],
            'game_clock': game['period_time']['game_clock']
        }
        g['status'] = '{} - {}'.format(g['period_status'], g['game_clock'])
        if g['game_clock'] == '' or g['period_status'] == 'Final':
            g['status'] = g['period_status']
        for team in ('visitor', 'home'):
            g[team] = {
                'abbr': game[team]['abbreviation'], 'city': game[team]['city'],
                'name': game[team]['nickname'], 'score': game[team]['score']
            }
        games.append(g)
    return games


def stringify_all(games):
    output = ''
    for game in games:
        team_1, score_1 = game['visitor']['name'].ljust(14), game['visitor']['score'].rjust(3)
        team_2, score_2 = game['home']['name'].rjust(14), game['home']['score'].ljust(3)
        output += '{} {} : {} {} [{}]\n'.format(team_1, score_1, score_2, team_2, game['status'])
    return html.unescape(output)


def stringify_single(game):
    team_1, score_1 = game['visitor']['name'], game['visitor']['score']
    team_2, score_2 = game['home']['name'], game['home']['score']
    output = '{} {} : {} {} [{}]'.format(team_1, score_1, score_2, team_2, game['status'])
    return html.unescape(output)


if __name__ == '__main__':
    print(serve(score_date))