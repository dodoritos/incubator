from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from django.views.generic.detail import DetailView
from django.views.generic import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.contrib import messages
from datetime import datetime
from actstream import action
from math import ceil
from itertools import groupby

from users.decorators import permission_required
from users.mixins import PermissionRequiredMixin

from .serializers import ProjectSerializer
from .models import Project, Task
from .forms import ProjectForm


class ProjectAddView(PermissionRequiredMixin, CreateView):
    form_class = ProjectForm
    template_name = 'add_project.html'
    permission_required = 'projects.add_project'

    def get_initial(self):
        return {
            'maintainer': self.request.user,
            'progress': 0,
        }

    def form_valid(self, form):
        ret = super(ProjectAddView, self).form_valid(form)
        action.send(self.request.user, verb='a créé', action_object=self.object)

        return ret


class ProjectEditView(PermissionRequiredMixin, UpdateView):
    form_class = ProjectForm
    model = Project
    template_name = 'add_project.html'
    permission_required = 'projects.change_project'

    def form_valid(self, form):
        ret = super(ProjectEditView, self).form_valid(form)
        action.send(self.request.user, verb='a édité', action_object=self.object)

        return ret


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'


def clusters_of(seq, size):
    for i in range(int(ceil(len(seq) / size))):
        lower, upper = i * size, (i + 1) * size
        yield seq[lower:upper]


def projects_home(request):
    projects = Project.objects.prefetch_related("participants").select_related("maintainer").order_by('status', '-modified')

    # group the finised and "ants are gone" projets together
    grouper = lambda x: x.status if x.status != "a" else "f"
    groups = {k: list(g) for k, g in groupby(projects, grouper)}
    return render(request, "projects_home.html", {
        'progress': clusters_of(groups.get('i',[]), 4),
        'done': clusters_of(groups.get('f',[]), 4),
        'proposition': clusters_of(groups.get('p',[]), 4),
    })


@permission_required('projects.add_task')
def add_task(request, pk):
    if 'task_name' not in request.POST:
        return HttpResponseBadRequest("Vous n'avez pas donné de nom de tâche")
    project = get_object_or_404(Project, pk=pk)

    task_name = request.POST['task_name'].strip()

    if not task_name or not filter(str.isalpha, task_name):
        messages.add_message(request, messages.ERROR, "Le nom de la tâche est vide")
        return HttpResponseRedirect(reverse('view_project', args=[project.id]))

    task = Task.objects.create(
        project=project,
        name=task_name,
        proposed_by=request.user)

    action.send(request.user, verb='a ajouté la tâche', action_object=task, target=project)

    return HttpResponseRedirect(reverse('view_project', args=[pk]))


@permission_required('projects.change_task')
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.completed_by = request.user
    task.completed_on = datetime.now()
    task.save()

    action.send(request.user, verb='a fini la tâche', action_object=task, target=task.project)

    return HttpResponseRedirect(reverse('view_project', args=[task.project.id]))


@permission_required('projects.change_task')
def uncomplete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.completed_by = None
    task.completed_on = None
    task.save()

    action.send(request.user, verb='a ré-ajouté la tâche', action_object=task, target=task.project)

    return HttpResponseRedirect(reverse('view_project', args=[task.project.id]))


def add_participation(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.participants.add(request.user)

    action.send(request.user, verb='participe à', action_object=project)

    return HttpResponseRedirect(reverse('view_project', args=[pk]))


def remove_participation(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.participants.remove(request.user)
    return HttpResponseRedirect(reverse('view_project', args=[pk]))


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
