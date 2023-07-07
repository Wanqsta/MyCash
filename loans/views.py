from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import CreateContactForm, TransactionForm
from .models import Contact, TRANSACTION_CHOICE

def create_contact(request):
    if request.method == 'POST':
        form = CreateContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            return redirect ('users:home') 
    else:
        form = CreateContactForm     
    return render(request, 'loans/create_contact.html', {'form': form})

@login_required
def contacts_list (request):
    contacts = Contact.objects.filter(user=request.user)
    return render(request, 'loans/contacts_list.html', {'contacts': contacts})

@login_required
def contact_detail(request, id):
    contact = Contact.objects.get(id=id)
    return render(request, 'loans/contact.html',{"contact": contact})

@login_required
def create_transaction(request, type):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = type
            contact = transaction.contact
            if transaction.transaction_type == 'borrow':
                contact.credit = contact.credit+transaction.amount
                contact.save()
                transaction.save()
                return redirect('loans:contact_detail', id=contact.id)
            if transaction.transaction_type == 'repay':
                contact.credit = contact.credit-transaction.amount
                contact.save()
                transaction.save()
                return redirect('loans:contact_detail', id=contact.id)
            if transaction.transaction_type == 'lend':
                contact.debit = contact.debit+transaction.amount
                contact.save()
                transaction.save()
                return redirect('loans:contact_detail', id=contact.id)
            if transaction.transaction_type == 'receive':
                contact.debit = contact.debit-transaction.amount
                contact.save()
                transaction.save()
                return redirect('loans:contact_detail', id=contact.id)
    form = TransactionForm()
    return render(request, 'loans/transaction.html', {"form": form})

def test(request):
    return render(request, 'loans/test.html')
