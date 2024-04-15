from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

# Create your models here.
class Shareholder(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name', )


class Collector(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Customer(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(max_length=400, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name', )


class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loan_customer')
    guarantor1 = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loan_guarantor1')
    guarantor2 = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='loan_guarantor2',
        null=True, blank=True
        )
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    duration = models.PositiveIntegerField()
    interest = models.DecimalField(decimal_places=2, max_digits=10)
    start_date = models.DateField()
    shareholder = models.ForeignKey(Shareholder, on_delete=models.CASCADE)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE)
    collected = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, editable=False)
    amount_to_deliver = models.DecimalField(decimal_places=2, max_digits=10, editable=False)
    fees = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, editable=False)
    amount_with_interest = models.DecimalField(decimal_places=2, max_digits=10, editable=False)
    STATUS = (
        ('Active', 'Active'),
        ('Closed', 'Closed'),
    )
    status = models.CharField(max_length=6, choices=STATUS, default='Active')

    
    def __str__(self):
        return f'{self.customer.name} ({self.amount})'
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            Installment.objects.filter(loan=self).delete()
        
        self.fees = (self.amount * Decimal(0.05)).quantize(Decimal('.01'), ROUND_HALF_UP)
        interest_per_ten_months = self.amount * self.interest / Decimal(100)
        num_of_ten_months = self.duration / Decimal(10)
        total_interest = (interest_per_ten_months * num_of_ten_months).quantize(Decimal('.01'), ROUND_HALF_UP)
        self.amount_with_interest = self.amount + total_interest
        installment_amount = (self.amount_with_interest / self.duration).quantize(
            Decimal('.01'), ROUND_HALF_UP)
        self.collected = installment_amount
        self.amount_to_deliver = self.amount - self.fees - installment_amount
        
        for i in range(1, self.duration + 1):
            new_date = self.start_date + relativedelta(months=(i - 1))
            installment = Installment(loan=self, date=new_date, amount=installment_amount)
            if i == 1:
                installment.collector = self.collector
                installment.paid = True
            installment.save()
        super().save(*args, **kwargs)


class Installment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='loan_installment')
    date = models.DateField()
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    paid = models.BooleanField(default=False)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE, blank=True, null=True)
    month = models.CharField(max_length=20, editable=False)
    year = models.PositiveIntegerField(editable=False)
    
    def save(self, *args, **kwargs):
        self.month = self.date.strftime('%B')
        self.year = self.date.strftime('%Y')
        
        if self.pk is not None:
            paid_installments = Installment.objects.filter(
                loan=self.loan,
                paid=True
            ).exclude(pk=self.pk)
            total_paid = paid_installments.aggregate(total=Sum('amount'))['total']
            count_paid = paid_installments.count()
            if self.paid == True:
                total_paid += self.amount
                count_paid += 1
            Loan.objects.filter(pk=self.loan.pk).update(collected=total_paid)
            loan = Loan.objects.get(pk=self.loan.pk)
            print('counting', loan.duration, count_paid)
            if loan.duration == count_paid:
                Loan.objects.filter(pk=self.loan.pk).update(status='Closed')
            print('paid_installments', paid_installments)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.loan.customer.name}'
    
    class Meta:
        ordering = ('date', )

