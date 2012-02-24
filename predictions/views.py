from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm

def home(request):
    return render_to_response('home.html', {}, context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")




def register(request):
    form = UserCreationForm()

    if request.method == 'POST':
        data = request.POST.copy()
        errors = form.get_validation_errors(data)
        if not errors:
            new_user = form.save()
            return HttpResponseRedirect("/accounts/created/")
    else:
        data, errors = {}, {}

    return render_to_response("registration/register.html", {
        'form' : form
    })