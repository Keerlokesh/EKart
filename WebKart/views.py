from django.shortcuts import render
from django.http import HttpResponse
from .models import product,Contact,Orders,OrdersUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from .Paytm import Checksum

MERCHANT_KEY = 'MJxTZM76674390085957'


def index(request):
    products = product.objects.all()
    #print(products)

    # params = {'no_of_slide':nSlides,'range':range(1,nSlides) ,'product':products}
    #allprods=[[products,range(1,nSlides),nSlides],
    #         [products,range(1,nSlides),nSlides]]


    allprods=[]
    catprods =product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = product.objects.filter(category=cat)
        n = len(products)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allprods.append([prod,range(1,nSlides),nSlides])

    params = {'allprods': allprods}
    return render(request,'WebKart/index.html',params)

def searchMatch(query,item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    products = product.objects.all()
    allprods = []
    catprods = product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query,item)]
        n = len(products)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allprods.append([prod, range(1, nSlides), nSlides])


    params = {'allprods': allprods,"msg":""}
    if len(allprods) == 0 or len(query) < 2:
        params = {'msg': "Please make sure to enter relevant query!"}
    return render(request, 'WebKart/search.html', params)

def about(request):
    return render(request,'WebKart/about.html')

def contact(request):
    thank = False
    if request.method == 'POST':
        name = request.POST.get('name','none')
        email = request.POST.get('email','none')
        city = request.POST.get('city','none')
        state = request.POST.get('state','none')
        mobile = request.POST.get('mobile','none')
        suggestion = request.POST.get('suggestion', 'none')
        contact = Contact(name=name,email=email,city=city,state=state,mobile=mobile,suggestion=suggestion)
        contact.save()
        thank = True
    return render(request,'WebKart/contact.html',{'thank':thank})

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrdersUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status": "success","updates": updates,"itemsjson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status": "noItem"}')
        except Exception as e:
            return HttpResponse('{"status": "error"}')

    return render(request, 'WebKart/tracker.html')

def productview(request, myid):
    #managing Products
    pname = ''
    products = product.objects.all()
    allprods = []
    Product = product.objects.filter(id=myid)
    catprods = product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    print(cats)
    for cat in cats:
        prod = product.objects.filter(category=cat)
        n = len(products)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allprods.append([prod,range(1,nSlides),nSlides])

    return render(request,'WebKart/products.html',{'product':Product[0],'allprods':allprods})

def checkout(request):
    if request.method == 'POST':
        items_json = request.POST.get('itemsjson', '')
        name = request.POST.get('name', 'none')
        email = request.POST.get('email', 'none')
        address = request.POST.get('address1', 'none') + '' + request.POST.get('address2', 'none')
        city = request.POST.get('city', 'none')
        state = request.POST.get('state', 'none')
        zip_code = request.POST.get('zip_code', 'none')
        phone = request.POST.get('phone', 'none')
        amount = request.POST.get('totalPrice')
        order = Orders(items_json=items_json,name=name,amount=amount, email=email,address=address, city=city, state=state, zip_code=zip_code, phone=phone)
        order.save()
        update = OrdersUpdate(order_id=order.order_id,update_desc="Under Processing!")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'WebKart/checkout.html',{'thank':thank,'id':id})
        #Request Paytm to transfer money
        param_dict = {
            "MID": "MJxTZM76674390085957",
            "ORDER_ID": str(order.order_id),
            "CUST_ID": email,
            "TXN_AMOUNT": str(amount),
            "CHANNEL_ID": "WEB",
            "INDUSTRY_TYPE_ID": "Retail",
            "WEBSITE": "WEBSTAGING",
            "CALLBACK_URL": "http://127.0.0.1:8000/WebKart/handlerequest/"
        }


        #return render(request,'WebKart/paytm.html',{'param_dict':param_dict})

    return render(request, 'WebKart/checkout.html')

@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'WebKart/paymentstatus.html', {'response': response_dict})
