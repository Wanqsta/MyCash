from django.urls import path
from .views import create_contact, contacts_list, contact_detail, create_transaction, test
from .management.commands.bot import webhook

app_name = 'loans'

urlpatterns = [
    path('create/contact', create_contact, name='create_contact'),
    path('contact/list', contacts_list, name='contacts_list'),
    path('contact/<int:id>/', contact_detail, name='contact_detail'),
    path('transaction/<str:type>/', create_transaction, name='create_transaction'),
    path('view/test', test, name='test'),
    path('bot/', webhook, name='webhook'),

]
