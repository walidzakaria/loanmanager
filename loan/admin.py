from django.contrib import admin
from .models import Shareholder, Collector, Customer, Loan, Installment


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )
    search_fields = ('name', )


class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'guarantor1', 'guarantor2', 'amount', 'duration',
                    'start_date', 'shareholder', 'collector', 'collected', 'fees', )
    search_fields = ('customer__name',)
    list_filter= ('start_date', 'duration', 'shareholder', 'collector', )
    readonly_fields = ('collected', )


admin.site.register(Shareholder)
admin.site.register(Collector)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(Installment)