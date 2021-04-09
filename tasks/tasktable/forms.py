from django import forms
from django.forms.widgets import DateTimeInput
from .models import Task, Project, Status, File
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin import widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from tempus_dominus.widgets import DateTimePicker


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'password'}
    ))


class PreApprovalForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'pre_approved',
            'feedback',
            'state',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'approved',
            'feedback',
            'state',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class EditProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name',
            'members',
        ]

        widgets = {
            'members': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class EditTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'description',
            'due_date',
            'importance',
            'assignees',
            'manager',
            'references',
            'project',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'cols': 40, 'rows': 10}),
            'assignees': forms.CheckboxSelectMultiple(),
            'due_date':  DateTimePicker(),
            'references': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = [
            'name',
            'type',
            'project',
            'file',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class NewStatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = [
            'user',
            'status',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class UpdateStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'state',
            'status',
            'submissions',
        ]

        widgets = {
            'status': forms.CheckboxSelectMultiple(),
            'submissions': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class NewProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name',
            'members',
        ]

        widgets = {
            'members': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class NewTaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = [
            'name',
            'description',
            'due_date',
            'importance',
            'assignees',
            'manager',
            'references',
            'project',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'cols': 40, 'rows': 10, 'initial': 'Testing'}),
            'assignees': forms.CheckboxSelectMultiple(),
            'references': forms.CheckboxSelectMultiple(),
            'due_date': DateTimePicker(attrs={'id': 'date-field'}),
        }

        validators = {
            'description': MinLengthValidator(limit_value=10)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create'))

    def clean(self):
        data = self.cleaned_data
        a = self.cleaned_data.get('assignees')
        p = self.cleaned_data.get('project').id
        project = Project.objects.get(id=p)
        for person in a:
            if person not in project.members.all():
                raise forms.ValidationError(
                    'You have assigned this task to a person who is not in this project.')

        return data
