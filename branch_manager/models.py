from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)
    class Meta:
        abstract = True


class AccountManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, name, phone, user, password, **extra_fields):
        values = [email, name, phone, user]
        field_value_map = dict(zip(self.model.REQUIRED_FIELDS, values))
        for field_name, value in field_value_map.items():
            if not value:
                raise ValueError('The {} value must be set'.format(field_name))

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            phone=phone,
            user = user,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, phone, user, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, name, phone, user, password, **extra_fields)

    def create_superuser(self, email, name, phone, user, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, name, phone, user, password, **extra_fields)

    
class Branch(models.Model):
    branch_name = models.CharField(max_length=300)
    pincode = models.CharField(max_length=300)
    address = models.CharField(max_length=400)
    branch_code = models.IntegerField()

    def __str__(self):
        return f' {self.branch_name}'
    

class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_type = (
        ("TOP", "Owner"),
        ("MID", "Branch Head"),
        ("LOW", "Agent")
    )
    email = models.EmailField(unique=True, max_length=40)
    name = models.CharField(max_length=20)
    phone = models.CharField(max_length=150)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    user = models.CharField(max_length=200, choices=user_type)  # This is the field you're filtering on
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    branch_head = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'user': 'MID'})  # Adding Branch Head association

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone', 'user']

    def get_full_name(self):
        return f'{self.name} {self.email}'

class AgentAssignment(models.Model):
    agents = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,  
        null=True, blank=True,  # Add this to allow NULL values
        related_name='assigned_agents',
        limit_choices_to={'user': 'LOW'},
        verbose_name="Agent"
    )
    branch_head = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,  
        null=True, blank=True,  # Add this to allow NULL values
        limit_choices_to={'user': 'MID'},
        verbose_name="Branch Head"
    )
    area = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.agents.name}" if self.agents else "Unassigned Agent"

class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=100)
    ifsc_code = models.CharField(max_length=20)
    account_number = models.CharField(max_length=20)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    premium = models.IntegerField(default=0)
    address = models.CharField(max_length=300)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date_of_birth = models.CharField(max_length=150)
    scheme = models.CharField(max_length=150, choices=[
        ("MONTHLY", "Monthly"),
        ("HALF YEARLY", "Half Yearly"),
        ("YEARLY", "Yearly")
    ])
    sex = models.CharField(max_length=200, choices=[
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other")
    ])
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('DEACTIVE', 'Deactive'),
    ]
    nominee = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DEACTIVE')

    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,  # Ensures agent can be deleted without deleting customers
        null=True,  # This is required!
        blank=True,  # Allows field to be blank
        limit_choices_to={'user': 'LOW'},  
        related_name="assigned_customers"
    )

    def __str__(self):
        return self.name
    

class CreditRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  
        null=True, blank=True,  # Add this to allow NULL values
        limit_choices_to={'user': 'LOW'},
        related_name='credit_requests'
    )
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.SET_NULL,  
        null=True, blank=True,  # Add this to allow NULL values
        related_name='credit_requests'
    )
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    branch_head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  
        null=True, blank=True,  # Add this to allow NULL values
        limit_choices_to={'user': 'MID'},
        related_name='pending_approvals'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_time = models.DateTimeField(default=datetime.now(), null=True)

    def __str__(self):
        return f"Credit request for {self.customer.name} by {self.agent.name}" if self.customer and self.agent else "Unassigned Credit Request"


class TransactionRequest(models.Model):
    TRANSACTION_TYPES = (
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  
        null=True, blank=True,  # Allows NULL values
        limit_choices_to={'user': 'LOW'},
        related_name='transaction_requests'
    )
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.SET_NULL,  
        null=True, blank=True,  # Allows NULL values
        related_name='transaction_requests'
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    branch_head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  
        null=True, blank=True,  # Allows NULL values
        limit_choices_to={'user': 'MID'},
        related_name='pending_transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} request for {self.customer.name} by {self.agent.name}" if self.customer and self.agent else "Unassigned Transaction Request"


class Nominee(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='nominees')
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    relation = models.CharField(max_length=100)
    address = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.name} - {self.relation}"

    class Meta:
        verbose_name = "Nominee"
        verbose_name_plural = "Nominees"


class Document(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=200)
    document_number = models.CharField(max_length=100)
    image = models.ImageField(upload_to='documents/')

    def __str__(self):
        return self.document_name

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"

class TransferRecord(models.Model):
    sender = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='sent_transfers'
    )
    receiver = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='received_transfers'
    )
    branch_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user': 'MID'},
        related_name='transfers_handled'
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    remarks = models.TextField(blank=True)
    transfer_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Transfer ₹{self.amount} from {self.sender.name} to {self.receiver.name} on {self.transfer_date.date()}'
    
class Branch_manager(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


