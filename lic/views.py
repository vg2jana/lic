from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Client, Policy

class Clients(generic.ListView):
    template_name = 'lic/clients.html'
    # DOCS: Context object is client_list
    context_object_name = 'client_list'

    def get_queryset(self):
        return Client.objects.order_by('-first_name')


class ClientDetailView(generic.DetailView):
    model = Client
    # DOCS: template name is client_detail
    template_name = 'lic/client_detail.html'

    # Use this to pass any extra information
    #def get_context_data(self, **kwargs):
    #    # Call the base implementation first to get a context
    #    context = super().get_context_data(**kwargs)
    #    # Add in a QuerySet of all the books
    #    context['full_name'] = " Hi"
    #    return context


class PolicyDetailView(generic.DetailView):
    model = Policy
    # DOCS: template name is policy_detail
    template_name = 'lic/policy_detail.html'


def index(request):
    template = loader.get_template('lic/base.html')
    context = {
        #'client_list': Client.objects.all(),
    }
    return HttpResponse(template.render(context, request))

def client_detail(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    return render(request, 'lic/client_detail.html', {'client': client})

def policy_detail():
    return None