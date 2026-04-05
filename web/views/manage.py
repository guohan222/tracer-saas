from django.shortcuts import render


def dashboard(request,proj_id):
    return render(request,'dashboard.html')






def statistics(request,proj_id):
    return render(request,'statistics.html')







