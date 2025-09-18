from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta, datetime, time

import pandas as pd
import plotly.express as px

from .models import User, GroceryItem, WastedGroceryItem


# ----------------- AUTH -----------------
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )
        messages.success(request, "Registration successful!")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("profileuser")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")


# ----------------- INVENTORY -----------------
def add_item(request):
    if request.method == "POST":
        GroceryItem.objects.create(
            user=request.user,
            name=request.POST.get("name"),
            category=request.POST.get("category"),
            quantity=request.POST.get("quantity"),
            purchase=request.POST.get("purchase"),
            expiry=request.POST.get("expiry"),
            supplier=request.POST.get("supplier"),
            price=request.POST.get("price"),
            mrp=request.POST.get("mrp"),
        )
        return redirect("view_item")

    return render(request, "add_item.html")


def view_item(request):
    today = timezone.now().date()
    expired_items = GroceryItem.objects.filter(expiry__lt=today)

    for item in expired_items:
        item.quantity_wasted += item.quantity
        item.save()

        WastedGroceryItem.objects.create(
            user=item.user,
            name=item.name,
            quantity=item.quantity,
            reason="expired",
            waste_date=item.expiry
        )
        item.delete()

    items = GroceryItem.objects.all()
    return render(request, "view_item.html", {"items": items})


def edit_item(request, item_id):
    item = get_object_or_404(GroceryItem, id=item_id)
    if request.method == "POST":
        item.name = request.POST["name"]
        item.category = request.POST["category"]
        item.quantity = request.POST["quantity"]
        item.purchase = request.POST["purchase"]
        item.expiry = request.POST["expiry"]
        item.supplier = request.POST["supplier"]
        item.price = request.POST["price"]
        item.mrp = request.POST["mrp"]
        item.save()
        return redirect("view_item")
    return render(request, "edit_item.html", {"item": item})


def delete_item(request, item_id):
    item = get_object_or_404(GroceryItem, id=item_id)

    item.quantity_wasted += item.quantity
    item.save()

    WastedGroceryItem.objects.create(
        user=item.user,
        name=item.name,
        quantity=item.quantity,
        reason="manual",
        waste_date=timezone.now().date()
    )

    item.delete()
    return redirect("view_item")


def sell_item(request, item_id):
    item = get_object_or_404(GroceryItem, id=item_id)

    if request.method == "POST":
        sold_qty = int(request.POST.get("sold_qty"))
        if 0 < sold_qty <= item.remaining_quantity:
            item.sold_quantity += sold_qty
            item.save()
            messages.success(request, f"Sold {sold_qty} units of {item.name}")
            return redirect("view_item")
        else:
            messages.error(request, "Invalid quantity entered.")

    return render(request, "sell_item.html", {"item": item})


# ----------------- WASTE LOGGING -----------------
def mark_wasted(request, item_id):
    item = get_object_or_404(GroceryItem, id=item_id)
    wasted_qty = item.quantity
    reason = request.POST.get("reason", "manual")

    item.quantity_wasted += wasted_qty
    item.save()

    WastedGroceryItem.objects.create(
        user=request.user,
        name=item.name,
        quantity=wasted_qty,
        reason=reason,
        waste_date=timezone.now().date()
    )

    messages.success(request, f"{wasted_qty} units of {item.name} marked as wasted.")
    return redirect("waste_logged")


def waste_logged(request):
    wasted_items = WastedGroceryItem.objects.all().order_by("-waste_date")
    return render(request, "waste_logged.html", {"wasted_items": wasted_items})


# ----------------- REPORTS -----------------
def report(request):
    wasted_items = WastedGroceryItem.objects.all().values()
    df = pd.DataFrame(wasted_items)

    if df.empty:
        return render(request, "report.html", {
            "reason_chart": "",
            "daily_chart": "",
            "wasted_items_chart": ""
        })

    # Convert to datetime for plotting, but group by plain date
    df['waste_date'] = pd.to_datetime(df['waste_date'], errors='coerce').dt.date


    reason_chart = px.pie(
        df, names="reason", values="quantity", title="Waste by Reason"
    ).to_html(full_html=False)

    daily_chart = px.line(
        df.groupby("waste_date")["quantity"].sum().reset_index(),
        x="waste_date", y="quantity", title="Daily Waste Trend"
    ).to_html(full_html=False)

    all_wasted = (
        df.groupby("name")["quantity"].sum().reset_index().sort_values(by="quantity", ascending=False)
    )
    wasted_items_chart = px.bar(
        all_wasted, x="name", y="quantity", title="All Wasted Items", color="quantity"
    ).to_html(full_html=False)

    return render(request, "report.html", {
        "reason_chart": reason_chart,
        "daily_chart": daily_chart,
        "wasted_items_chart": wasted_items_chart
    })


def weekly_waste_dashboard(request):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)

    waste_data = (
        WastedGroceryItem.objects
        .filter(waste_date__range=[start_date, end_date])
        .values("category")
        .annotate(total_wasted=Sum("quantity"))
    )

    categories = [w["category"] for w in waste_data]
    quantities = [w["total_wasted"] for w in waste_data]

    fig_bar = px.bar(
        x=categories, y=quantities,
        labels={"x": "Category", "y": "Quantity Wasted"},
        title="Weekly Waste by Category"
    )
    bar_html = fig_bar.to_html(full_html=False)

    return render(request, "report.html", {"bar_html": bar_html})


# ----------------- DASHBOARDS -----------------
def expiring_soon(request):
    today = timezone.now().date()
    soon = today + timedelta(days=3)

    items = GroceryItem.objects.filter(expiry__lte=soon)

    return render(request, "expiring_soon.html", {
        "items": items,
        "today": today,
        "soon": soon
    })


def profile(request):
    today = timezone.now().date()

    expired_items = GroceryItem.objects.filter(expiry__lt=today)
    for item in expired_items:
        WastedGroceryItem.objects.create(
            user=item.user,
            name=item.name,
            quantity=item.quantity,
            reason="expired",
            waste_date=item.expiry
        )
        item.delete()

    three_days = today + timedelta(days=3)

    expiring_count = GroceryItem.objects.filter(
        expiry__lte=three_days, expiry__gte=today
    ).count()

    available_items = GroceryItem.objects.filter(expiry__gte=today).count()
    wasted_count = WastedGroceryItem.objects.count()

    category_counts = (
        GroceryItem.objects.filter(expiry__gte=today)
        .values("category")
        .annotate(total=Count("id"))
        .order_by("category")
    )

    return render(request, "profile.html", {
        "expiring_count": expiring_count,
        "available_items": available_items,
        "wasted_count": wasted_count,
        "category_counts": category_counts,
    })


def inventory(request):
    category_counts = GroceryItem.objects.values("category").annotate(total=Count("id"))
    return render(request, "inventory.html", {"category_counts": category_counts})


@login_required
def savings(request):
    items = GroceryItem.objects.filter(user=request.user)
    wasted_items = WastedGroceryItem.objects.filter(user=request.user)

    savings_data = []
    total_profit, total_loss = 0, 0

    for item in items:
        sold_qty = item.sold_quantity
        wasted_qty = item.quantity_wasted
        remaining_qty = item.remaining_quantity

        profit = sold_qty * (item.mrp - item.price)
        item_wasted_records = wasted_items.filter(name__iexact=item.name.strip())
        loss = sum([w.quantity * item.price for w in item_wasted_records])
        net_result = profit - loss
        net_status = "profit" if net_result >= 0 else "loss"

        total_profit += profit
        total_loss += loss

        savings_data.append({
            "name": item.name,
            "mrp": item.mrp,
            "price": item.price,
            "sold_qty": sold_qty,
            "wasted_qty": wasted_qty,
            "remaining_qty": remaining_qty,
            "profit": profit,
            "loss": loss,
            "net_result": net_result,
            "net_status": net_status,
        })

    net_total = total_profit - total_loss
    net_total_status = "profit" if net_total >= 0 else "loss"

    return render(request, "savings.html", {
        "savings_data": savings_data,
        "total_profit": total_profit,
        "total_loss": total_loss,
        "net_total": net_total,
        "net_total_status": net_total_status
    })


@login_required
def profileuser(request):
    return render(request, "profile.html", {
        "store_name": request.user.username,
        "expiring_count": 0,
        "available_items": 0,
        "wasted_count": 0,
        "category_counts": []
    })
