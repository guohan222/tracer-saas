from django.shortcuts import render


def project_list(request):
    print(request.tracer.user)
    print(request.tracer.product)
    return render(request,'project_list.html')