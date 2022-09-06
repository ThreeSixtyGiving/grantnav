from django.shortcuts import render

def home(request):

    context = {}

    return render(request, "builder.html", context=context)
