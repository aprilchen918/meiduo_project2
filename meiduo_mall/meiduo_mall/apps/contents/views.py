from django.shortcuts import render
from django.views import View

# Create your views here.


class IndexView(View):
    """Home page advertisement"""
    def get(self, request):
        """Provide home page adversment ingerface"""
        return render(request, 'index.html')