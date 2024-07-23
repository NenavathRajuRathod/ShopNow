from django.shortcuts import render,redirect
from ecommerceapp.models import Contact,Product,OrderUpdate,Orders,WishList,Subscriber,UserProfile,OrderCancel
from django.contrib import messages
from math import ceil
from django.conf import settings
from django.views.decorators.csrf import  csrf_exempt
import razorpay
from django.http import JsonResponse 
import json
from django.template.loader import render_to_string
from .utils import TokenGenerator,generate_token
from django.core.mail import EmailMessage
# Create your views here.

def index(request):

    allProds = []
    catprods = Product.objects.values('category','id')
    print(catprods)
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}

    return render(request,"index.html",params)




def searchMatch(query,item):
    if query.lower() in item.product_name.lower() or query.lower() in item.category.lower() or query.lower() in item.subcategory.lower() or query.lower() in item.desc.lower():
        return True
    else:
        return False
    

def search(request):
    query=request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp= Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query,item)]
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod)!=0:
            allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds,'msg':""}
    if len(allProds)==0 or len(query)<4:
        params={'msg':'please make sure to enter the relavent search'}
    return render(request,"index.html",params)

    
def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        messages.info(request,"we will get back to you soon..")
        return render(request,"contact.html")


    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    if request.method == "POST":
        items_json = request.POST.get('itemsJson')
        name = request.POST.get('name')
        amount = max(int(float(request.POST.get('amt')) ), 1)
        email = request.POST.get('email')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        
        Order = Orders(items_json=items_json, name=name, amount=amount, email=email, address1=address1, address2=address2, city=city, state=state, zip_code=zip_code, phone=phone)
        Order.save()
        
        update = OrderUpdate(order_id=Order.order_id, update_desc="the order has been placed")
        update.stage=1
        update.save()
        # PAYMENT INTEGRATION
        amount = max(int(float(amount*100)),100)
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        client.set_app_details({"title": "Infy Cart", "version": "1.8.17"})
        
        payment_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'order_{Order.order_id}',
            'payment_capture': '1'
        }

        razorpay_order = client.order.create(data=payment_data)
        order_id = razorpay_order['id']
        Order.razorpay_id=order_id
        Order.save()
        return render(request, 'razorpaytest.html', {'order_id': order_id, 'key': settings.RAZORPAY_API_KEY, 'name': name, 'email': email, "phone": phone, "address": address1})

    return render(request, 'checkout.html')

@csrf_exempt
def handlerequest(request):
    if request.method == 'POST':
        response = request.POST 
        try:
            param_dict={
                'razorpay_order_id':response.get('razorpay_order_id'),
                'razorpay_payment_id':response.get('razorpay_payment_id'),
                'razorpay_signature':response.get('razorpay_signature')
            }
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
            check = client.utility.verify_payment_signature(param_dict)
            status=client.utility.verify_payment_signature(param_dict)
            order = Orders.objects.get(razorpay_id=response.get('razorpay_order_id'))
            order.oid = param_dict.get('razorpay_payment_id')
            order.paymentstatus = 'PAID'
            order.payment_id=param_dict.get('razorpay_payment_id')
            order.save()
            #for seding email to user for order has placed
            # user=request.user
            # email_subject="Your Order is Placed"  
            # message=render_to_string('emailsucess.html',{
               
            #     'orderid':response.get('razorpay_order_id')
            # })
        
            # email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[user.email])
            # print("before sending itttt.........................")
            # email_message.send()
            # print("after sending itttt.........................")
            return render(request,'paymentstatus.html',{'status':True,'id':response.get('razorpay_order_id')})
        except:
            return render(request,'paymentstatus.html',{'status':False,'id':response.get('razorpay_order_id')})


def viewproduct(request,id):
    if not request.user.is_authenticated:
        return redirect('/auth/login')
    product=Product.objects.get(pk=id);
    qset=WishList.objects.filter(product=Product.objects.get(pk=id),user=request.user)
    print(len(qset))
    boolean=False
    
    if len(qset)!=0:
        boolean=True
        print("True")
    return render(request,'viewproduct.html',{'product':product,'boolean':boolean})


#to add the item into wishlist model/data base
def add_to_wishlist(request,product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(pk=product_id)
        WishList.objects.create(user=request.user, product=product)
        return redirect('viewproduct', id=product_id)
    else:
        return redirect('/auth/login')

def remove_from_wishlist(request,product_id):
    wishlist_rows = WishList.objects.filter(product=Product.objects.get(pk=product_id), user=request.user)
    wishlist_rows.delete()
    return redirect('viewproduct', id=product_id)
    
def wishlist_remove(request,id):
    wishlist_rows = WishList.objects.filter(product=Product.objects.get(pk=id), user=request.user)
    wishlist_rows.delete()
    return redirect('profile')
#to show the wishlist items to user
def wishlist(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')
    
    wishitems=WishList.objects.filter(user=request.user)
    return render(request,'whishlist.html',{'items':wishitems});






def blog(request):
    return render(request,'blog.html')


def subscribe(request):
    if request.method=='POST':
        email=request.POST.get('email');
        sub=Subscriber(email=email)
        sub.save()
    return redirect('/')

class FinalOderset():
    def __init__(self,original_id,order_id,amount,status,items,date,feedbackbool,stage,request_for_cancel):
        self.original_id=original_id
        self.order_id=order_id
        self.amount=amount
        self.status=status
        self.items=items
        self.date=date
        self.feedbackbool=feedbackbool
        self.stage=stage
        self.request_for_cancel=request_for_cancel
def profile(request):
    if not request.user.is_authenticated:
        return redirect('/auth/login')
    allorder=Orders.objects.filter(email=request.user.username)

    result=[] #for storing all objects 
    for order in allorder:
        if(order.paymentstatus!='PAID'):
            OrderUpdate.objects.get(order_id=order.order_id).delete()
            order.delete()
            continue
        original_id=order.razorpay_id
        order_id=order.order_id
        amount=order.amount
        status=OrderUpdate.objects.get(order_id=order_id).delivered
        items = json.loads(order.items_json)
        date=OrderUpdate.objects.get(order_id=order_id).timestamp
        feedbackbool=OrderUpdate.objects.get(order_id=order_id).feedbackbool
        stage=OrderUpdate.objects.get(order_id=order_id).stage
        request_for_cancel=OrderUpdate.objects.get(order_id=order_id).request_for_cancel
        finalobj=FinalOderset(original_id,order_id,amount,status,items,date,feedbackbool,stage,request_for_cancel)
        result.append(finalobj)

    allwishlist = WishList.objects.filter(user=request.user)
    wishlist=[]
    for i in allwishlist:
        wishlist.append(i.product)
    print(wishlist)
    try:
        userprofile=UserProfile.objects.get(user=request.user)
        boolean=True
    except:
        boolean=False
        userprofile=None

    return render(request,'profile.html',{'user':request.user,'userprofile':userprofile,'boolean':boolean,'myorders':result,'mywishlist':wishlist})
    



def editprofile(request):
    if request.method=='POST':
        temp=UserProfile.objects.filter(user=request.user)
        temp.delete()
        first_name=request.POST.get('first_name')
        phone=request.POST.get('phone')
        address1=request.POST.get('address1')
        address2=request.POST.get('address2')
        city=request.POST.get('city')
        first_name=request.POST.get('first_name')
        pincode=request.POST.get('pincode')
        country=request.POST.get('country')
        dob=request.POST.get('dob')
        gender=request.POST.get('gender')
        profilePicture=request.FILES.get('profilePicture')
        userprofile=UserProfile(user=request.user,profile_picture=profilePicture,phone=phone,address1=address1,address2=address2,city=city,pincode=pincode,country=country,dob=dob,gender=gender)
        userprofile.save()
        return redirect('/profile/')
    return render(request,'editprofile.html');



def trackorder(request, id):
    order = OrderUpdate.objects.get(order_id=id)
    order_percentage = order.stage * 25  
    return render(request, 'trackorder.html', {'order': order, 'order_percentage': order_percentage})


def feedback(request,id):
    if request.method=='POST':
        rate=request.POST.get('rate')
        desc=request.POST.get('desc')
        order=OrderUpdate.objects.get(order_id=id)
        order.feedbackraterate=rate
        order.feedbackdesc=desc
        order.feedbackbool=False
        order.save()
        return redirect('/profile/')
    return render(request,'feedback.html',{'id':id});


def cancelorder(request,id):
    if request.method=='POST':
        order=Orders.objects.get(order_id=id)
        orderupdate=OrderUpdate.objects.get(order_id=id)
        orderupdate.request_for_cancel=True;
        orderupdate.stage=-1
        orderupdate.save()
        order.save()
        reason=request.POST.get('reason')
        ordercancel=OrderCancel(order=order,updateorder=orderupdate,reason=reason)
        ordercancel.save()
        return redirect('/profile/')
    return  render(request,'cancelorder.html',{'id':id})
    
