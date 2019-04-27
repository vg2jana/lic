from insurance import models
from django import forms

class PolicyTypeForm(forms.ModelForm):
    action_items = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=models.PolicyType.policy_type_choices)

    class Meta:
        model = models.PolicyType
        fields = '__all__'
        list_fields = '__all__'
