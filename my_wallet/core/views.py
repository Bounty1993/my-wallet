from django.shortcuts import render
from django.views.generic import TemplateView
import logging

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get(self, *args):
        logger.debug('Hello from here')
        return super().get(*args)



