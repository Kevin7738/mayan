import logging

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView

from mayan.apps.common.generics import SimpleView, SingleObjectListView
from mayan.apps.common.literals import LIST_MODE_CHOICE_ITEM

from .forms import SearchForm, AdvancedSearchForm
from .icons import icon_search_submit
from  mayan.apps.sources.icons import icon_wizard_submit
from .mixins import SearchModelMixin
from .runtime import search_backend

from django.shortcuts import render
from formtools.wizard.views import SessionWizardView
from mayan.apps.dynamic_search.forms import DocumentTypeSelectFormInSearch, MetadataTypeSelectFormInSearch, MetadataValueSelectFormInSearch
from django.http import HttpResponseRedirect
from mayan.apps.metadata.models import MetadataType, DocumentMetadata, DocumentTypeMetadataType

from mayan.apps.documents.permissions import permission_document_type_view, permission_document_view
logger = logging.getLogger(name=__name__)


class ResultsView(SearchModelMixin, SingleObjectListView):
    def get_extra_context(self):
        context = {
            'hide_object': True,
            'no_results_icon': icon_search_submit,
            'no_results_text': _(
                'Try again using different terms. '
            ),
            'no_results_title': _('No search results'),
            'search_model': self.search_model,
            'title': _('Search results for: %s') % self.search_model.label,
            # 'title': _('Search results for: %s') % self.request.GET.get('_match_all'),

        }

        if self.search_model.list_mode == LIST_MODE_CHOICE_ITEM:
            context['list_as_items'] = True

        return context

    def get_source_queryset(self):
        self.search_model = self.get_search_model()

        if self.request.GET:
            # Only do search if there is user input, otherwise just render
            # the template with the extra_context

            if self.request.GET.get('_match_all', 'off') == 'on':
                global_and_search = True
            else:
                global_and_search = False

            queryset = search_backend.search(
                global_and_search=global_and_search,
                search_model=self.search_model,
                query_string=self.request.GET, user=self.request.user
            )

            return queryset


class SearchView(SearchModelMixin, SimpleView):
    template_name = 'appearance/generic_form.html'
    title = _('Search')

    def get_extra_context(self):
        self.search_model = self.get_search_model()
        return {
            'form': self.get_form(),
            'form_action': reverse(
                viewname='search:results', kwargs={
                    'search_model_name': self.search_model.get_full_name()
                }
            ),
            'search_model': self.search_model,
            'submit_icon_class': icon_search_submit,
            'submit_label': _('Search'),
            'submit_method': 'GET',
            'title': _('Search for: %s') % self.search_model.label,
        }

    def get_form(self):
        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']
            return SearchForm(initial={'q': query_string})
        else:
            return SearchForm()


class AdvancedSearchView(SearchView):
    title = _('Advanced search')

    def get_form(self):
        return AdvancedSearchForm(
            data=self.request.GET, search_model=self.get_search_model()
        )


class SearchAgainView(RedirectView):
    pattern_name = 'search:search_advanced'
    query_string = True

class DocumentSearchWizard(SessionWizardView):
    template_name = 'dynamic_search/wizard_form.html'

    form_list = [
        DocumentTypeSelectFormInSearch, 
        MetadataTypeSelectFormInSearch,
        MetadataValueSelectFormInSearch,
    ]
    
    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == '0':
            kwargs.update({
                'permission': permission_document_view,
                'user': self.request.user
            })

        if step == '1':          
            document_type = self.get_cleaned_data_for_step('0')['document_type__label']
            kwargs.update({'document_type' : document_type})

            # step0_doc_id = self.get_cleaned_data_for_step('0')['document_type__label'].pk

        if step == '2':
            hasMetadataType = self.get_cleaned_data_for_step('1')['metadata__metadata_type__name']
            if hasMetadataType:
                metadata_type_id = hasMetadataType.pk
            else:
                metadata_type_id = None
            document_type = self.get_cleaned_data_for_step('0')['document_type__label']
            kwargs.update({
                'document_type' : document_type,
                'metadata_type_id' : metadata_type_id,
            })
        return kwargs

        
    def done(self, form_list, **kwargs):
        documentType = self.get_cleaned_data_for_step('0')['document_type__label'].label
        metadataSelectResult = self.get_cleaned_data_for_step('1')['metadata__metadata_type__name']
        
        if metadataSelectResult is None:
            metadataType = ''

        else:
            metadataType = metadataSelectResult.name
        
        metadataValue = ''
        if metadataType is None:
            metadataValue = ''
        else:
            metadataValueSelectResult = self.get_cleaned_data_for_step('2')['metadata__value']
            if metadataValueSelectResult is None:
                metadataValue = ''
            else:
                metadataValue = metadataValueSelectResult.value
        


        return HttpResponseRedirect(reverse('search:results')+
        '?_search_model_name=documents.Document&'+
        '_match_all=on'+
        '&document_type__label='+documentType+
        '&metadata__metadata_type__name='+metadataType+
        '&metadata__value='+metadataValue+
        '&q='
        )