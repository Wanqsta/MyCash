from django import forms

from .models import Contact, Transaction

class CreateContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'number')

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ('created', 'transaction_type')


