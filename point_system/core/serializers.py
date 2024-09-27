from rest_framework import serializers
from .models import User, QRCode, Item, RedeemedItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'name', 'points', 'referral_code', 'referred_by']

class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ['code', 'points', 'used_by']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'description', 'points_required','available_units']

class RedeemedItemerializer(serializers.ModelSerializer):
    class Meta:
        model = RedeemedItem
        fields = ['user', 'item', 'quantity', 'redeemed_at']