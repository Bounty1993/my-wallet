from django.shortcuts import render, redirect
from django.views.generic import \
    TemplateView, CreateView
from .forms import AssetCreationFormset
import datetime
from .models import Portfolio
from django.contrib.auth.decorators import login_required

class HomeView(TemplateView):
    template_name = 'core/home.html'

@login_required
def create_asset(request):

    if request.method == 'POST':
        formset = AssetCreationFormset(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.bought_for = instance.get_current_price()
                instance.created_at = datetime.date.today()
                asset = instance.save()
                profile = request.user
                Portfolio.objects.create(profile=profile,
                                         assets=asset)
            return redirect('/thanks/')

    else:
        formset = AssetCreationFormset()

    return render(request, 'core/new.html', {'formset': formset})
