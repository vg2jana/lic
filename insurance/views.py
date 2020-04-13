import json
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Client, Policy, Due
from django_tables2 import RequestConfig


class ClientDetailView(generic.DetailView):
    model = Client
    template_name = 'client_detail.html'

    # Use this to pass any extra information
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        #context['policies'] = Client.policy_set.all()
        return context


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

def all_clients(request):
    template = loader.get_template('lic/clients.html')
    context = {
        'client_list': Client.objects.all(),
        'column_names': ("Name", "Customer ID", "Email ID", "Mobile number", "Enrolled Policies")
    }
    return HttpResponse(template.render(context, request))

def dues(request):
    template = loader.get_template('lic/dues.html')
    context = {
        'due_list': Due.objects.all(),
        'column_names': ("Name", "Email ID", "Mobile number", "Policy number", "Due date", "Grace date", "Premium paid", "Next reminder")
    }
    return HttpResponse(template.render(context, request))

def client_detail(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    return render(request, 'lic/client_detail.html', {'client': client})

def policy_detail():
    return None

def due_json(request, pk):
    due = Due.objects.get(id=pk)
    client = due.policy.client
    due_json = {
        'name': client.full_name(),
        'email': client.email,
        'mobile': client.mobile_number,
        'policy': due.policy.number,
        'paid': due.paid(),
    }
    if request.is_ajax():
        return JsonResponse(due_json)
    else:
        return HttpResponse(json.dumps(due_json))

def due_submit(request, pk):
    if request.method == 'POST':
        data = request.POST
        premium_paid = data.get('premiumPaid')
        due = Due.objects.get(id=pk)
        if premium_paid is not due.premium_paid:
            due.premium_paid = premium_paid
            due.save()
        if due.premium_paid is False:
            for reminder in due.reminder_set.all():
                reminder.reminder_sent = False
                reminder.save()
        return dues(request)
