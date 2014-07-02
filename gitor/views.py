from django.http import HttpResponse,StreamingHttpResponse
from django.shortcuts import render
from github import Github

import urllib, urllib2




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

def easy(request):
	if request.method == 'POST':
		try:
			pseudo=request.POST.get('your_user')
			password=request.POST.get('your_password')		
		except:
			print('error')
			pass

		try:
			g = Github(pseudo, password)
			stack=[]
			for repo in g.get_user().get_repos():
				stack.append(repo.name)
		except:
			pass

		if stack.count > 0:
			return HttpResponse(stack)
		else:
			return HttpResponse('non')
	else:
		return HttpResponse('entrez vos credentials')