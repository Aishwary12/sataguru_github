from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, RegexValidator
from django.contrib.auth.password_validation import validate_password
from .models import *
from django.forms import DateInput

# class UserChangeForm(forms.ModelForm):
#     password = ReadOnlyPasswordHashField()

#     class Meta:
#         model = CustomUser
#         fields = ('email', 'name', 'phone', 'date_of_birth', 'picture', 'password', 'is_active', 'is_superuser')

    
user_type = (
        ("TOP","Owner"),
        ("MID","Branch Head"),
        ("LOW","Agent"))

class UserRegistrationForm(forms.ModelForm):
    
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'user', 'phone')
        widgets = {
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
            'name': forms.TextInput(attrs={'placeholder': 'Username'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone'}),
        }

    # Dynamically add fields
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), required=False, empty_label="Select Branch")
    branch_head = forms.ModelChoiceField(queryset=CustomUser.objects.filter(user='MID'), required=False, empty_label="Select Branch Head")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show the branch field only for "Branch Head"
        self.fields['user'].choices = [choice for choice in self.fields['user'].choices if choice[0] != 'TOP']
        if 'user' in self.initial and self.initial['user'] == 'MID':
            self.fields['branch'].required = False
            self.fields['branch_head'].required = False  # Branch Head doesn't need a branch head
        elif 'user' in self.initial and self.initial['user'] == 'LOW':
            self.fields['branch'].required = False
            self.fields['branch_head'].required = True  # Agent (LOW) needs a Branch Head
        else:
            self.fields['branch'].required = False
            self.fields['branch_head'].required = False  # For other user types, neither field is required

    def save(self, commit=True):
        user = super().save(commit=False)
        # user.set_password(self.cleaned_data["password"])

        # Logic to associate a branch or branch head
        if self.cleaned_data.get('user') == 'MID':
            branch = self.cleaned_data.get('branch')
            if branch:
                # Optionally, associate the branch with the Branch Head user
                user.branch = branch
        
        if self.cleaned_data.get('user') == 'LOW':
            branch_head = self.cleaned_data.get('branch_head')
            if branch_head:
                # Optionally, associate the Branch Head with the Agent
                user.branch_head = branch_head  # Assuming you have a field to store the branch head

        if commit:
            user.save()
        return user

class AgentRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.TextInput(attrs={'placeholder': 'Password'}))

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'phone', 'password')
        widgets = {
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
            'name': forms.TextInput(attrs={'placeholder': 'Username'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone'}),
        }

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)

        # Set user type to 'LOW' for agents
        if user.user == 'LOW':  # Ensure that 'LOW' is selected
            user.user = 'LOW'  # Manually set user type to LOW

        # Hash the password
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['branch_name', 'pincode', 'address', 'branch_code']
        widgets = {
            'branch_name': forms.TextInput(attrs={'placeholder': 'Enter Branch Name', 'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'placeholder': 'Enter Pincode', 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter Address', 'class': 'form-control'}),
            'branch_code': forms.NumberInput(attrs={'placeholder': 'Enter Branch Code', 'class': 'form-control'}),
        }

class AgentAssignmentForm(forms.ModelForm):
    class Meta:
        model = AgentAssignment
        fields = ['agents', 'branch_head', "area"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit choices for 'agent' to only those with user_type='LOW'
        self.fields['agents'].queryset = CustomUser.objects.filter(user='LOW')
        # Limit choices for 'branch_head' to only those with user_type='MID'
        self.fields['branch_head'].queryset = CustomUser.objects.filter(user='MID')


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'name', 'date_of_birth', 'address', 'premium', 
            'credit_amount', 'debit_amount', 'email', 'phone', 'scheme', 'sex', 'assigned_agent'
        ]
        widgets = {
            'credit_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'debit_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'date_of_birth': DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        # Pop user from kwargs to filter agents based on the logged-in user
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            
            if self.user.is_superuser:
                self.fields['assigned_agent'].queryset = get_user_model().objects.filter(user='LOW')
            elif self.user.user == 'MID':  # Branch Head (user='MID')
                self.fields['assigned_agent'].queryset = AgentAssignment.objects.select_related(
                    'agents', 'branch_head', 'agents__branch'
                ).filter(agents__user='LOW', branch_head=self.user)
            else:
                self.fields['assigned_agent'].queryset = get_user_model().objects.none()
        

    def clean(self):
        cleaned_data = super().clean()  # Get the cleaned data from other fields

        # Get the agent assignment ID (assuming it's sent as part of the form)
        agent_assignment_id = cleaned_data.get('assigned_agent')
        if agent_assignment_id:
            # Fetch the AgentAssignment instance
            agent_assignment = AgentAssignment.objects.filter(id=agent_assignment_id.id).first()

            if agent_assignment:
                # Assign the CustomUser instance (agents) to the assigned_agent field in Customer model
                cleaned_data['assigned_agent'] = agent_assignment.agents  # agents is the CustomUser instance

        return cleaned_data

class NomineeForm(forms.ModelForm):
    class Meta:
        model = Nominee
        fields = ['name', 'phone_number', 'relation', 'address']


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_name', 'document_number', 'image']
        widgets = {
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # def clean_image(self):
    #     image = self.cleaned_data.get('image')
    #     if image:
    #         if image.size > 200 * 1024:  # 200 KB = 200 * 1024 bytes
    #             raise forms.ValidationError("Image file size must be under 200KB.")
    #     return image
