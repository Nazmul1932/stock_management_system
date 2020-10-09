from django.contrib import admin
from .models import Stock, Category, StockHistory
from .forms import StockCreateForm


class StockCreationAdmin(admin.ModelAdmin):
    list_display = ['category', 'item_name', 'quantity']
    form = StockCreateForm
    list_filter = ['category']
    search_fields = ['category__name', 'item_name']


admin.site.register(Stock, StockCreationAdmin)
admin.site.register(Category)
admin.site.register(StockHistory)


