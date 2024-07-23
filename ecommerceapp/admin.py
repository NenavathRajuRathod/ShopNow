from django.contrib import admin

from ecommerceapp.models import Product,Contact,Orders,OrderUpdate,WishList,Subscriber,UserProfile
# Register your models here.
admin.site.register(Contact);
admin.site.register(Product)
admin.site.register(OrderUpdate)
admin.site.register(Orders)
admin.site.register(WishList)
admin.site.register(Subscriber)
admin.site.register(UserProfile)