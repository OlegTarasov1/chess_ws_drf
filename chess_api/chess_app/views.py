from django.shortcuts import render

def index(request):
    return render(request, 'index.html')


def chat_test(request):
    return render(request, 'chat_test.html')