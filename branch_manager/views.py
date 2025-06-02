from decimal import Decimal
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
from django.utils.datastructures import MultiValueDictKeyError
from reportlab.platypus import *
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from django.db.models import Max
import pandas as pd
from django.http import HttpResponse
from .forms import *

import xlsxwriter
import os

import datetime
import calendar
import openpyxl
import xlwt
import zipfile
import dateutil.relativedelta
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password  # For hashing the password
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
import random
import string

def generate_random_password(length=8):
    """Generate a random password with letters and digits"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def dashboard(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""
    user = request.user

    # Fetch all transaction requests and order them by latest first
    if user.user == 'MID':  # Branch Head
        transactions = TransactionRequest.objects.filter(branch_head=user).order_by('-created_at')
    elif user.user == 'LOW':  # Agent
        transactions = TransactionRequest.objects.filter(agent=user, transaction_type='CREDIT').order_by('-created_at')
    else:  # Admin or higher-level user
        transactions = TransactionRequest.objects.all().order_by('-created_at')

    return render(request, "branch_manager/dashboard-page.html", {"msg1": msg1, "msg": msg, "transactions": transactions})

def registration(request):
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    else:
        msg1 = ''

    form = UserRegistrationForm()
    if request.method == "POST":
        user = CustomUser.objects.all()
        form = UserRegistrationForm(request.POST)
        # emails = email_validation(request, form.data['email'].lower(), user)
        # phone = phone_number(form.data.get('phone'))
        
        # if emails: 
        #     return redirect('all_users')
        # elif phone:
        #     request.session["massage1"] = 'Please Enter Valid Phone Number !!'
        #     return redirect('all_users')
        if form.is_valid():
            form.save()
            request.session["massage"] = 'User Added Successfully !!'
            return redirect("all_users")
        else:
            request.session["massage1"] = 'Please Enter Valid Information !!'
            return redirect('all_users')
    else:
        form = UserRegistrationForm()
    return render(request, "branch_manager/create-user.html/", {"form": form, "msg_danger": msg1})

def loginuser(request):
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    else:pass
        
    
    if request.method == 'POST':
        u = request.POST.get('email')
        p = request.POST.get('password')
        user = authenticate(email=u, password=p)
        if user is not None:
            login(request, user)
            request.session["massage"] = 'Welcome To Satguru Bank Services'
            return redirect('dashboard')
        else:
            request.session["massage1"] = 'Please Enter Valid Credentials!!!'
            return redirect('loginuser')
    template_name = 'branch_manager/Login.html'
    return render(request, template_name, {"msg1": msg1})

# def branch_manager(request):
#     msg1 = ''
#     if "massage1" in request.session:
#         msg1 = request.session["massage1"]
#         del request.session["massage1"]
#     else:
#         msg1 = ''

#     form = UserRegistrationForm()
#     if request.method == "POST":
#         user = CustomUser.objects.all()
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             request.session["massage"] = 'User Added Successfully !!'
#             return redirect("branch_manager")
#         else:
#             request.session["massage1"] = 'Please Enter Valid Information !!'
#             return redirect('branch_manager')
        
#     else:
#         form = UserRegistrationForm()
#         branch_heads = CustomUser.objects.filter(user='MID')
#     return render(request, "branch_manager/branch-manager.html/", {"form": form, "msg1": msg1, "branch_heads": branch_heads})

def transactions_report(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""
    user = request.user

    # Fetch all transaction requests and order them by latest first
    if user.user == 'MID':  # Branch Head
        transactions = TransactionRequest.objects.filter(branch_head=user).order_by('-created_at')
    elif user.user == 'LOW':  # Agent
        transactions = TransactionRequest.objects.filter(agent=user, transaction_type='CREDIT').order_by('-created_at')
    else:  # Admin or higher-level user
        transactions = TransactionRequest.objects.all().order_by('-created_at')

    return render(request, "branch_manager/transactions.html", {"msg1": msg1, "msg": msg, "transactions": transactions})


def branch_manager(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""
    form = UserRegistrationForm()

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            random_password = generate_random_password()
            print('random_password', random_password)
            random_password = "Pass@1234"
            user.set_password(random_password)  # Hash the password
            user.save()
            request.session["massage"] = "User Added Successfully! Email Sent."
            return redirect("branch_manager")
        else:
            request.session["massage1"] = "Please Enter Valid Information!"
            return redirect("branch_manager")

    branch_heads = CustomUser.objects.filter(user="MID")
    return render(request, "branch_manager/branch-manager.html", {"form": form, "msg1": msg1, "msg": msg, "branch_heads": branch_heads})


def agent(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""
    current_user = request.user

    if current_user.is_staff:
        branch_heads = CustomUser.objects.filter(user="MID")
    else:
        branch_heads = CustomUser.objects.filter(user="MID", id=current_user.id)

    if current_user.is_staff:
        agents_with_assignments = AgentAssignment.objects.select_related(
            "agents", "branch_head", "agents__branch"
        ).filter(agents__user="LOW")
    else:
        agents_with_assignments = AgentAssignment.objects.select_related(
            "agents", "branch_head", "agents__branch"
        ).filter(agents__user="LOW", branch_head=current_user)

    if request.method == "POST":
        agent_name = request.POST.get("full_name")
        agent_email = request.POST.get("email")
        agent_phone = request.POST.get("phone")
        branch_head_id = request.POST.get("branch_head")
        agent_area = request.POST.get("area")

        if CustomUser.objects.filter(email=agent_email).exists():
            request.session["massage1"] = "This email is already in use. Please choose another one."
            return redirect("agent")

        random_password = generate_random_password()
        print('random_password', random_password)
        random_password = 'Pass@1234'
        # random_password = "Pass@1234"

        agent_user = CustomUser(
            name=agent_name,
            email=agent_email,
            user="LOW",
            phone=agent_phone,
        )
        agent_user.set_password(random_password)  # Hash the password
        agent_user.save()

        agent_registration = AgentAssignment(
            agents=agent_user,
            branch_head=CustomUser.objects.get(id=branch_head_id),
            area=agent_area,
        )
        agent_registration.save()
        request.session["massage"] = "User Added Successfully! Email Sent."
        return redirect("agent")

    return render(
        request,
        "branch_manager/agent.html",
        {"msg1": msg1, "msg": msg, "agents": agents_with_assignments, "branch_heads": branch_heads},
    )

def update_agent_assignment(request, assignment_id):
    agent = get_object_or_404(CustomUser, id=assignment_id)
    assignment = get_object_or_404(AgentAssignment, agents=agent)
    msg = ""
    msg1 = ''

    if "massage1" in request.session:
        msg1 = request.session.pop("massage1")
    elif "massage" in request.session:
        msg = request.session.pop("massage")

    if request.method == "POST":
        agent = request.POST["agents"]
        agents = get_object_or_404(AgentAssignment, agents=agent)
        branch_head = request.POST["branch_head"]
        area = request.POST["area"]
        password = "Pass@1234"
        form = AgentAssignmentForm(
            agents=agents,
            branch_head = branch_head,
            area=area
        )

        if form.is_valid():
            agent_assignment = form.save(commit=False)
            # Assign the currently logged-in branch manager if they're not staff
            if not request.user.is_staff:
                agent_assignment.branch_head = request.user
            agent_assignment.save()
            request.session["massage"] = "Assignment updated successfully!"
            return redirect("agent")
        else:
            request.session["massage1"] = "Please correct the form errors."
            return redirect("update_agent_assignment", assignment_id=assignment.agents.id)
    else:
        form = AgentAssignmentForm(instance=assignment)
    return render(request, "branch_manager/update-agent.html", {
        "form": form,
        "assignment": assignment,
        "msg": msg,
        "msg1": msg1
    })

# Action to approve the credit request
# Approve Transaction (Credit/Debit)
def approve_transaction(request, request_id):
    transaction_request = get_object_or_404(TransactionRequest, id=request_id)

    if transaction_request.branch_head == request.user:
        # Update the status to approved
        if transaction_request.status == 'APPROVED':
            request.session["massage1"] = "Request Already Approved."
            return redirect('transaction')
        if transaction_request.status == 'REJECTED':
            request.session["massage1"] = "Request Already Rejected."
            return redirect('transaction')

        transaction_request.status = 'APPROVED'
        request.session["massage"] = "Request Approved Successfully."
        transaction_request.save()

        # Apply the transaction to the customer's account
        if transaction_request.transaction_type == 'CREDIT':
            transaction_request.customer.credit_amount += transaction_request.amount
        elif transaction_request.transaction_type == 'DEBIT':
            transaction_request.customer.debit_amount += transaction_request.amount
        
        transaction_request.customer.save()

    return redirect('transaction')


# Reject Transaction (Credit/Debit)
def reject_transaction(request, request_id):
    transaction_request = get_object_or_404(TransactionRequest, id=request_id)

    if transaction_request.branch_head == request.user:
        # Update the status to rejected
        if transaction_request.status == 'APPROVED':
            request.session["massage1"] = "Request Already Approved."
            return redirect('transaction')

        request.session["massage"] = "Request Rejected Successfully."
        transaction_request.delete()

    return redirect('transaction')


def create_branch(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('branch')  # Redirect to branch list page after successful creation
    else:
        form = BranchForm()
        branches = Branch.objects.all()
    return render(request, 'branch_manager/branch.html', {'form': form, 'branches': branches})


def generate_account_number():
    today = datetime.datetime.now().strftime('%Y%m%d')  # Format: YYYYMMDD
    # Filter customers created today based on account number prefix
    latest_account = Customer.objects.filter(account_number__startswith=today).aggregate(
        Max('account_number')
    )['account_number__max']
    
    if latest_account:
        # Extract last 3 digits and increment
        last_increment = int(latest_account[-3:])
        new_increment = f"{last_increment + 1:03d}"
    else:
        # First of the day
        new_increment = "001"
    
    new_account_number = f"{today}{new_increment}"

    return new_account_number


def create_customer(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""

    user = request.user
    # If the user is an agent, show only customers assigned to this agent
    # if user.user == 'LOW':  # If the user is an Agent
    #     return redirect("search_customer")
    if user.user == 'LOW':  # If the user is a Branch Head
        customers = Customer.objects.filter(status='ACTIVE')
    else:
        
        customers = Customer.objects.all() 

    if request.method == 'POST':
        form = CustomerForm(request.POST, user=request.user)  # Pass the logged-in user to the form
        if form.is_valid():
            customer = form.save(commit=False)
            customer.account_number = generate_account_number()  # Auto-generate unique account number
            customer.save()
            request.session["massage"] = "Customer added successfully!"
            return redirect('customer')  # Redirect to customer list or any other page
        else:
            request.session["massage1"] = "Enter Valid Details!"
            return redirect('customer')
    else:
        form = CustomerForm(user=request.user)  # Pass the logged-in user to the form
        nominee_form = NomineeForm()
        document_form = DocumentForm()
    return render(request, 'branch_manager/create_customer.html', {"msg1": msg1, "msg": msg, 'form': form, 'nominee_form' : nominee_form, 'document_form': document_form, 'customers': customers})

def credit_premium(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""

    return redirect("search_customer")

def search_customer(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""

    if request.method == 'POST':
        account_no = request.POST["account_number"]
        customer_id = Customer.objects.filter(account_number=account_no).first()
        if customer_id == None:
            request.session["massage1"] = "Bank Account Not Found!"
            return redirect('search_customer')
        if customer_id.status == "DEACTIVE":
            request.session["massage1"] = "Customer Is Not Active!"
            return redirect('search_customer')
        request.session["customer_id"] = customer_id.id
        return redirect('search')  # Or wherever you want to redirect after saving nominee
    
    return render(request, 'branch_manager/search-customer.html', {"msg1": msg1, "msg": msg,
    })


def transfer_customer(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""

    if request.method == 'POST':
        account_no = request.POST["account_number"]
        customer_id = Customer.objects.filter(account_number=account_no).first()
        reciver_account_no = request.POST["reciever_account_number"]
        reciver_customer_id = Customer.objects.filter(account_number=reciver_account_no).first()
        if customer_id == None or reciver_customer_id == None:
            request.session["massage1"] = "Bank Account Not Found!"
            return redirect('transfer_customer')
        if customer_id.status == "DEACTIVE" or reciver_customer_id.status == "DEACTIVE":
            request.session["massage1"] = "Customer Is Not Active!"
            return redirect('transfer_customer')
        request.session["customer_id"] = customer_id.id
        request.session["reciever_customer_id"] = reciver_customer_id.id
        return redirect('transfer_search')  # Or wherever you want to redirect after saving nominee
    
    return render(request, 'branch_manager/transfer-customer.html', {"msg1": msg1, "msg": msg,
    })


def transfer_search(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""

    customer_id = ""
    if "customer_id" in request.session:
        customer_id = request.session["customer_id"]
        del request.session["customer_id"]
    else:
        request.session["massage1"] = "Please Search Again!"
        return redirect("transfer_customer")
    
    reciever_customer_id = ""
    if "reciever_customer_id" in request.session:
        reciever_customer_id = request.session["reciever_customer_id"]
        del request.session["reciever_customer_id"]
    else:
        request.session["massage1"] = "Please Search Again!"
        return redirect("transfer_customer")

    main_customers = Customer.objects.get(id=int(customer_id))
    reciver_customer = Customer.objects.get(id=int(reciever_customer_id))
    return render(request, 'branch_manager/transfer-form.html', {'customer': main_customers, "reciver" : reciver_customer,"msg":msg , "msg1": msg1})

def transfer_amount(request, sender_id, receiver_id):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        remarks = request.POST.get('remarks', '').strip()
        current_user = request.user
        try:
            amount = Decimal(amount)
        except:
            request.session["massage1"] = "Invalid amount."
            return redirect("transfer_customer")

        if amount <= 0:
            request.session["massage1"] = "Amount must be greater than zero."
            return redirect("transfer_customer")

        sender = get_object_or_404(Customer, id=sender_id)
        
        if sender.credit_amount < amount:
            request.session["massage1"] = "Sender does not have enough balance."
            return redirect("transfer_customer")
        
        transaction_request = TransactionRequest(
                transaction_type='DEBIT',
                agent=current_user if current_user.user == 'LOW' else None,  # Only set if agent
                customer=sender,
                amount=amount,
                branch_head=current_user,  # Set branch head if agent, else set self
                status='APPROVED' if current_user.user == 'MID' else 'PENDING'  # Auto approve if branch head
            )
        if transaction_request.status == 'APPROVED':
            sender.credit_amount -= int(amount)
            sender.save()
        transaction_request.save()

        receiver = get_object_or_404(Customer, id=receiver_id)
        transaction_request = TransactionRequest(
                transaction_type='CREDIT',
                agent=current_user if current_user.user == 'LOW' else None,  # Only set if agent
                customer=receiver,
                amount=amount,
                branch_head=current_user,  # Set branch head if agent, else set self
                status='APPROVED' if current_user.user == 'MID' or current_user.user == 'TOP' else 'PENDING'  # Auto approve if branch head
            )
        
        if transaction_request.status == 'APPROVED':
            receiver.credit_amount += int(amount)
            receiver.save()
        transaction_request.save()

        # Create TransferRecord
        TransferRecord.objects.create(
            sender=sender,
            receiver=receiver,
            branch_manager=request.user,
            amount=amount,
            remarks=remarks,
            transfer_date=timezone.now()
        )

        request.session["massage"] = f"₹{amount} transferred from {sender.name} to {receiver.name}."
        return redirect("transfer_customer")  # Update this URL to your actual post-transfer redirect

    else:
        return redirect("transfer_customer")
    
def transfer_records(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""

    transfers = TransferRecord.objects.filter(branch_manager=request.user).order_by('-transfer_date')
    return render(request, 'branch_manager/transfer_records.html', {'transfers': transfers})
    


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        user = CustomUser.objects.get(email=email)
        return redirect('search')
    
    return render(request, 'branch_manager/forgot-password.html', {
    })


def search(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""

    customer_id = ""
    if "customer_id" in request.session:
        customer_id = request.session["customer_id"]
        del request.session["customer_id"]
    else:
        request.session["massage1"] = "Please Search Again!"
        return redirect("search_customer")
    # If the user is an agent, show only customers assigned to this agent 
    customers = Customer.objects.get(id=int(customer_id))
    current_date = datetime.datetime.now()
    return render(request, 'branch_manager/customer-form.html', {'customer': customers, "current_date":current_date,"msg":msg , "msg1": msg1})


def add_nominee(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    if request.method == 'POST':
        nominee_form = NomineeForm(request.POST)
        if nominee_form.is_valid():
            nominee = nominee_form.save(commit=False)
            nominee.customer = customer  # Link nominee to the customer
            nominee.save()
            return redirect('customer')  # Or wherever you want to redirect after saving nominee
    
    else:
        nominee_form = NomineeForm()

    return render(request, 'branch_manager/add-nominee.html', {
        'form': nominee_form,
        'customer': customer
    })


def see_nominee(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    nominees = Nominee.objects.filter(customer=customer)
    return render(request, 'branch_manager/see-nominee.html', {
        'nominees': nominees
    })

def add_documents(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.customer = customer
            document.save()
            return redirect('customer')  # Or another appropriate URL
    else:
        form = DocumentForm()
    
    return render(request, 'branch_manager/add-documents.html', {
        'form': form,
        'customer': customer,
    })

def view_documents(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    documents = Document.objects.filter(customer=customer)
    return render(request, 'branch_manager/view_documents.html', {
        'documents': documents,
        'customer': customer
    })

def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    document.delete()
    return redirect('view_documents')

def see_transation(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    transactions = TransactionRequest.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'branch_manager/see-transation.html', {
        'transactions': transactions,
        'customer' : customer
    })


def export_transactions_excel(request, customer_id):
    transactions = TransactionRequest.objects.filter(customer_id=customer_id)
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    data = [
        {
            "Transaction Type": tr.transaction_type,
            "Agent": tr.agent.name if tr.agent else "Agent Not Assign",
            "Customer": tr.customer.name if tr.customer else "",
            "Amount": tr.amount,
            "Status": tr.status,
            "Branch Head": tr.branch_head.name if tr.branch_head else "",
            "Date": tr.created_at.strftime('%Y-%m-%d'),
        }
        for tr in transactions
    ]

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="transactions_{current_date}.xlsx"'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Transactions')

    return response

def all_export_transactions_excel(request):
    user = request.user

    if user.user == 'MID':  # Branch Head
        transactions = TransactionRequest.objects.filter(branch_head=user).order_by('-created_at')
    elif user.user == 'LOW':  # Agent
        transactions = TransactionRequest.objects.filter(agent=user).order_by('-created_at')
    else:  # Admin or higher-level user
        transactions = TransactionRequest.objects.all().order_by('-created_at')

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    data = [
        {
            "Transaction Type": tr.transaction_type,
            "Agent": tr.agent.name if tr.agent else "Agent Not Assign",
            "Customer": tr.customer.name if tr.customer else "",
            "Amount": tr.amount,
            "Status": tr.status,
            "Branch Head": tr.branch_head.name if tr.branch_head else "",
            "Date": tr.created_at.strftime('%Y-%m-%d'),
        }
        for tr in transactions
    ]

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="transactions_{current_date}.xlsx"'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Transactions')

    return response


def export_transactions_pdf(request, customer_id):
    transactions = TransactionRequest.objects.filter(customer_id=customer_id)
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="transactions_{current_date}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Transaction Report")
    y -= 40

    # Define column titles and widths
    headers = ["Type", "Agent", "Customer", "Amount", "Status", "Branch Head", "Date"]
    col_widths = [60, 90, 90, 60, 60, 90, 70]
    x_start = 30

    # Draw header background
    p.setFillColor(colors.lightgrey)
    p.rect(x_start, y - 5, sum(col_widths), 20, fill=1)
    p.setFillColor(colors.black)

    # Draw headers
    p.setFont("Helvetica-Bold", 10)
    x = x_start
    for i, header in enumerate(headers):
        p.drawString(x + 2, y, header)
        x += col_widths[i]
    y -= 20

    # Draw rows
    p.setFont("Helvetica", 9)
    for tr in transactions:
        if y < 60:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica-Bold", 10)
            x = x_start
            for i, header in enumerate(headers):
                p.drawString(x + 2, y, header)
                x += col_widths[i]
            y -= 20
            p.setFont("Helvetica", 9)

        row = [
            tr.transaction_type,
            tr.agent.name if tr.agent else "Agent Not Assigned",
            tr.customer.name if tr.customer else "",
            f"{tr.amount}",
            tr.status,
            tr.branch_head.name if tr.branch_head else "",
            tr.created_at.strftime('%Y-%m-%d'),
        ]

        x = x_start
        for i, item in enumerate(row):
            p.drawString(x + 2, y, str(item))
            x += col_widths[i]
        y -= 18

    # Draw borders
    y_table_end = y + (18 * len(transactions)) + 20
    x = x_start
    for width_val in col_widths:
        p.line(x, height - 90, x, y + 2)
        x += width_val
    p.line(x_start, height - 90, x_start + sum(col_widths), height - 90)
    p.line(x_start, y + 2, x_start + sum(col_widths), y + 2)

    p.save()
    return response

def all_export_transactions_pdf(request):
    user = request.user

    if user.user == 'MID':  # Branch Head
        transactions = TransactionRequest.objects.filter(branch_head=user).order_by('-created_at')
    elif user.user == 'LOW':  # Agent
        transactions = TransactionRequest.objects.filter(agent=user).order_by('-created_at')
    else:  # Admin or higher-level user
        transactions = TransactionRequest.objects.all().order_by('-created_at')
    
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="transactions_{current_date}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Transaction Report")
    y -= 40

    # Define column titles and widths
    headers = ["Type", "Agent", "Customer", "Amount", "Status", "Branch Head", "Date"]
    col_widths = [60, 90, 90, 60, 60, 90, 70]
    x_start = 30

    # Draw header background
    p.setFillColor(colors.lightgrey)
    p.rect(x_start, y - 5, sum(col_widths), 20, fill=1)
    p.setFillColor(colors.black)

    # Draw headers
    p.setFont("Helvetica-Bold", 10)
    x = x_start
    for i, header in enumerate(headers):
        p.drawString(x + 2, y, header)
        x += col_widths[i]
    y -= 20

    # Draw rows
    p.setFont("Helvetica", 9)
    for tr in transactions:
        if y < 60:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica-Bold", 10)
            x = x_start
            for i, header in enumerate(headers):
                p.drawString(x + 2, y, header)
                x += col_widths[i]
            y -= 20
            p.setFont("Helvetica", 9)

        row = [
            tr.transaction_type,
            tr.agent.name if tr.agent else "Agent Not Assigned",
            tr.customer.name if tr.customer else "",
            f"{tr.amount}",
            tr.status,
            tr.branch_head.name if tr.branch_head else "",
            tr.created_at.strftime('%Y-%m-%d'),
        ]

        x = x_start
        for i, item in enumerate(row):
            p.drawString(x + 2, y, str(item))
            x += col_widths[i]
        y -= 18

    # Draw borders
    y_table_end = y + (18 * len(transactions)) + 20
    x = x_start
    for width_val in col_widths:
        p.line(x, height - 90, x, y + 2)
        x += width_val
    p.line(x_start, height - 90, x_start + sum(col_widths), height - 90)
    p.line(x_start, y + 2, x_start + sum(col_widths), y + 2)

    p.save()
    return response


def credit_request(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    current_user = request.user  # Logged-in user (Agent or Branch Head)

    # If the user is an agent, find their branch head
    branch_head_instance = None
    if current_user.user == 'LOW':
        try:
            branch_head_instance = AgentAssignment.objects.get(agents=current_user).branch_head
        except AgentAssignment.DoesNotExist:
            branch_head_instance = None  
    if request.method == 'POST':
        amount = request.POST.get('credit_amount')
        update_date = request.POST.get('created_at')
        if update_date:
            update_date = datetime.datetime.strptime(update_date, '%Y-%m-%d')
            update_date = update_date.replace(
                hour=datetime.datetime.now().hour,
                minute=datetime.datetime.now().minute,
                second=datetime.datetime.now().second
            )
        if amount:
            update_date = request.POST.get('created_at')
            if update_date:
                update_date = datetime.datetime.strptime(update_date, '%Y-%m-%d')
                update_date = update_date.replace(
                    hour=datetime.datetime.now().hour,
                    minute=datetime.datetime.now().minute,
                    second=datetime.datetime.now().second
                )
            transaction_request = TransactionRequest(
                transaction_type='CREDIT',
                agent=current_user if current_user.user == 'LOW' else None,  # Only set if agent
                customer=customer,
                amount=amount,
                created_at=update_date,
                branch_head=branch_head_instance if current_user.user == 'LOW' else current_user,  # Set branch head if agent, else set self
                status='APPROVED' if current_user.user == 'MID' else 'PENDING'  # Auto approve if branch head
            )
            if transaction_request.status == 'APPROVED':
                customer.credit_amount += int(amount)
                customer.save()
            transaction_request.save()
            request.session["massage"] = "Credit request added successfully!"
            return redirect('search_customer')
    
    return render(request, 'branch_manager/add-credit.html', {'customer': customer})


def debit_request(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    current_user = request.user  # Logged-in branch head

    # if current_user.user != 'MID':
    #     return HttpResponseForbidden("Only branch heads can process debit requests.")

    if request.method == 'POST':
        amount = request.POST.get('debit_amount')
        if amount:
            transaction_request = TransactionRequest(
                transaction_type='DEBIT',
                agent=None,  # No agent since branch head initiates this
                customer=customer,
                amount=amount,
                branch_head=current_user,
                status='APPROVED'  # Debit transactions are automatically approved
            )
            transaction_request.save()
            customer.credit_amount -= int(amount)
            customer.debit_amount += int(amount)
            customer.save()
            request.session["massage"] = "Debit request added successfully!"
            return redirect('customer')
    return render(request, 'branch_manager/debit-amt.html', {'customer': customer})



           
def debit_search_customer(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""
    
    if request.method == 'POST':
        account_no = request.POST["account_number"]
        customer_id = Customer.objects.filter(account_number=account_no).first()
        if customer_id == None:
            request.session["massage1"] = "Bank Account Not Found!"
            return redirect('debit_search_customer')
        if customer_id.status == "DEACTIVE":
            request.session["massage1"] = "Customer Is Not Active!"
            return redirect('debit_search_customer')
        request.session["customer_id"] = customer_id.id
        return redirect('customer_debit_search') 
    
    return render(request, 'branch_manager/debit-search-customer.html', {"msg1": msg1, "msg": msg,
    })

def customer_debit_search(request):
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""

    customer_id = ""
    if "customer_id" in request.session:
        customer_id = request.session["customer_id"]
        del request.session["customer_id"]
    else:
        request.session["massage1"] = "Please Search Again!"
        return redirect("debit_search_customer")
    # If the user is an agent, show only customers assigned to this agent 
    customers = Customer.objects.get(id=int(customer_id))
    return render(request, 'branch_manager/customer-debit-form.html', {'customer': customers, "msg":msg , "msg1": msg1})


def customer_debit_request(request, customer_id):
    current_user = request.user  # Logged-in branch head
    amount = request.POST.get("amount")   
    customer = get_object_or_404(Customer, id=customer_id)
    if amount:
        transaction_request = TransactionRequest(
            transaction_type='DEBIT',
            agent=None,  # No agent since branch head initiates this
            customer=customer,
            amount=amount,
            branch_head=current_user,
            status='APPROVED'  # Debit transactions are automatically approved
        )
        transaction_request.save()
        customer.credit_amount -= int(amount)
        customer.debit_amount += int(amount)
        customer.save()
        request.session["massage"] = "Debit request added successfully!"
        return redirect('debit_search_customer') 

def update_branch_manager(request, user_id):
    branch_user = get_object_or_404(CustomUser, id=user_id)
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, instance=branch_user)  # Pass request.user
        if form.is_valid():
            form.save()
            request.session["massage"] = 'User Updated Successfully !!'
            return redirect("branch_manager")
        else:
            request.session["massage1"] = 'Please Enter Valid Information !!'
            return redirect('update_branch_manager', user_id=branch_user.id)
    else:
        form = UserRegistrationForm(instance=branch_user)  # Pass request.user
        branch_heads = CustomUser.objects.filter(user='MID')

    return render(request, "branch_manager/update_manager.html", {"form": form, "msg":msg , "msg1": msg1, "branch_heads": branch_heads, "branch_user":branch_user})


def update_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)  # Fetch customer instance
    msg = ""
    msg1 = ''
    if "massage1" in request.session:
        msg1 = request.session["massage1"]
        del request.session["massage1"]
    elif "massage" in request.session:
        msg = request.session["massage"]
        del request.session["massage"]
    else:
        msg1 = ''
        msg = ""

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer, user=request.user)  # Pass user
        if form.is_valid():
            form.save()
            request.session["massage"] = 'Customer Updated Successfully !!'
            return redirect("customer")  # Redirect to customer list page
        else:
            request.session["massage1"] = 'Please Enter Valid Information !!'
            return redirect('update_customer', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer, user=request.user)  # Pass user to form

    return render(request, "branch_manager/update-customer.html", {"form": form,"msg":msg , "msg1": msg1, "customer_id" :customer_id})


def change_status(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)  # Fetch customer instance

    if customer.status == "ACTIVE":
        customer.status = "DEACTIVE"
        customer.save()
        request.session["massage"] = 'Customer Status Updated Successfully !!'
        return redirect("customer")
    else:
        customer.status = "ACTIVE"
        customer.save()
        request.session["massage"] = 'Customer Status Updated Successfully !!'
        return redirect("customer")


# def create_customer(request):
#     customers = Customer.objects.all()
#     if request.method == 'POST':
#         # Pass the logged-in user to the form
#         form = CustomerForm(request.POST, user=request.user)
#         if form.is_valid():
#             form.save()
#             request.session["message"] = "Customer added successfully!"
#             return redirect('customer')  # Redirect to a customer list or another page
#     else:
#         # Pass the logged-in user to the form
#         form = CustomerForm(user=request.user)

#     return render(request, 'branch_manager/create_customer.html', {'form': form, "customers": customers})


# Read (List) View
def branch_list(request):
    branches = Branch.objects.all()
    return render(request, 'branch_list.html', {'branches': branches})

# Update View
def update_branch(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            return redirect('branch_list')  # Redirect to branch list after update
    else:
        form = BranchForm(instance=branch)
    return render(request, 'branch_update.html', {'form': form, 'branch': branch})

# Delete View
def delete_branch(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    if request.method == 'POST':
        branch.delete()
        return redirect('branch_list')  # Redirect to branch list after deletion
    return render(request, 'branch_confirm_delete.html', {'branch': branch})


def delete_agent(request, user_id):
    print(f"Deleting user with ID: {user_id}")
    
    # Get all agents with user type "LOW"
    agents = CustomUser.objects.filter(user="LOW")

    # Find the agent instance where the ID matches user_id
    agent_to_delete = None
    for agent in agents:
        if agent.id == user_id:
            agent_to_delete = agent
            break
   
    if agent_to_delete:
        # Set assigned_agent to NULL for all customers assigned to this agent
        Customer.objects.filter(assigned_agent=agent_to_delete).update(assigned_agent=None)
        
        # Now delete the agent
        request.session["massage"] = "Agent Deleted Successfully"
        agent_to_delete.delete()
    else:
        pass
    
    return redirect("agent")

def delete_customer(request, customer_id):
    print(f"Deleting customer with ID: {customer_id}")  # Debugging

    # Find the customer instance
    customer_to_delete = get_object_or_404(Customer, id=customer_id)

    # Remove customer from any related AgentAssignment
    AgentAssignment.objects.filter(agents=customer_to_delete.assigned_agent).update(agents=None)

    # Now delete the customer
    customer_to_delete.delete()

    return redirect("customer")

def logoutuser(request):
    logout(request)
    return redirect('loginuser')