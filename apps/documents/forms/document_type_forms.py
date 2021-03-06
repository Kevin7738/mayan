from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList

from ..models import DocumentType, DocumentTypeFilename
from mayan.apps.tags.models import Tag
from mayan.apps.tags.widgets import TagFormWidget
from mayan.apps.metadata.models import MetadataType, DocumentMetadata, DocumentTypeMetadataType
__all__ = ('MetadataValueSelectFormInSearch', 'MetadataTypeSelectFormInSearch', 'DocumentTypeFilteredSelectForm', 'DocumentTypeFilenameForm_create', 'DocumentTypeSelectFormInSearch', 'TagSelectFormInSearch')


class DocumentTypeFilteredSelectForm(forms.Form):
    """
    Form to select the document type of a document to be created. This form
    is meant to be reused and reconfigured by other apps. Example: Used
    as form #1 in the document creation wizard.
    """
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

        super(DocumentTypeFilteredSelectForm, self).__init__(*args, **kwargs)

        queryset = DocumentType.objects.all()
        if permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=queryset, user=user
            )

        self.fields['document_type'] = field_class(
            help_text=help_text, label=_('Document type'),
            queryset=queryset, required=True,
            widget=widget_class(attrs={'class': 'select2', 'size': 10}),
            **extra_kwargs
        )

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

class TagSelectFormInSearch(forms.Form):

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

        super(TagSelectFormInSearch, self).__init__(*args, **kwargs)

        # queryset = Tag.objects.all().order_by('documents').filter(documents__pk__in=[1, 2])
        queryset = Tag.objects.all().order_by('label')
        if permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=queryset, user=user
            )

        self.fields['tags__label'] = field_class(
            help_text=help_text, label=_('Select Tag'),
            queryset=queryset, required=True,
            widget=widget_class(attrs={'class': 'select2', 'size': 10}),
            to_field_name='label',
            **extra_kwargs
        )
    
    def media(self):
        return forms.Media(js=('tags/js/tags_form.js',))
        # class Media:
        #     js = ('tags/js/tags_form.js',)


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

        super(MetadataValueSelectFormInSearch, self).__init__(*args, **kwargs)

        # if query attributes have docuemnt_type__label:
            # Find the document type using the label of the document type.
            # if the document type matching the document_type__label is found:
                # save the id of the matching document type.
                # finder the doucment metadata objects query using the document type id as the filter.

                # Set the value of the document type select form item to the document type.

        queryset = DocumentMetadata.objects.all().order_by('value').distinct('value')
        # queryset = DocumentMetadata.objects.all().order_by('value').distinct('value').filter(document__pk=2)
        if permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=queryset, user=user
            )

        self.fields['metadata__value'] = field_class(
            help_text=help_text, label=_('Choose value of metadata'),
            queryset=queryset, required=True,
            widget=widget_class(attrs={'class': 'select2', 'size': 10}),
            to_field_name='value',
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

        super(MetadataTypeSelectFormInSearch, self).__init__(*args, **kwargs)
        
        queryset = DocumentTypeMetadataType.objects.all().order_by('metadata_type_id').distinct('metadata_type_id')
        # k = DocumentTypeMetadataType.objects.all().values_list('metadata_type_id', flat=True).filter(document_type__pk=2)
        # if k:
        #     queryset = MetadataType.objects.all().filter(pk__in=k)
        # else:
        #     queryset = MetadataType.objects.none()
        if permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=queryset, user=user
            )

        self.fields['metadata__metadata_type__name'] = field_class(
            help_text=help_text, label=_('Metadata type'),
            queryset=queryset, required=True,
            widget=widget_class(attrs={'class': 'select2', 'size': 10}),
            # to_field_name='name',
            **extra_kwargs
        )
class DocumentTypeFilenameForm_create(forms.ModelForm):
    """
    Model class form to create a new document type filename
    """
    class Meta:
        fields = ('filename',)
        model = DocumentTypeFilename
