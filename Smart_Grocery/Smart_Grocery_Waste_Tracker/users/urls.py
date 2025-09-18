from django.urls import path
from . import views

urlpatterns = [
    # User authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Grocery item management
    path('add_item/', views.add_item, name='add_item'),
    path('view_item/', views.view_item, name='view_item'),

    path('edit-item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),
    path('inventory/', views.inventory, name='inventory'),

    # Waste management
    path('mark_wasted/<int:item_id>/', views.mark_wasted, name='mark_wasted'),
    path('waste_logged/', views.waste_logged, name='waste_logged'),

    # Reports
    path('report/', views.report, name='report'),
    path('savings/', views.savings, name='savings'),

    # Expiry alerts
    path('expiring_soon/', views.expiring_soon, name='expiring_soon'),
    path('profileuser/', views.profileuser, name='profileuser'),

path("sell_item/<int:item_id>/", views.sell_item, name="sell_item"),

]