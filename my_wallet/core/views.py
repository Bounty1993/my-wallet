import logging

from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get(self, *args):
        logger.debug('Hello from here')
        return super().get(*args)
