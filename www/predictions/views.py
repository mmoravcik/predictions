from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from predictions.player.forms import CustomUserCreationForm

def home(request):
    return render_to_response('home.html', {}, context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return render_to_response("registration/register_ok.html", {}, context_instance=RequestContext(request))
    else:
        form = CustomUserCreationForm()

    return render_to_response("registration/register.html", {'form' : form}, context_instance=RequestContext(request))