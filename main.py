'''
WakaTime progress visualizer
'''

import re
import os
import base64
import datetime
import requests
from github import Github


START_COMMENT = '<!--START_SECTION:waka-->'
END_COMMENT = '<!--END_SECTION:waka-->'
listReg = f"{START_COMMENT}[\\s\\S]+{END_COMMENT}"
this_week = datetime.datetime.now().strftime('%W')

user = os.getenv('INPUT_USERNAME')
waka_key = os.getenv('INPUT_WAKATIME_API_KEY')
ghtoken = os.getenv('INPUT_GH_TOKEN')


def make_graph(percent: float):
    '''Make progress graph from API graph'''
    done_block = '█'
    empty_block = '░'
    pc_rnd = round(percent)
    return f"{done_block*int(pc_rnd/4)}{empty_block*int(25-int(pc_rnd/4))}"


def get_stats():
    '''Gets API data and returns markdown progress'''
    data = requests.get(
        f"https://wakatime.com/api/v1/users/current/stats/last_7_days?api_key={waka_key}").json()
    lang_data = data['data']['languages']
    data_list = []
    for l in lang_data[:5]:
        ln = len(l['name'])
        ln_text = len(l['text'])
        op = f"{l['name']}{' '*(12-ln)}{l['text']}{' '*(20-ln_text)}{make_graph(l['percent'])}   {l['percent']}"
        data_list.append(op)
    data = ' \n'.join(data_list)
    return '```text\n'+'Week #'+this_week+'\n'+data+'\n```'


def decode_readme(data: str):
    '''Decode the contets of old readme'''
    decoded_bytes = base64.b64decode(data)
    return str(decoded_bytes, 'utf-8')


def generate_new_readme(stats: str, readme: str):
    '''Generate a new Readme.md'''
    stats_in_readme = f"{START_COMMENT}\n{stats}\n{END_COMMENT}"
    return re.sub(listReg, stats_in_readme, readme)


if __name__ == '__main__':
    g = Github(ghtoken)
    repo = g.get_repo(f"{user}/{user}")
    contents = repo.get_readme()
    waka_stats = get_stats()
    rdmd = decode_readme(contents.content)
    new_readme = generate_new_readme(stats=waka_stats, readme=rdmd)
    if new_readme != rdmd:
        repo.update_file(path=contents.path, message='Updated with Dev Metrics',
                         content=new_readme, sha=contents.sha, branch='master')
