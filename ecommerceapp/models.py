from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    desc=models.TextField(max_length=500)
    phonenumber=models.IntegerField()
    def __str__(self):
        return str(self.id)+":"+self.name
    

class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    image = models.ImageField(upload_to='images/images')
    def __str__(self):
        return self.product_name
    

class Orders(models.Model):
    order_id=models.AutoField(primary_key=True)
    items_json=models.CharField(max_length=5000)
    amount=models.IntegerField(default=0)
    name=models.CharField(max_length=90)
    email=models.CharField(max_length=90)
    address1=models.CharField(max_length=200)
    address2=models.CharField(max_length=200)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    zip_code=models.CharField(max_length=100)
    payment_id=models.CharField(max_length=150,blank=True)
    paymentstatus=models.CharField(max_length=20,blank=True)
    phone=models.CharField(max_length=100,default="")
    razorpay_id=models.CharField(max_length=100,blank=True)
    def __str__(self):
        return str(self.order_id)+":"+str(self.name)
    


class OrderUpdate(models.Model):
    update_id=models.AutoField(primary_key=True)
    order_id=models.IntegerField(default="")
    update_desc=models.CharField(max_length=5000)
    delivered=models.BooleanField(default=False)
    stage = models.IntegerField(default=0)
    timestamp=models.DateTimeField(auto_now_add=True)
    feedbackbool=models.BooleanField(default=True)# True defines has to give 
    feedbackdesc=models.CharField(max_length=1000,default="");
    feedbackrate=models.CharField(max_length=5,default="");
    request_for_cancel=models.BooleanField(default=False)  # false defines not yet
    def __str__(self):
        return str(self.order_id)
    


class WishList(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.id) +"added"+str(self.product.id)

class Subscriber(models.Model):
    email=models.EmailField();

    def __str__(self):
        return self.email 
    


def default_profile_picture():
    return "../static/image/user.jpg"  

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/')
    phone=models.CharField(max_length=12)
    address1=models.CharField(max_length=100)
    address2=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    pincode=models.CharField(max_length=6)
    country=models.CharField(max_length=100)
    dob=models.DateField()
    gender=models.CharField(max_length=8)

    def __str__(self):
        return self.user.username


class OrderCancel(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    updateorder=models.ForeignKey(OrderUpdate,on_delete=models.CASCADE)
    reason = models.CharField(max_length=300)