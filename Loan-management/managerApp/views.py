from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import date

from managerApp.forms import AdminLoginForm, LoanCategoryForm
from loanApp.models import loanCategory, loanRequest, CustomerLoan, loanTransaction
from loginApp.models import CustomerSignUp


def superuser_login_view(request):
    """Handles superuser (admin) login."""
    if request.user.is_authenticated:
        return redirect('home')

    form = AdminLoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_superuser:
                login(request, user)
                return redirect('managerApp:dashboard')
            else:
                context = {'form': form, 'error': "You are not a Super User"}
                return render(request, 'admin/adminLogin.html', context)
        else:
            context = {'form': form, 'error': "Invalid Username or Password"}
            return render(request, 'admin/adminLogin.html', context)

    return render(request, 'admin/adminLogin.html', {'form': form, 'user': "Admin Login"})


@staff_member_required(login_url='/manager/admin-login')
def dashboard(request):
    """Displays admin dashboard with loan statistics."""
    context = {
        'totalCustomer': CustomerSignUp.objects.count(),
        'request': loanRequest.objects.filter(status='pending').count(),
        'approved': loanRequest.objects.filter(status='approved').count(),
        'rejected': loanRequest.objects.filter(status='rejected').count(),
        'totalLoan': CustomerLoan.objects.aggregate(total=Sum('total_loan'))['total'] or 0,
        'totalPayable': CustomerLoan.objects.aggregate(total=Sum('payable_loan'))['total'] or 0,
        'totalPaid': loanTransaction.objects.aggregate(total=Sum('payment'))['total'] or 0,
    }

    return render(request, 'admin/dashboard.html', context)


@staff_member_required(login_url='/manager/admin-login')
def add_category(request):
    """Allows admin to add new loan categories."""
    form = LoanCategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('managerApp:dashboard')
    return render(request, 'admin/admin_add_category.html', {'form': form})


@staff_member_required(login_url='/manager/admin-login')
def total_users(request):
    """Displays list of all registered users."""
    users = CustomerSignUp.objects.all()
    return render(request, 'admin/customer.html', {'users': users})


@staff_member_required(login_url='/manager/admin-login')
def user_remove(request, pk):
    """Deletes a user and their linked customer account."""
    CustomerSignUp.objects.filter(id=pk).delete()
    User.objects.filter(id=pk).delete()
    return redirect('managerApp:users')


@staff_member_required(login_url='/manager/admin-login')
def loan_request(request):
    """Displays all pending loan requests."""
    loanrequest = loanRequest.objects.filter(status='pending')
    return render(request, 'admin/request_user.html', {'loanrequest': loanrequest})


@staff_member_required(login_url='/manager/admin-login')
def approved_request(request, id):
    """Approves a pending loan request and updates customer's loan record."""
    loan_obj = loanRequest.objects.get(id=id)
    loan_obj.status_date = date.today().strftime("%B %d, %Y")
    loan_obj.status = 'approved'
    loan_obj.save()

    year = loan_obj.year
    approved_customer = loan_obj.customer
    interest = int(loan_obj.amount) * 0.12 * int(year)
    payable_amount = int(loan_obj.amount) + interest

    customer_loan, created = CustomerLoan.objects.get_or_create(
        customer=approved_customer,
        defaults={'total_loan': loan_obj.amount, 'payable_loan': payable_amount}
    )

    if not created:
        customer_loan.total_loan += int(loan_obj.amount)
        customer_loan.payable_loan += payable_amount
        customer_loan.save()

    return redirect('managerApp:loan-request')


@staff_member_required(login_url='/manager/admin-login')
def rejected_request(request, id):
    """Rejects a pending loan request."""
    loan_obj = loanRequest.objects.get(id=id)
    loan_obj.status_date = date.today().strftime("%B %d, %Y")
    loan_obj.status = 'rejected'
    loan_obj.save()
    return redirect('managerApp:loan-request')


@staff_member_required(login_url='/manager/admin-login')
def approved_loan(request):
    """Displays all approved loans."""
    approvedLoan = loanRequest.objects.filter(status='approved')
    return render(request, 'admin/approved_loan.html', {'approvedLoan': approvedLoan})


@staff_member_required(login_url='/manager/admin-login')
def rejected_loan(request):
    """Displays all rejected loans."""
    rejectedLoan = loanRequest.objects.filter(status='rejected')
    return render(request, 'admin/rejected_loan.html', {'rejectedLoan': rejectedLoan})


@staff_member_required(login_url='/manager/admin-login')
def transaction_loan(request):
    """Displays all loan transactions."""
    transactions = loanTransaction.objects.all()
    return render(request, 'admin/transaction.html', {'transactions': transactions})




