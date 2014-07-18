from django.http import HttpResponse,StreamingHttpResponse
from django.shortcuts import render
from github import Github
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from credentials import my_password,my_pseudo

import urllib, urllib2,json




def index(request):
	return render(request,'index.html')

def auth(request):
	if request.GET:
		url = 'https://github.com/login/oauth/access_token'
		values = {
				'client_id':'c8a11750567e610af115', 
		        'client_secret':'f2fdfc313af22b5ab62f510f69c75b6895b70f18',
		        'code':request.GET.get('code')
		        }

	data = urllib.urlencode(values)
	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)
	the_page = response.read()
	return HttpResponse(the_page)

def datas(request):
	l_commits=[]
	g= Github(my_pseudo,my_password)
	user = g.get_user()
	repos = user.get_repos()
	repos=[repos[0],repos[1]]
	for repo in repos:
		commits=repo.get_commits()
		for commit in commits:
			s_commit=repo.get_commit(commit.sha)
			author=s_commit.commit.author.name
			date=s_commit.commit.author.date
			c_files=s_commit.files
			for c_file in c_files:
				l_commits.append({'repo':repo.name,'file':c_file.filename,'commit':commit.sha,'author':author,'timestamp':date})
	
	context = RequestContext(request,{'request': request,'repos':l_commits,'error':False})
	return render_to_response('index2.html',context_instance=context)



def easy(request):
	if request.method == 'POST':
		stack=[]
		try:
			pseudo=request.POST.get('your_user')
			password=request.POST.get('your_password')		
		except:
			print('error')
			pass

		try:
			g = Github(pseudo,password)
			stack=[]
			for repo in g.get_user().get_repos():
				stack.append(repo.name)
		except:
			pass

		if stack.count > 0:
			context = RequestContext(request,{'request': request,'repos':stack,'error':False})
		else:
			context = RequestContext(request,{'request': request,'repos':'test','error':True})
	else:
		context = RequestContext(request,{'request': request,'repos':'test','error':True})

	return render_to_response('index2.html',context_instance=context)
