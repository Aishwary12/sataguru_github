from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(AgentAssignment)
admin.site.register(CustomUser)
admin.site.register(Branch)
admin.site.register(Customer)
admin.site.register(TransactionRequest)