import datetime
from django.db.models.fields.related import create_many_to_many_intermediary_model
import timeago
from .forms import NewTaskForm, NewProjectForm, UpdateStatusForm, NewStatusForm, UploadFileForm, EditTaskForm, EditProjectForm, ApprovalForm, PreApprovalForm, UserLoginForm
import os
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from .models import Task, Project, File, Status, Notification
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.utils import timezone


def index(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        current_user = User.objects.get(id=user_id)
        if current_user.groups.filter(name='Managers').exists():
            all_tasks = Task.objects.order_by('due_date', 'importance')
            template = loader.get_template('tasks/index.html')
            context = {
                'all_tasks': all_tasks,
                'can_edit': True
            }
            return HttpResponse(template.render(context, request))
        elif current_user.groups.filter(name='Admins').exists():
            all_tasks = Task.objects.order_by('due_date', 'importance')
            template = loader.get_template('tasks/index.html')
            context = {
                'all_tasks': all_tasks,
                'can_edit': True,
            }
            return HttpResponse(template.render(context, request))
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied


def details(request, id):
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        raise Http404("This task has not yet been created")

    all_statoos = task.status.values()
    status_list = []
    project = task.project.name
    references = task.references.all()
    submissions = task.submissions.all()
    submit_names = []
    current_user = User.objects.get(id=request.user.id)
    if current_user.groups.filter(name='Admins').exists():
        is_reviewer = True
    elif current_user.groups.filter(name='Managers').exists():
        is_reviewer = True
    else:
        is_reviewer = False
    reference_names = []
    for item in submissions:
        submit_names.append(item.name)
    for item in references:
        reference_names.append(item.name)
    all_assignees = task.assignees.values('username')
    assignee_list = []
    assignees = task.assignees.all()
    if current_user in assignees:
        mytask = True
    else:
        mytask = False
    for item in all_assignees.values('first_name', 'last_name'):
        assignee_list.append(item['first_name'] + ' ' + item['last_name'])
    for item in all_statoos.all():
        status_user = User.objects.get(id=item['user_id'])
        user_name = str(status_user.first_name) + \
            ' ' + str(status_user.last_name)
        status_list.append(str(user_name) + ': ' + item['status'])
    assignees = ', '.join(assignee_list)
    template = loader.get_template('tasks/details.html')
    context = {
        'project': project,
        'task': task,
        'assignees': assignees,
        'statoos': status_list,
        'reference_names': references,
        'mytask': mytask,
        'submit_names': submissions,
        'is_reviewer': is_reviewer,
    }
    return HttpResponse(template.render(context, request))


def mytasks(request):
    if request.user.is_authenticated:
        my_tasks = []
        user_id = request.user.id
        current_user = User.objects.get(id=user_id)
        all_tasks = Task.objects.all()
        for task in all_tasks:
            if current_user in task.assignees.all():
                my_tasks.append(task)
        template = loader.get_template('tasks/index.html')
        context = {
            'all_tasks': my_tasks,
        }
        return HttpResponse(template.render(context, request))

    else:
        raise PermissionDenied


def landing(request):
    if request.user.is_authenticated:
        response = redirect('/user/home')
    else:
        response = redirect('/user/login')
    return response


def logout_view(request):
    logout(request)
    template = loader.get_template('registration/logged_out.html')
    context = {}
    return HttpResponse(template.render(context, request))


def home(request):
    now = datetime.datetime.now(timezone.utc)
    if request.user.is_authenticated:
        ready_tasks = Task.objects.filter(
            state='Ready for Approval', approved=False)
        pre_ready_tasks = Task.objects.filter(
            state='Ready for Approval', approved=False, pre_approved=False)
        user_id = request.user.id
        current_user = User.objects.get(id=user_id)
        if current_user.groups.filter(name='Managers').exists():
            account_type = 'Manager'
            base = 'tasks/tool-base.html'
        elif current_user.groups.filter(name='Admins').exists():
            account_type = 'Admin'
            base = 'tasks/tool-base.html'
        else:
            account_type = 'Staff'
            base = 'tasks/base.html'
        if len(ready_tasks) == 1:
            task_tasks = 'task is'
        else:
            task_tasks = 'tasks are'
        if len(pre_ready_tasks) == 1:
            pre_task_tasks = 'task is'
        else:
            pre_task_tasks = 'tasks are'
        notifications = Notification.objects.all()
        my_notifications = []
        projects = Project.objects.all()
        my_projects = []
        tasks = Task.objects.all()
        my_tasks = []
        for project in projects:
            if current_user in project.members.all():
                my_projects.append(project)
        for task in tasks:
            if current_user in task.assignees.all():
                my_tasks.append(task)
        for notification in notifications:
            notification.time_ago = timeago.format(
                notification.date_time_created, now=now, locale='en_short')
            if current_user in notification.recipients.all():
                my_notifications.append(notification)
        template = loader.get_template('tasks/home.html')
        context = {
            'account_type': account_type,
            'user': current_user,
            'ready_tasks': str(len(ready_tasks)) + ' ' + str(task_tasks),
            'pre_ready_tasks': str(len(pre_ready_tasks)) + ' ' + str(pre_task_tasks),
            'my_notifications': my_notifications,
            'my_projects': my_projects,
            'my_tasks': my_tasks,
            'notification_count': len(my_notifications),
            'base': base
        }
        return HttpResponse(template.render(context, request))
    else:
        raise PermissionDenied


def projects(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        current_user = User.objects.get(id=user_id)
        all_projects = Project.objects.all()
        my_projects = []
        if current_user.groups.filter(name='Staff').exists():
            user_type = 'Staff'
        elif current_user.groups.filter(name='Admins').exists():
            user_type = 'Admin'
        elif current_user.groups.filter(name='Managers').exists():
            user_type = 'Manager'
        else:
            raise PermissionDenied
        all_tasks = Task.objects.all()
        personal_tasks = Task.objects.all()
        project_tasks = []
        template = loader.get_template('tasks/projects.html')
        for project in all_projects:
            if current_user in project.members.all():
                my_projects.append(project)
        if len(all_tasks) > 0:
            for task in all_tasks:
                if task.project in my_projects:
                    project_tasks.append(task)

        if len(personal_tasks) > 0:
            for task in personal_tasks:
                if task.project in my_projects:
                    project_tasks.append(task)
        context = {
            'projects': my_projects,
            'tasks': project_tasks,
            'user_type': user_type,
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseForbidden()


def download(request, id):
    request_file = File.objects.get(id=id)
    filepath = request_file.file.path
    with open(filepath, 'rb') as down_file:
        response = HttpResponse(down_file.read())
        response['content_type'] = 'application/force-download'
        response['Content-Disposition'] = 'attachment;filename=' + \
            os.path.basename(filepath)
        return response


def projectdetails(request, id):
    if request.user.is_authenticated:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        user_type = ''
        project = Project.objects.get(id=id)
        all_tasks = Task.objects.filter(project=project)
        working = 0
        for task in all_tasks:
            if task.approved:
                working = working + 1
        try:
            working = working / len(all_tasks)
        except ZeroDivisionError:
            working = 0
        working = working * 100
        working = round(working, 2)
        working = str(working) + '%'
        project_members = project.members.all()
        if user in project_members:
            if user.groups.filter(name='Staff').exists():
                user_type = 'Staff'
            elif user.groups.filter(name='Admins').exists():
                user_type = 'Admin'
            elif user.groups.filter(name='Managers').exists():
                user_type = 'Manager'
            else:
                raise PermissionDenied

            context = {
                'tasks': all_tasks,
                'project': project,
                'members': project_members,
                'user_type': user_type,
                'percent': working,
            }
            template = loader.get_template('tasks/projectdetails.html')
            return HttpResponse(template.render(context, request))
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied


def newtask(request):
    if request.user.is_authenticated:
        if len(Project.objects.all()) == 0:
            return HttpResponse('Please add a project first.')
        else:
            user = User.objects.get(username=request.user.username)
            if user.groups.filter(name='Staff').exists():
                user_type = 'Staff'
            elif user.groups.filter(name='Admins').exists():
                user_type = 'Admin'
            elif user.groups.filter(name='Managers').exists():
                user_type = 'Manager'
            else:
                raise PermissionDenied
            if user_type == 'Admin' or user_type == 'Manager':
                form = NewTaskForm(request.POST or None)
                fields = list(form)
                if form.is_valid():
                    form.save()
                    task_name = form.cleaned_data['name']
                    task_id = Task.objects.get(name=task_name).id
                    members = form.cleaned_data.get('assignees').all()
                    description = 'You have been added to a new task called {0}. Click to view it.'.format(
                        task_name)
                    notification = Notification(
                        title=task_name, description=description, link_url='/tasks/{0}'.format(task_id))
                    notification.save()
                    saved_notification = Notification.objects.get(
                        title=task_name)
                    saved_notification.recipients.set(members)
                    saved_notification.save()
                    recipients = []

                    for member in members:
                        recipients.append(str(member.email))
                    html_message = loader.render_to_string(
                        'email/newtaskemail.html',
                        {
                            'task': str(task_name),
                            'id': int(task_id)
                        }
                    )
                    send_mail(
                        'New Task: ' + str(task_name),
                        'You have been added to a new task called: ' +
                        str(task_name) + '. http://127.0.0.1:8000/user/home',
                        'joshuabode45@gmail.com',
                        recipients,
                        html_message=html_message
                    )
                    return HttpResponseRedirect('/tasks/{0}'.format(task_id))
                context = {
                    'form': form,
                    'fields': fields,
                }
                return render(request, "tasks/newtask.html", context)
            else:
                raise PermissionDenied
    else:
        raise PermissionDenied


def newproject(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        groups = user.groups.all()
        if user.groups.filter(name='Staff').exists():
            user_type = 'Staff'
        elif user.groups.filter(name='Admins').exists():
            user_type = 'Admin'
        elif user.groups.filter(name='Managers').exists():
            user_type = 'Manager'
        else:
            raise PermissionDenied
        if user_type == 'Admin' or user_type == 'Manager':
            form = NewProjectForm(request.POST or None)
            if form.is_valid():
                form.save()
                project_name = form.cleaned_data['name']
                project_id = Project.objects.get(name=project_name).id
                members = form.cleaned_data.get('members').all()
                description = 'You have been added to a new project called {0}. Click to view it.'.format(
                    project_name)
                notification = Notification(
                    title=project_name, description=description, link_url='/projects/{0}'.format(project_id))
                notification.save()
                saved_notification = Notification.objects.get(
                    title=project_name)
                saved_notification.recipients.set(members)
                saved_notification.save()
                recipients = []
                for member in members:
                    recipients.append(str(member.email))
                html_message = loader.render_to_string(
                    'email/newprojectemail.html',
                    {
                        'project': str(project_name),
                        'id': int(project_id),
                    }
                )
                send_mail(
                    'New Project: ' + str(project_name),
                    'You have been added to a new project called: ' +
                    str(project_name) + '. http://127.0.0.1:8000/user/home',
                    'joshuabode45@gmail.com',
                    recipients,
                    html_message=html_message
                )
                return HttpResponseRedirect('/projects/{0}'.format(project_id))
            context = {
                'form': form
            }
            return render(request, "tasks/newproject.html", context)
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied


def status(request, id):
    if request.user.is_authenticated:
        instance = Task.objects.get(id=id)
        form = UpdateStatusForm(request.POST or None, instance=instance)
        form.fields['status'].queryset = Status.objects.filter(
            user=request.user)
        reviewers = []
        for user in User.objects.all():
            if user.groups.filter(name='Admins').exists():
                reviewers.append(user.email)
            elif user.groups.filter(name='Managers').exists():
                reviewers.append(user.email)
            else:
                pass
        html_message = loader.render_to_string(
            'email/ready.html',
            {
                'task': instance
            }
        )
        if form.is_valid():
            if instance.state == 'Ready for Approval':
                send_mail(
                    str(instance) + ': Ready for Approval',
                    'The task ' + str(instance) + 'is now ready for approval.',
                    'joshuabode45@gmail.com',
                    reviewers,
                    html_message=html_message
                )
            form.save()
            return HttpResponseRedirect('/tasks/{0}'.format(id))
        context = {
            'form': form
        }
        return render(request, 'tasks/updatestatus.html', context)
    else:
        raise PermissionDenied


def newstatus(request):
    if request.user.is_authenticated:
        form = NewStatusForm(request.POST or None)
        form.fields['user'].queryset = User.objects.filter(
            id=request.user.id)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/tasks')
        context = {
            'form': form
        }
        return render(request, "tasks/newstatus.html", context)
    else:
        raise PermissionDenied


def uploadfile(request):
    if request.user.is_authenticated:
        form = UploadFileForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, "tasks/uploadfile.html", context)
    else:
        raise PermissionDenied


def edittask(request, id, *args, **kwargs):
    if request.user.is_authenticated:
        instance = Task.objects.get(id=id)
        form = EditTaskForm(request.POST or None, instance=instance)
        if request.POST.get('Delete'):
            instance.delete()
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/tasks/{0}'.format(id))
        context = {'form': form, 'title': instance.name, 'id': instance.id}
        return render(request, "tasks/edittask.html", context)
    else:
        raise PermissionDenied


def editproject(request, id, *args, **kwargs):
    if request.user.is_authenticated:
        instance = Project.objects.get(id=id)
        form = EditProjectForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/projects/{0}'.format(id))
        context = {'form': form, 'name': instance.name}
        return render(request, "tasks/editproject.html", context)

    else:
        raise PermissionDenied


def approve(request, id, *args, **kwargs):
    if request.user.is_authenticated:
        instance = Task.objects.get(id=id)
        submissions = instance.submissions.all()
        submit_names = []
        pre_approved = instance.pre_approved
        for item in submissions:
            submit_names.append(item.name)
        form = ApprovalForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/see-approve-requests')
        context = {
            'form': form,
            'title': instance.name,
            'submit_names': submit_names,
            'pre_approved': pre_approved,
        }
        return render(request, "tasks/approval.html", context)
    else:
        raise PermissionDenied


def pre_approve(request, id, *args, **kwargs):
    if request.user.is_authenticated:
        instance = Task.objects.get(id=id)
        submissions = instance.submissions.all()
        submit_names = []
        for item in submissions:
            submit_names.append(item.name)
        form = PreApprovalForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/see-approve-requests')
        context = {
            'form': form,
            'title': instance.name,
            'submit_names': submit_names,
        }
        return render(request, "tasks/pre-approval.html", context)
    else:
        raise PermissionDenied


def viewready(request):
    ready_tasks = Task.objects.filter(
        state='Ready for Approval', approved=False)
    if request.user.groups.filter(name='Managers').exists():
        user_type = 'Manager'
    if request.user.groups.filter(name='Admins').exists():
        user_type = 'Admin'
    else:
        user_type = 'Staff'
    context = {
        'all_tasks': ready_tasks,
        'user_type': user_type,
    }
    return render(request, "tasks/viewrequests.html", context)


def previewready(request):
    ready_tasks = Task.objects.filter(
        state='Ready for Approval', approved=False, pre_approved=False)
    if request.user.groups.filter(name='Managers').exists():
        user_type = 'Manager'
    if request.user.groups.filter(name='Admins').exists():
        user_type = 'Admin'
    else:
        user_type = 'Staff'
    context = {
        'all_tasks': ready_tasks,
        'user_type': user_type,
    }
    return render(request, "tasks/previewrequests.html", context)


def filespace(request, id, *args, **kwargs):
    if request.user.is_authenticated:
        project = Project.objects.get(id=id)
        project_name = project.name
        all_files = File.objects.all()
        project_files = []
        critical_files = []
        submissions = []
        references = []
        for file in all_files:
            if file.project == project:
                project_files.append(file)
        for file in project_files:
            if file.type == 'critical_files':
                critical_files.append(file)
            elif file.type == 'references':
                references.append(file)
            else:
                submissions.append(file)
        context = {
            'project_files': project_files,
            'submissions': submissions,
            'references': references,
            'critical_files': critical_files,
            'project': project_name,
        }
        return render(request, "tasks/filespace.html", context)
    else:
        pass


def forgot(request):
    return render(request, 'tasks/forgot.html', {})


def dismiss_notification(request, notification_id):
    current_user = request.user
    notification = Notification.objects.get(id=notification_id)
    notification.recipients.remove(current_user)
    return HttpResponseRedirect('/user/home')


def dismiss_all(request):
    current_user = request.user
    notifications = Notification.objects.all()
    for notification in notifications:
        notification.recipients.remove(current_user)
    return HttpResponseRedirect('/user/home')


def delete_task(request, id):
    task = Task.objects.get(id=id)
    task.delete()
    return HttpResponseRedirect('/tasks/manage')
