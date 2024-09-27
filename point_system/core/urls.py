from django.urls import path
from . import views

urlpatterns = [
    path('register-qr/', views.register_qr, name='register-qr'),
    path('points/<str:phone_number>/', views.check_points, name='check-points'),
    path('get-refferrals/<str:phone_number>/', views.get_referrals, name='get-refferrals'),

    path('get-avaliable-items/', views.get_available_items, name='get-redeem'),
    path('get-my-items/<str:phone_number>/', views.get_redeemed_items, name='get-my-items'),
    path('redeem-item/', views.redeem_item, name='redeem-item'),

    path('code-refer/<str:phone_number>/', views.check_code, name='check-code'),
    path('add-reffer/', views.refer_system, name='refer-system'),
    path('create-profile/', views.create_profile, name='create-profile'),

    path('create-referral-code/', views.create_referral_code, name='create-referral-code'),
]