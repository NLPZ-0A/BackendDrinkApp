from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, QRCode, Item ,RedeemedItem

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'points_required')  # Asegúrate de incluir 'id'

admin.site.register(User)
admin.site.register(QRCode)
#admin.site.register(Item)
admin.site.register(RedeemedItem)