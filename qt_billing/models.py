from django.db import models
from ordered_model.models import OrderedModel


class UniqueSellingPoint(models.Model):
    description = models.CharField(max_length=128)

    def __str__(self):
        return self.description


class ProductUtil(models.Model):
    product = models.OneToOneField("djstripe.Product", on_delete=models.CASCADE)
    unique_selling_points = models.ManyToManyField(
        UniqueSellingPoint, through="ProductUniqueSellingPointThroughModel"
    )
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.product.__str__()


class ProductUniqueSellingPointThroughModel(OrderedModel):
    product_util = models.ForeignKey(ProductUtil, on_delete=models.CASCADE)
    unique_selling_point = models.ForeignKey(
        UniqueSellingPoint, on_delete=models.CASCADE
    )
    order_with_respect_to = "product_util"

    class Meta:
        ordering = ("product_util", "order")
