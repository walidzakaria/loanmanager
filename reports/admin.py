from django.contrib import admin
from .models import Commission, MonthCommission

# Register your models here.
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'description', 'customer', 'start_date', 'amount', )
    list_filter = ('user', 'description', 'year', 'month', )
    
    def has_add_permission(self, request):
        # Disable the ability to add new instances
        return False

    def has_change_permission(self, request, obj=None):
        # Disable the ability to change existing instances
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete instances
        return False
    
    def save_model(self, request, obj, form, change):
        # Prevent saving changes to the model
        pass
    

class MonthCommissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'year', 'month', )
    list_filter = ('user', 'year', 'month', )
    
    def has_add_permission(self, request):
        # Disable the ability to add new instances
        return False

    def has_change_permission(self, request, obj=None):
        # Disable the ability to change existing instances
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete instances
        return False
    
    def save_model(self, request, obj, form, change):
        # Prevent saving changes to the model
        pass


admin.site.register(Commission, CommissionAdmin)
admin.site.register(MonthCommission, MonthCommissionAdmin)
