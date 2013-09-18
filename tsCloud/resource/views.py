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

def submit(request, category_slug, template_name='resource/submit.html'):
    # Get the root category for base form
    try:
        category = models.Category.objects.get(slug = category_slug)
    except models.Category.DoesNotExist, err:
        raise Http404(err)

    form_class = getattr(forms, category.form_class_name, None)
    if not form_class:
        raise Http404('Specific category is not exist')

    form_initial_data = {
        'category': category.slug
    }
    form = form_class(initial=form_initial_data)

    # Do the POST works
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if not request.REQUEST.get('continue'):
                return redirect(form.instance.get_absolute_url())

    # Render the form
    return render(request, template_name, {
        'form': form,
    })
    