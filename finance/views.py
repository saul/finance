from django.shortcuts import render

def reload_top(request):
    return render(request, 'reload_top.html')
