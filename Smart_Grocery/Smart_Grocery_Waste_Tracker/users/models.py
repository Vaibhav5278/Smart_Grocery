from django.db import models
from django.contrib.auth.models import User


class GroceryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    purchase = models.DateField()   # 🔹 only date
    expiry = models.DateField()     # 🔹 only date
    supplier = models.CharField(max_length=100, blank=True, null=True)
    price = models.PositiveIntegerField(default=0)
    mrp = models.PositiveIntegerField(default=0)
    quantity_wasted = models.FloatField(default=0)
    waste_date = models.DateField(blank=True, null=True)   # 🔹 changed
    waste_reason = models.CharField(max_length=100, blank=True, null=True)
    sold_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    # --- Utility functions ---
    @property
    def remaining_quantity(self):
        return self.quantity - (self.sold_quantity + self.quantity_wasted)

    @property
    def sold_value(self):
        return self.sold_quantity * self.mrp

    @property
    def wasted_value(self):
        return self.quantity_wasted * self.price

    @property
    def savings(self):
        return (self.quantity - self.quantity_wasted) * self.mrp


class WastedItem(models.Model):
    item_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    quantity_wasted = models.FloatField()
    waste_date = models.DateField()   # 🔹 changed
    reason = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.item_name} - {self.quantity_wasted}"


class WastedGroceryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    reason = models.CharField(
        max_length=255,
        choices=[
            ('expired', 'Expired'),
            ('damaged', 'Damaged'),
            ('manual', 'Manually Discarded')
        ]
    )
    waste_date = models.DateField(blank=True, null=True)   # 🔹 changed


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100)

    def __str__(self):
        return self.store_name
