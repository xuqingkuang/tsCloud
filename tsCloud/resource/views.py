from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.decorators.csrf import csrf_exempt

import forms, models

# Create your views here.


class HomeView(TemplateView):
    """
    Home View
    """
    template_name = 'resource/home.html'

class ResourceDetailView(DetailView):
    model = models.Resource
    template_name = 'resource/resource_detail.html'

class ResourceListView(ListView):
    model = models.Resource
    template_name = 'resource/resource_list.html'
    context_object_name = 'resources'
    paginate_by = 10

def download(request, slug):
    try:
        res = models.Resource.objects.get(slug = slug)
    except models.Resource.DoesNotExist, err:
        raise Http404(err)
    return redirect(res.download(source = request.REQUEST.get('source')))

class SubmitView(CreateView):
    template_name='resource/submit.html'
    model_class = models.Resource

    def get_initial(self):
        return {
            'category': self.kwargs['category_slug'],
        }

    def get_form_class(self):
        # Get the root category for base form
        try:
            category = models.Category.objects.get(
                slug = self.kwargs['category_slug']
            )
        except models.Category.DoesNotExist, err:
            raise Http404(err)
        return getattr(forms, category.form_class_name)

class RecommendationListView(ListView):
    template_name = 'resource/recommendation_list.html'
    context_object_name = 'recommendations'
    allow_empty = False
    
    def get_queryset(self):
        return models.Recommendation.objects.filter(
            category__slug = self.kwargs['category_slug'],
            is_active = True
        )

class RecommendationEditView(TemplateView):
    model_class = models.Recommendation
    form_class = forms.RecommendationForm
    template_name = 'resource/recommendation_edit.html'

    def get_context_data(self, **kwargs):
        context = super(RecommendationEditView, self).get_context_data(**kwargs)
        context['form'] = self.form_class(initial={
            'category': self.kwargs['category_slug']
        })
        context['recommendations'] = self.model_class.objects.filter(
            category__slug = self.kwargs['category_slug']
        ).select_related('category', 'Resource')
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            category.recommendation_set.all().delete()
            resource_pks = request.POST.getlist('resourcePk')
            index = 10
            for resource_pk in resource_pks:
                try:
                    resource = models.Resource.objects.get(pk = resource_pk)
                except models.Resource.DoesNotExist:
                    continue
                category.recommendation_set.create(
                    resource = resource,
                    desc = request.POST.get('desc_' + resource_pk, None),
                    order = index,
                    is_active = request.POST.get('isActive_' + resource_pk, False),
                )
                index += 10
        return super(RecommendationEditView, self).get(request, *args, **kwargs)
