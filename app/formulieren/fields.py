from django import forms
from django.forms.boundfield import BoundField as OriginalBoundField


class BoundField(OriginalBoundField):
    def __str__(self):
        """Render this field as an HTML widget."""
        if self.field.show_hidden_initial:
            return self.as_field_group() + self.as_hidden(only_initial=True)
        return self.as_field_group()


class BoundFieldOverride(forms.Field):
    def get_bound_field(self, form, field_name):
        """
        Return a BoundField instance that will be used when accessing the form
        field in a template.
        """
        return BoundField(form, self, field_name)


class CharField(forms.CharField, BoundFieldOverride):
    ...
    # def get_bound_field(self, form, field_name):
    #     """
    #     Return a BoundField instance that will be used when accessing the form
    #     field in a template.
    #     """
    #     return BoundField(form, self, field_name)
    # template_name="formulieren/fields/field.html"


class MultipleChoiceField(forms.MultipleChoiceField, BoundFieldOverride):
    ...
