import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.models import DocumentType
from mayan.apps.metadata.models import MetadataType, DocumentMetadata, DocumentTypeMetadataType

logger = logging.getLogger(__name__)

class AdvancedSearchForm(forms.Form):
    _match_all = forms.BooleanField(
        label=_('Match all'), help_text=_(
            'When checked, only results that match all fields will be '
            'returned. When unchecked results that match at least one field '
            'will be returned.'
        ), required=False
    )

    def __init__(self, *args, **kwargs):
        self.search_model = kwargs.pop('search_model')
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)

        for name, label in self.search_model.get_fields_simple_list():
            self.fields[name] = forms.CharField(
                label=label,
                required=False
            )


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=128, label=_('Search terms'), required=False
    )


class ContactForm1(forms.Form):
    inputDocType = forms.CharField(max_length=100)

class ContactForm2(forms.Form):
    inputMetadataType = forms.CharField(max_length=100)

class DocumentTypeSelectFormInSearch(forms.Form):
    
    def __init__(self, *args, **kwargs):
        help_text = kwargs.pop('help_text', None)
        if kwargs.pop('allow_multiple', False):
            extra_kwargs = {}
            field_class = forms.ModelMultipleChoiceField
            widget_class = forms.widgets.SelectMultiple
        else:
            extra_kwargs = {'empty_label': None}
            field_class = forms.ModelChoiceField
            widget_class = forms.widgets.Select

        permission = kwargs.pop('permission', None)
        user = kwargs.pop('user', None)
    
        super(DocumentTypeSelectFormInSearch, self).__init__(*args, **kwargs)

        queryset = DocumentType.objects.all().order_by('label')
        if permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=queryset, user=user
            )

        self.fields['document_type__label'] = field_class(
            help_text=help_text, label=_('Document type'),
            queryset=queryset, required=True,
            widget=widget_class(attrs={'class': 'select2', 'size': 10}),
            to_field_name='label',
            **extra_kwargs
        )
    
class MetadataTypeSelectFormInSearch(forms.Form):
      
    def __init__(self, *args, **kwargs):
        help_text = kwargs.pop('help_text', None)
        if kwargs.pop('allow_multiple', False):
            extra_kwargs = {}
            field_class = forms.ModelMultipleChoiceField
            widget_class = forms.widgets.SelectMultiple
        else:
            extra_kwargs = {'empty_label': None}
            field_class = forms.ModelChoiceField
            widget_class = forms.widgets.Select

        permission = kwargs.pop('permission', None)
        user = kwargs.pop('user', None)
        document_type = kwargs.pop('document_type')
        # document_id = kwargs.pop('step0_doc_id')

        # All the metadata tags for the selected document type
        document_metadata_types = document_type.metadata.all()

        super(MetadataTypeSelectFormInSearch, self).__init__(*args, **kwargs)
        
        # function to check if has metadata value according to document id
        def has_metadata_value(doc_id):
            if DocumentMetadata.objects.all().filter(document_id = doc_id):
                return True
            return False

        # print all field for 'document_type'-------------
        all_fields = document_type._meta.get_fields()
        logger.debug("**field for document_type**")
        for name in all_fields:
            logger.debug("**************   :"+str(name))
        # -------------------------------------------------
        
        documents_related_to_document_type = document_type.documents.all()
        valued_document_id_list = []
        for document in documents_related_to_document_type:
            if has_metadata_value(document.id):
                valued_document_id_list.append(document.id)

        valued_metadata_type_id_list = DocumentMetadata.objects.all().values_list('metadata_type_id', flat=True).filter(document_id__in=valued_document_id_list)          
        
        # k = DocumentTypeMetadataType.objects.all().values_list('metadata_type_id', flat=True).filter(document_type__pk=document_id)
        queryset = MetadataType.objects.all().filter(pk__in=valued_metadata_type_id_list)
        if permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=queryset, user=user
            )

        self.fields['metadata__metadata_type__name'] = field_class(
            help_text=help_text, label=_('Metadata type'),
            queryset=queryset, required=False,
            widget=widget_class(attrs={'class': 'select2', 'size': 10}),
            to_field_name='name',
            **extra_kwargs
        ) 
       

class MetadataValueSelectFormInSearch(forms.Form):
    
    def __init__(self, *args, **kwargs):
        help_text = kwargs.pop('help_text', None)
        if kwargs.pop('allow_multiple', False):
            extra_kwargs = {}
            field_class = forms.ModelMultipleChoiceField
            widget_class = forms.widgets.SelectMultiple
        else:
            extra_kwargs = {'empty_label': None}
            field_class = forms.ModelChoiceField
            widget_class = forms.widgets.Select
            
        permission = kwargs.pop('permission', None)
        user = kwargs.pop('user', None)
        # qs = kwargs.pop('qs', None)
        
        document_type = kwargs.pop('document_type')
        metadata_type_id = kwargs.pop('metadata_type_id')
        super(MetadataValueSelectFormInSearch, self).__init__(*args, **kwargs)
        # function to check if has metadata value according to document id
        def has_metadata_value(doc_id):
            if DocumentMetadata.objects.all().filter(document_id = doc_id):
                return True
            return False
        
        documents_related_to_document_type = document_type.documents.all()
        valued_document_id_list = []
        for document in documents_related_to_document_type:
            if has_metadata_value(document.id):
                valued_document_id_list.append(document.id)
        # queryset = qs
        queryset = DocumentMetadata.objects.all().order_by('value').distinct('value').filter(document_id__in=valued_document_id_list, metadata_type_id = metadata_type_id)
        if permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=queryset, user=user
            )

        self.fields['metadata__value'] = field_class(
            help_text=help_text, label=_('Choose value of metadata'),
            queryset=queryset, required=False,
            widget=widget_class(attrs={'class': 'select2', 'size': 10}),
            to_field_name='value',
            **extra_kwargs
        )