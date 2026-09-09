import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, FormView

from .forms import ContactForm
from .models import Page

logger = logging.getLogger(__name__)


class PageDetailView(DetailView):
    model = Page
    template_name = "content/page_detail.html"
    context_object_name = "page"

    def get_queryset(self):
        return Page.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = self.object.title
        ctx["meta_description"] = self.object.meta_description
        return ctx


class ContactsView(FormView):
    template_name = "content/contacts.html"
    form_class = ContactForm

    def get_success_url(self):
        return reverse("content:contacts") + "?sent=1"

    def form_valid(self, form):
        message = form.save()
        logger.info("Нове звернення #%s з контактної форми", message.pk)
        messages.success(self.request, "Дякуємо! Ми зв'яжемось з вами найближчим часом.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Контакти"
        return ctx
