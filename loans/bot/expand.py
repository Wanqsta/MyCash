from loans.models import Contact
from loans.models import Transaction

def get_paginated_contacts(user_id, offset, limit):
    # Предположим, что у вас есть модель "Contact" и список всех контактов "contacts"
    contacts = Contact.objects.filter(user_id=user_id)
    total_count = len(contacts)
    is_last = False
    is_first = False

    start_index = offset

    if offset == 0:
        is_first = True

    end_index = offset + limit
    if end_index >= total_count:
        is_last = True

    paginated_contacts = contacts[start_index:end_index]
    

    return paginated_contacts, is_last, is_first

def get_paginated_debit(user_id, offset, limit):
    contacts = Contact.objects.filter(user_id=user_id).exclude(debit=0).order_by('debit')
    total_count = len(contacts)
    is_last = False
    is_first = False

    start_index = offset

    if offset == 0:
        is_first = True

    end_index = offset + limit
    if end_index >= total_count:
        is_last = True

    paginated_contacts = contacts[start_index:end_index]
    
    return paginated_contacts, is_last, is_first

def get_paginated_credit(user_id, offset, limit):
    contacts = Contact.objects.filter(user_id=user_id).exclude(credit=0).order_by('credit')
    print(contacts.count(),'red')
    total_count = len(contacts)
    is_last = False
    is_first = False

    start_index = offset

    if offset == 0:
        is_first = True

    end_index = offset + limit
    if end_index >= total_count:
        is_last = True

    paginated_contacts = contacts[start_index:end_index]
    
    return paginated_contacts, is_last, is_first

def get_paginated_transaction(user_id, offset, limit):
    transactions = Transaction.objects.filter(contact__user_id=user_id).order_by('-created')
    print(transactions)
    total_count = len(transactions)
    is_last = False
    is_first = False

    start_index = offset

    if offset == 0:
        is_first = True

    end_index = offset + limit
    if end_index >= total_count:
        is_last = True
    print(start_index)
    print(end_index)
    paginated_transactions = transactions[start_index:end_index]
    
    return paginated_transactions, is_last, is_first

def get_paginated_history(contact_id, offset, limit):
    transactions = Transaction.objects.filter(contact_id=contact_id).order_by('-created')
    print(transactions)
    total_count = len(transactions)
    is_last = False
    is_first = False

    start_index = offset

    if offset == 0:
        is_first = True

    end_index = offset + limit
    if end_index >= total_count:
        is_last = True
    print(start_index)
    print(end_index)
    paginated_transactions = transactions[start_index:end_index]
    
    return paginated_transactions, is_last, is_first