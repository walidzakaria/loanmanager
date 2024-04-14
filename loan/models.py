from django.db import models
from decimal import Decimal, ROUND_HALF_UP

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
    start_date = models.DateField()
    shareholder = models.ForeignKey(Shareholder, on_delete=models.CASCADE)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE)
    collected = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)

    @property
    def fees(self):
        return (self.amount * Decimal(0.05)).quantize(Decimal('.01'), ROUND_HALF_UP)
    
    def __str__(self):
        return f'{self.customer.name} ({self.amount})'


class Installment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='loan_installment')
    date = models.DateField()
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    paid = models.BooleanField(default=False)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.loan.customer.name}'
