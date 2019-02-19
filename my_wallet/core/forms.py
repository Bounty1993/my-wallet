from django import forms
from django.forms import modelformset_factory
from .models import Asset


class AssetCreationForm(forms.ModelForm):


    class Meta:
        model = Asset
        fields = ('stock', 'num_of_shares')
        widgets = {
            'stocks': forms.Select(
                attrs={'class': 'special'}
            ),
            'num_of_shares': forms.NumberInput(
                attrs={'class': 'special'}
            )
        }


AssetCreationFormset = modelformset_factory(
    Asset, form=AssetCreationForm)
