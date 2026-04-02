from django.shortcuts import render


def dashboard(request,proj_id):
    return render(request,'dashboard.html')


def issues(request,proj_id):
    return render(request,'issues.html')



def statistics(request,proj_id):
    return render(request,'statistics.html')








def settings(request,proj_id):
    return render(request,'settings.html')