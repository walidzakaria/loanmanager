from django.contrib import admin
from .models import Shareholder, Collector, Customer, Loan, Installment


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )
    search_fields = ('name', )


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 0
    readonly_fields = ['id', 'loan', 'date', 'amount', 'paid', 'collector', 'month', 'year',]
    
    def has_change_permission(self, request, obj=None):
        return False  # Always return False to make the inline read-only

    def has_delete_permission(self, request, obj=None):
        return False  # Always return False to prevent deletion

class LoanAdmin(admin.ModelAdmin):
    inlines = [InstallmentInline]
    list_display = ('id', 'customer', 'guarantor1', 'guarantor2', 'amount', 'duration',
                    'start_date', 'shareholder', 'collector', 'collected', 'fees', 'amount_to_deliver',
                    'amount_with_interest', 'status',)
    search_fields = ('customer__name',)
    list_filter= ('start_date', 'duration', 'shareholder', 'collector', 'status', )
    readonly_fields = ('fees', 'collected', 'amount_with_interest', 'amount_to_deliver', )


class InstallmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'loan', 'date', 'amount', 'paid', 'collector', 'month', 'year', )
    list_filter = ('paid', 'collector', 'month', 'year', 'day', )
    readonly_fields = ('month', 'year', 'day', 'commission', )


admin.site.register(Shareholder)
admin.site.register(Collector)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(Installment, InstallmentAdmin)
