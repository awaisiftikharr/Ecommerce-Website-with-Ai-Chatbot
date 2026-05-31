from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from django.core.paginator import Paginator
# AI Imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
# Auth Imports
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# --- 1. STORE (HOMEPAGE) ---
def store(request):
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
        except:
            customer = Customer.objects.create(user=request.user, name=request.user.username, email=request.user.email)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = 0

    q = request.GET.get('q') if request.GET.get('q') != None else ''
    products_list = Product.objects.filter(name__icontains=q).order_by('-id')
    
    paginator = Paginator(products_list, 6) 
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

# --- 2. CART PAGE ---
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = 0

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

# --- 3. CHECKOUT PAGE ---
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = 0

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

# --- 4. UPDATE ITEM (ADD TO CART) ---
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

# --- 5. PROCESS ORDER (PAYMENT) ---
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == float(order.get_cart_total):
            order.complete = True
        order.save()

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)

# --- 6. PRODUCT DETAIL (AI RECOMMENDATIONS) ---
def product_detail(request, pk):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = 0

    product = Product.objects.get(id=pk)

    # AI Logic
    products = list(Product.objects.all().values('id', 'name', 'description'))
    df = pd.DataFrame(products)
    recommendations = []
    
    if len(df) > 1:
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['description'].fillna(''))
        idx_list = df.index[df['id'] == product.id].tolist()
        if idx_list:
            idx = idx_list[0]
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:4]
            product_indices = [i[0] for i in sim_scores]
            rec_ids = df.iloc[product_indices]['id'].tolist()
            recommendations = Product.objects.filter(id__in=rec_ids)

    context = {'product':product, 'cartItems':cartItems, 'recommendations':recommendations}
    return render(request, 'store/product_detail.html', context)

# --- 7. CHATBOT LOGIC ---
def chatbot_response(request):
    user_message = request.GET.get('msg', '').lower()
    response = "I am sorry, I didn't understand. Try asking 'Do you have laptops?' or 'Price of phone'."
    
    greetings = ["hello", "hi", "hey", "salam"]
    price_keywords = ["price", "cost", "much", "worth"]
    stock_keywords = ["have", "stock", "find", "search", "available"]
    products = Product.objects.all()

    if any(word in user_message for word in greetings):
        response = "Hello! Welcome to SmartFinds. How can I help you today?"
    elif any(word in user_message for word in price_keywords):
        found = False
        for p in products:
            if p.name.lower() in user_message or user_message in p.name.lower():
                response = f"The price of {p.name} is ${p.price}."
                found = True
                break
        if not found:
            response = "I can check prices! Which product are you asking about?"
    elif any(word in user_message for word in stock_keywords):
        found_items = []
        for p in products:
            if p.name.lower() in user_message or user_message in p.name.lower():
                found_items.append(p.name)
        if found_items:
             response = f"Yes! We have these items: {', '.join(found_items[:3])}."
        else:
             response = "Sorry, I couldn't find that specific item."
    else:
        for p in products:
            if p.name.lower() in user_message or user_message in p.name.lower():
                response = f"Yes, we have {p.name}. It costs ${p.price}."
                return JsonResponse({'response': response})

    return JsonResponse({'response': response})

# --- 8. USER AUTHENTICATION (THIS WAS MISSING!) ---
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create Customer profile immediately
            Customer.objects.create(user=user, name=user.username, email=user.email)
            login(request, user)
            return redirect('store')
    else:
        form = UserCreationForm()
    context = {'form':form}
    return render(request, 'store/register.html', context)

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('store')
    else:
        form = AuthenticationForm()
    context = {'form':form}
    return render(request, 'store/login.html', context)

def logout_user(request):
    logout(request)
    return redirect('store') 