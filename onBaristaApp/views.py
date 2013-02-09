# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from onBaristaApp.models import User

def login(request):
	if request.method == 'POST':

		username = request.POST['username']
		password = request.POST['password']
		try:
			user = User.objects.get(userName = username, password = password)

		except (KeyError,User.DoesNotExist):
			return render(request, 'login.html', {'error_message':"user name or password do not match our records.",})
		else:
			request.session['username'] = user.userName
			return render(request, 'home.html', {'user_name':user.userName,})
	else:
		return render(request, 'login.html')

def home(request):
	return render(request, 'home.html')
