from django.contrib import admin
from ordered_model.admin import OrderedInlineModelAdminMixin, OrderedTabularInline

from .models import (
    ProductUniqueSellingPointThroughModel,
    ProductUtil,
    UniqueSellingPoint,
)


class UniqueSellingPointTabularInline(OrderedTabularInline):
    model = ProductUniqueSellingPointThroughModel
    fields = ("unique_selling_point", "order", "move_up_down_links")
    readonly_fields = (
        "order",
        "move_up_down_links",
    )
    ordering = ("order",)
    extra = 1


class ProductUtilAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    model = ProductUtil
    list_display = ("product",)
    exclude = ("unique_selling_points",)
    inlines = (UniqueSellingPointTabularInline,)


admin.site.register(UniqueSellingPoint)
admin.site.register(ProductUtil, ProductUtilAdmin)
