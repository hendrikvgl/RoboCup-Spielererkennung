from datetime import datetime

from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.contrib.auth.models import User
from django.utils.dateformat import format as date_format

class Cashbook(models.Model):
    name = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0,
            editable=False)

    def __unicode__(self):
        return self.name

class Transaction(models.Model):
    cashbook = models.ForeignKey(Cashbook)
    when = models.DateTimeField(default=datetime.today)
    who = models.ForeignKey(User)
    comment = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __unicode__(self):
        formatted_date = date_format('Y-m-d H:i', self.when)
        return u'[{0}] Transaction of {1} EUR by {2} in {3}'.format(
                formatted_date, self.amount, self.who, self.cashbook.name)

def apply_transaction_cb(sender, instance, **kwargs):
    cashbook = None
    if instance.pk:
        # Redraw old transaction changes
        old_transaction = Transaction.objects.get(pk=instance.pk)
        cashbook = old_transaction.cashbook
        cashbook.balance -= old_transaction.amount
        cashbook.save()
    
    if not cashbook or cashbook != instance.cashbook:
        cashbook = instance.cashbook
    cashbook.balance += instance.amount
    cashbook.save()

def remove_transaction_cb(sender, instance, **kwargs):
    cashbook = instance.cashbook
    cashbook.balance -= instance.amount
    cashbook.save()

pre_save.connect(apply_transaction_cb, sender=Transaction)
pre_delete.connect(remove_transaction_cb, sender=Transaction)
