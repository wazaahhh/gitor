
from urllib2 import urlopen
import json
import re
import pandas as pd
from datetime import datetime
import time
import requests
import matplotlib
from scipy import stats
import sys

sys.path.append("/home/ubuntu/toyCode/sLibs/")
from tm_python_lib import *


#from settings import github_token
github_token = "819cb7cace7f4a01e41ac5d4e3a9f033c4c6bc15"

ISO8601 = "%Y-%m-%dT%H:%M:%SZ"

settings = {
            'project': 'sbenthall',
            'repo': 'bigbang',
            'github_token': github_token
            }

'''GitHub API functions'''
# from https://github.com/nipy/dipy/blob/master/tools/github_stats.py
element_pat = re.compile(r'<(.+?)>')
rel_pat = re.compile(r'rel=[\'"](\w+)[\'"]')

def parseLinkHeaders(headers):
    link_s = headers.get('link', '')
    urls = element_pat.findall(link_s)
    rels = rel_pat.findall(link_s)
    d = {}
    for rel,url in zip(rels, urls):
        d[rel] = url
    return d

def getPagedRequest(url):
    """get a full list, handling APIv3's paging"""
    results = []
    while url:
        print("fetching %s" % url)
        f = urlopen(url)
        results_json = json.load(f)
        if type(results_json) == list:
            results.extend(results_json)
        else:
            results.extend([results_json])
        
        links = parseLinkHeaders(f.headers)
        url = links.get('next')
        time.sleep(0.25)
    return results


'''Functions to Fetch from GitHub API'''
#print datetime.fromtimestamp(0).strftime(ISO8601) # for github since param
project_url = 'https://api.github.com/repos/{project}/{repo}'.format(**settings)

def getIssues(settings, project_url, state='all'):
    url = project_url + '/issues?access_token={0}&state={1}'.format(settings['github_token'],state)
    return getPagedRequest(url)

def getIssueComments(settings, project_url, issue_id):
    # GET /repos/:owner/:repo/issues/:number/comments
    url = project_url + '/issues/{0}/comments?access_token={1}'.format(
                                                                        issue_id,
                                                                        settings['github_token'])
    return getPagedRequest(url)

def getCommits(settings, project_url):
    # GET /repos/:owner/:repo/commits
    url = project_url + '/commits?access_token={0}'.format(settings['github_token'])
    return getPagedRequest(url)

def getCommitInfo(settings, project_url, sha):
    # GET /repos/:owner/:repo/commits/:sha
    url = project_url + '/commits/{0}?access_token={1}'.format(sha, settings['github_token'])
    #print json.load(urlopen(url))
    return getPagedRequest(url)
    
def getReleases(settings, project_url):
    # GET /repos/:owner/:repo/releases
    pass



'''Functions to Make Data Frames''' 

def createCommitsDataframe(commits_json):
    
    df = pd.DataFrame(commits_json)
#     if not refresh:
#         try:
#             print 'trying to open commits.json'
#             with open('commits.json') as infile:
#                 print 'reading commits.json'
#                 df = pd.read_json(infile)
#                 
#                 # put timestamp column datatime object
#                 df['timestamp'] = pd.to_datetime(df.timestamp)
#                 df.index = df.timestamp
#                 return df
#         except:
#             print 'no commits.json found, getting commits and creating DataFrame'
#             
#     if not commits_json:
#         commits_json = getCommits(settings, project_url)
#         df = pd.DataFrame(commits_json)
#         return df
    
    def addCommitAuthor(row):
        # Commit can have different committer and author
        if row['author']:
            if row['author']['login']:
                return row['author']['login']
            
    def addCommitStats(sha):
        ## API limit is 5000 per hour - TODO: slow  down our calls if we're going to hit
        # the limit
        commit = getCommitInfo(settings, project_url, sha)[0]
        return commit['stats']['additions'], commit['stats']['deletions']
    
    def addCommitDate(commit):
        return commit['author']['date']

    df['author_name'] = df.apply(addCommitAuthor, axis=1)
    ## Out until we can control staying within the API Limit
    #df['additions'], df['deletions'] = zip(*df.sha.apply(addCommitStats))
    df['timestamp'] = df['commit'].apply(addCommitDate)
    df['timestamp'] = pd.to_datetime(df.timestamp)
    df.index = df.timestamp
    #print df.head()
    return df

def uniquerAuthors(auth):
    return len(set([a for a in auth if a != None]))


def createBurstsDataframe(commits_df,t_resol='5D'):
    
    count_commits = commits_df.commit.resample(t_resol,how='count')
    count_authors = commits_df.author_name.resample(t_resol,how=uniquerAuthors)
    time  = count_commits.index.astype(np.int64) // 10**9 / 3600 / 24
    t0 = min(time)
    time = time - t0
    
    dico = { 'count_commits' : count_commits.values,"count_authors" : count_authors.values, 'time': time, 't0' : t0}
    #dico2 = { 'timestamp' : Time250[:-1], "beta" : beta, "p" : p, "r" : r}
    bursts_df = pd.DataFrame(dico,index=dico['time'])
    return bursts_df,dico


