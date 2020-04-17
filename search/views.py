from django.views.generic.base import TemplateView
from django.utils.datastructures import MultiValueDictKeyError

from .utils import perform_search


class Search(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        try:
            query = self.request.GET['query']
        except MultiValueDictKeyError:
            # this happens when someone goes directly to the /search/ url...
            # for some reason people have gotten this to error...
            query = ''
        results, counts = perform_search(query)

        context = {'query': query,
                   'counts': counts,
                   'results': results}
        kwargs.update(context)

        return super().get_context_data(**kwargs)
