from django.views.generic.base import TemplateView

from .utils import perform_search


class Search(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        query = self.request.GET['query']
        results, counts = perform_search(query)

        context = {'query': query,
                   'counts': counts,
                   'results': results}
        kwargs.update(context)

        return super().get_context_data(**kwargs)
