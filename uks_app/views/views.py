from django.shortcuts import render

# home page
def index(request): 
    return render(request, 'uks_app/index.html') #optional third argument context


 
