from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

from .utils import get_arabic_month_name
# Create your models here.
class Shareholder(models.Model):
    name = models.CharField(max_length=100, verbose_name='الاسم')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name', )
        verbose_name = 'شريك'
        verbose_name_plural = 'شركاء'


class Collector(models.Model):
    name = models.CharField(max_length=100, verbose_name='الاسم')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )
        verbose_name = 'محصل'
        verbose_name_plural = 'محصلون'


class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name='الاسم')
    address = models.TextField(max_length=400, blank=True, null=True, verbose_name='العنوان')

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name', )
        verbose_name = 'عميل'
        verbose_name_plural = 'عملاء'


class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loan_customer', verbose_name='العميل')
    guarantor1 = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loan_guarantor1', verbose_name='الضامن الأول')
    guarantor2 = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='loan_guarantor2',
        null=True, blank=True,
        verbose_name='الضامن الثاني'
        )
    amount = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='القيمة')
    duration = models.PositiveIntegerField(verbose_name='المدة',)
    interest = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='الفائدة')
    start_date = models.DateField(verbose_name='تاريخ البدء')
    shareholder = models.ForeignKey(Shareholder, on_delete=models.CASCADE, verbose_name='الشريك')
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE, verbose_name='المحصل')
    collected = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, editable=False, verbose_name='المبلغ المحصل')
    amount_to_deliver = models.DecimalField(decimal_places=2, max_digits=10, editable=False, verbose_name='المبلغ المسلم')
    fees = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, editable=False, verbose_name='الرسوم الإدارية')
    commission = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, editable=False, verbose_name='العمولة')
    amount_with_interest = models.DecimalField(decimal_places=2, max_digits=10, editable=False, verbose_name='القيمة بالفائدة')
    STATUS = (
        ('Active', 'نشط'),
        ('Closed', 'مغلق'),
    )
    status = models.CharField(max_length=6, choices=STATUS, default='Active', verbose_name='الحالة')

    class Meta:
        verbose_name = 'قرض'
        verbose_name_plural = 'قروض'
    
    def __str__(self):
        return f'{self.customer.name} ({self.amount})'
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            Installment.objects.filter(loan=self).delete()
        
        self.fees = (self.amount * Decimal(0.01)).quantize(Decimal('.01'), ROUND_HALF_UP)
        self.commission = (self.amount * Decimal(0.05)).quantize(Decimal('.01'), ROUND_HALF_UP)
        interest_per_ten_months = self.amount * self.interest / Decimal(100)
        num_of_ten_months = self.duration / Decimal(10)
        total_interest = (interest_per_ten_months * num_of_ten_months).quantize(Decimal('.01'), ROUND_HALF_UP)
        self.amount_with_interest = self.amount + total_interest
        installment_amount = (self.amount_with_interest / self.duration).quantize(
            Decimal('.01'), ROUND_HALF_UP)
        self.collected = installment_amount
        self.amount_to_deliver = self.amount - self.fees - self.commission - installment_amount
        super().save(*args, **kwargs)
        for i in range(1, self.duration + 1):
            new_date = self.start_date + relativedelta(months=(i - 1))
            installment = Installment(loan=self, date=new_date, amount=installment_amount)
            if i == 1:
                installment.collector = self.collector
                installment.paid = True
            installment.save()


class Installment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='loan_installment', verbose_name='')
    date = models.DateField(verbose_name='التاريخ')
    amount = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='المدفوع')
    commission = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, editable=False, verbose_name='العمولة')
    paid = models.BooleanField(default=False, verbose_name='تم الدفع')
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE, blank=True, null=True, verbose_name='المحصل')
    day = models.PositiveSmallIntegerField(default=1, verbose_name='اليوم', editable=False)
    month = models.CharField(max_length=20, editable=False, verbose_name='الشهر')
    year = models.PositiveIntegerField(editable=False, verbose_name='السنة')
    
    def save(self, *args, **kwargs):
        self.month = get_arabic_month_name(self.date)
        self.year = self.date.strftime('%Y')
        self.day = self.date.day
        if self.paid:
            self.commission = (self.amount * Decimal(0.006)).quantize(Decimal('.01'), ROUND_HALF_UP)
        else:
            self.commission = 0.00
        
        if self.pk is not None:
            paid_installments = Installment.objects.filter(
                loan=self.loan,
                paid=True
            ).exclude(pk=self.pk)
            if paid_installments:
                total_paid = paid_installments.aggregate(total=Sum('amount'))['total']
                count_paid = paid_installments.count()
            else:
                total_paid = 0
                count_paid = 0
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
        verbose_name = 'قسط'
        verbose_name_plural = 'أقساط'
