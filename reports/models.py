from django.db import models

# Create your models here.
class Commission(models.Model):
    user = models.CharField(max_length=100, verbose_name='الموظف')
    description = models.CharField(max_length=100, verbose_name='البيان')
    customer = models.CharField(max_length=100, verbose_name='العميل')
    start_date = models.DateField(verbose_name='التاريخ')
    amount = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='القيمة')
    year = models.CharField(max_length=4, verbose_name='السنة')
    month = models.CharField(max_length=2, verbose_name='الشهر')
    
    class Meta:
        managed = False
        db_table = 'Commission'
        verbose_name_plural = 'العمولات'
        verbose_name = 'العمولة'


class MonthCommission(models.Model):
    user = models.CharField(max_length=100, verbose_name='الموظف')
    amount = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='القيمة')
    year = models.CharField(max_length=4, verbose_name='السنة')
    month = models.CharField(max_length=2, verbose_name='الشهر')
    
    class Meta:
        managed = False
        db_table = 'MonthCommission'
        verbose_name_plural = 'إجمالي العمولات'
        verbose_name = 'إجمالي العمولات'
