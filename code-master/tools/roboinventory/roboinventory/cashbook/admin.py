from django.contrib import admin

from roboinventory.cashbook.models import Cashbook, Transaction

class CashbookAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('cashbook', 'when', 'who', 'comment', 'amount')
    list_filter = ('cashbook', )
    ordering = ('-when', )

admin.site.register(Cashbook, CashbookAdmin)
admin.site.register(Transaction, TransactionAdmin)
