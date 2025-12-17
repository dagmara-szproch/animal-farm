from django.shortcuts import render

def volunteer_info(request):
    return render(request, 'volunteer/volunteer_info.html')