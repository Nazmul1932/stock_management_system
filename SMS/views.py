from django.http import HttpResponse
from django.shortcuts import render, redirect
import csv
from .forms import *
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def home(request):
    title = 'Welcome this is the home page'
    context = {
        'title': title
    }
    return render(request, 'home.html', context)


@login_required
def list_items(request):
    title = 'List of Items'
    form = StockSearchForm(request.POST or None)
    items = Stock.objects.all()
    if request.method == 'POST':
        items = Stock.objects.filter(item_name__icontains=form['item_name'].value())
        if form['export_to_csv'].value():
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
            writer = csv.writer(response)
            writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
            instance = items
            for stock in instance:
                writer.writerow([stock.category, stock.item_name, stock.quantity])
            return response

    context = {
        'title': title,
        'items': items,
        'form': form
    }
    return render(request, 'list_item.html', context)


@login_required
def add_items(request):
    form = StockCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully Added Items')
        return redirect('/list_items')
    context = {
        'form': form,
        'title': "Add Item",
    }
    return render(request, 'add_items.html', context)


@login_required
def add_category(request):
    form = CategoryCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully Added Category')
        return redirect('/list_items')
    context = {
        'form': form,
        'title': "Add Item",
    }
    return render(request, 'add_category.html', context)


def update_items(request, pk):
    items = Stock.objects.get(id=pk)
    form = StockUpdateForm(instance=items)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=items)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Updated Item')
            return redirect('/list_items')

    context = {
        'form': form
    }
    return render(request, 'add_items.html', context)


def delete_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    if request.method == 'POST':
        queryset.delete()
        messages.success(request, 'Successfully Deleted This Item')
        return redirect('/list_items')
    return render(request, 'delete_items.html')


def stock_detail(request, pk):
    items = Stock.objects.get(id=pk)
    context = {
        "items": items,
        "title": items.item_name
    }
    return render(request, "stock_detail.html", context)


def issue_items(request, pk):
    items = Stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=items)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.receive_quantity = 0
        instance.quantity -= instance.issue_quantity
        instance.issue_by = str(request.user)
        messages.success(request, "Issued SUCCESSFULLY. " + str(instance.quantity) + " " + str(
            instance.item_name) + "s now left in Store")
        instance.save()

        return redirect('/stock_detail/' + str(instance.id))
    # return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": 'Issue ' + str(items.item_name),
        "items": items,
        "form": form,
        "username": 'Issue By: ' + str(request.user),
    }
    return render(request, "add_items.html", context)


def receive_items(request, pk):
    items = Stock.objects.get(id=pk)
    form = ReceiveForm(request.POST or None, instance=items)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.issue_quantity = 0
        instance.quantity += instance.receive_quantity
        instance.save()
        messages.success(request, "Received SUCCESSFULLY. " + str(instance.quantity) + " " + str(
            instance.item_name) + "s now in Store")
        return redirect('/stock_detail/' + str(instance.id))
    # return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "title": 'Receive ' + str(items.item_name),
        "items": items,
        "form": form,
        "username": 'Receive By: ' + str(request.user),
    }
    return render(request, "add_items.html", context)


def reorder_level(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReorderLevelForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Reorder level for " + str(instance.item_name) + " is updated to " + str(
            instance.reorder_level))

        return redirect("list_items")
    context = {
        "instance": queryset,
        "form": form,
    }
    return render(request, "add_items.html", context)


@login_required
def list_history(request):
    header = 'LIST OF ITEMS'
    items = StockHistory.objects.all()
    context = {
        "header": header,
        "items": items,
    }
    return render(request, "list_history.html", context)
