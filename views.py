from django.shortcuts import render
from .GCP_functions import reidentify
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html')

@csrf_exempt
def unencrypt_view(request):
    if request.method == 'POST':
        return reidentify(request)
    else:
        return HttpResponse("This URL only supports POST requests.", status=405)