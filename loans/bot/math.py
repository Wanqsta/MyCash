from loans.models import Contact
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
User = get_user_model()

def calculate_total(user_id, type):
    filtered_contacts = Contact.objects.filter(user_id=user_id)
    print(filtered_contacts)
    total_amount = filtered_contacts.aggregate(total_amount=Sum(type))['total_amount'] 
    print(total_amount)
    return total_amount

def process_search_contact(user_id, message_text, main_keyborad):
    search_query = message_text.strip()
    contacts = Contact.objects.filter(user_id=user_id).filter(
        Q(name__icontains=search_query) | Q(number__icontains=search_query)
    )
    return contacts 