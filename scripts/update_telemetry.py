"""Generate a compact GitHub mission telemetry SVG from the public GitHub REST API.

Uses only Python's standard library. Run with GITHUB_TOKEN set from GitHub Actions;
no personal access token, external package, or secret committed to the repo.
For local preview: python scripts/update_telemetry.py --offline
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

USER='ayush-khatrii'
OUT=Path(__file__).resolve().parents[1]/'assets'/'telemetry.svg'


def api(path):
    token=os.getenv('GITHUB_TOKEN','')
    headers={'Accept':'application/vnd.github+json','User-Agent':'stellar-profile-telemetry', 'X-GitHub-Api-Version':'2022-11-28'}
    if token:headers['Authorization']=f'Bearer {token}'
    req=Request('https://api.github.com'+path,headers=headers)
    with urlopen(req,timeout=25) as r:
        return json.loads(r.read().decode('utf-8'))


def text(x,y,value,sz=20,clr='#e8f4ff',weight=600,mono=False,anchor=None):
    family="'DejaVu Sans Mono',ui-monospace,monospace" if mono else "'DejaVu Sans',Arial,sans-serif"
    attrs=f' text-anchor="{anchor}"' if anchor else ''
    return f'<text x="{x}" y="{y}" fill="{clr}" font-family="{family}" font-size="{sz}" font-weight="{weight}"{attrs}>{escape(str(value))}</text>'


def truncate(s,n):
    return s if len(s)<=n else s[:n-1]+'…'


def render(info):
    width,height=1200,160
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="GitHub public profile telemetry">',
       '<style>@keyframes beacon{0%,100%{opacity:.3}50%{opacity:1}} .beacon{animation:beacon 2.2s ease-in-out infinite} @keyframes signal{0%,100%{opacity:.4}50%{opacity:1}} .signal{animation:signal 3.4s ease-in-out infinite}</style>',
       '<defs>',
       '<linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#080f21"/><stop offset=".68" stop-color="#10203a"/><stop offset="1" stop-color="#1e1a43"/></linearGradient>',
       '<linearGradient id="line"><stop stop-color="#4ad9ef"/><stop offset="1" stop-color="#b39aff"/></linearGradient>',
       '<filter id="gl"><feGaussianBlur stdDeviation="4"/></filter>',
       '</defs>',
       '<rect x="1" y="1" width="1198" height="158" rx="15" fill="url(#bg)" stroke="#344969"/>',
       '<rect x="24" y="20" width="4" height="23" rx="2" fill="#50d8ec"/>',
       text(42,37,'MISSION TELEMETRY',14,'#cbf6ff',700,True),
       text(1170,36,'GITHUB / PUBLIC',12,'#8fb4ce',500,True,'end'),
       '<line x1="28" y1="56" x2="1172" y2="56" stroke="#304862"/>',
    ]
    fields=[('PUBLIC REPOSITORIES',info['repos']),('FOLLOWERS',info['followers']),('STARS RECEIVED',info['stars']),('RECENTLY UPDATED',info['recent'])]
    widths=[260,230,250,394]
    x=30
    for i,((label,val),wd) in enumerate(zip(fields,widths)):
        svg.append(text(x,84,label,12,'#89b4d0',500,True))
        svg.append(text(x,121,truncate(str(val),27 if i==3 else 13),24 if i<3 else 21,'#f1f7ff',700))
        if i<3:svg.append(f'<line x1="{x+wd-17}" y1="75" x2="{x+wd-17}" y2="131" stroke="#34516e"/>')
        x+=wd
    svg.extend([f'<rect class="signal" x="30" y="145" width="1140" height="2" rx="1" fill="url(#line)" opacity="0.75"/>',
                '<circle class="beacon" cx="1015" cy="30" r="3.5" fill="#65f4c8"/>',
                '</svg>'])
    return '\n'.join(svg)+'\n'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');a=parser.parse_args()
    if a.offline:
        data={'repos':'—','followers':'—','stars':'—','recent':'AWAITING FIRST SYNC'}
    else:
        user=api('/users/'+USER)
        repos=[]
        page=1
        while True:
            res=api(f'/users/{USER}/repos?per_page=100&page={page}&type=owner&sort=updated')
            repos+=res
            if len(res)<100:break
            page+=1
            if page>20:raise RuntimeError('More than 2,000 repos; pagination guard.')
        public=[r for r in repos if not r.get('private') and not r.get('fork')]
        most_recent=next((r.get('name','') for r in repos if not r.get('private')),'—')
        data={'repos':user.get('public_repos','—'),'followers':user.get('followers','—'),
              'stars':sum(int(r.get('stargazers_count',0)) for r in public),'recent':most_recent}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(render(data),encoding='utf-8')
    print('Telemetry generated:',OUT,' | ',data)

if __name__=='__main__':main()
