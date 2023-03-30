from django import forms

from app_cart.models import ProductInCart

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=21,
        widget=forms.TextInput(
            attrs={'class': 'Amount-input form-input', 'min': '1', 'max': '101', 'size': '2',
                   'maxlength': '2', 'readonly': True}),
        label=''
    )
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class CartAddProductModelForm(forms.ModelForm):
    class Meta:
        model = ProductInCart
        fields = ('quantity',)
        widgets = {
            'quantity': forms.TextInput(
                attrs={'class': 'Amount-input form-input', 'min': '1', 'max': '101', 'size': '2',
                       'maxlength': '2', 'readonly': True})
        }
