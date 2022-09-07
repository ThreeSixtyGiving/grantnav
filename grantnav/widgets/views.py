from django.shortcuts import render


def home(request):

    context = {}
    return render(request, "builder.html", context=context)


def tabular(request):

    context = {}
    return render(request, "widgets/tabular_grants.html", context=context)
