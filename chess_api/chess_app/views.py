from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def chat_test(request):
    return render(request, 'chat_test.html')

def chess_test(request):
    return render(request, 'chess_test.html')