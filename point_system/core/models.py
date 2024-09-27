from django.db import models

class User(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    points = models.PositiveIntegerField(default=0)
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referidos')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number

class QRCode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    points = models.PositiveIntegerField()
    gift = models.CharField(max_length=100, null=True, blank=True)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    points_required = models.PositiveIntegerField()  # Puntos necesarios para canjear el objeto
    available_units = models.PositiveIntegerField(default=0)  # Unidades disponibles

    def __str__(self):
        return self.name

class RedeemedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redeemed_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='redeemed_items')
    quantity = models.PositiveIntegerField()  # Cantidad canjeada
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.name} - {self.item.name} (x{self.quantity})'
