from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('product/<int:pk>/', views.product_detail, name="product_detail"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    
    # Auth URLs
    path('register/', views.register_user, name="register"),
    path('login/', views.login_user, name="login"),
    path('logout/', views.logout_user, name="logout"),
    
    # Chatbot URL
    path('chatbot/', views.chatbot_response, name="chatbot"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
]