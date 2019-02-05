from django.shortcuts import render
from django.views import View

class MyProfileCreation(View):
    def get(self, request):
        return render(request, 'profiles/signup.html')
