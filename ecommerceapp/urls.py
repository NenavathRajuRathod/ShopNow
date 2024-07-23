from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('contact/',views.contact),
    path('about/',views.about,name="about"),
    path('checkout/',views.checkout,name="checkout"),
    path('handlerequest/', views.handlerequest, name='handlerequest'),
    path('viewproduct/<id>/',views.viewproduct,name='viewproduct'),
    path('add_to_wishlist/<product_id>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('remove_from_wishlist/<product_id>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('search/',views.search,name='search'),
    path('profile/',views.profile,name='profile'),
    path('editprofile/',views.editprofile,name='editprofile'),
    path('trackorder/<int:id>/',views.trackorder,name='trackorder'),
    path('feedback/<int:id>/',views.feedback,name='feedback'),
    path('wishlist_remove/<int:id>/',views.wishlist_remove,name='wishlist_remove'),
    path('cancelorder/<id>/',views.cancelorder,name='cancelorder'),

]
