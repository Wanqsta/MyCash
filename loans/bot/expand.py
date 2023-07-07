from loans.models import Contact

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
