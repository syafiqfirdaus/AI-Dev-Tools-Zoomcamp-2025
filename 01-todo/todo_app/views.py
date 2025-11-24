from django.shortcuts import render, redirect, get_object_or_404
from .models import Todo

def todo_list(request):
    todos = Todo.objects.all().order_by('due_date')
    return render(request, 'home.html', {'todos': todos})

def todo_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        if due_date == '':
            due_date = None
        
        Todo.objects.create(
            title=title,
            description=description,
            due_date=due_date
        )
        return redirect('todo_list')
    return render(request, 'home.html') # Should ideally be a separate create template or modal, but for simplicity reusing home or just redirecting if GET (though create usually needs a form). 
    # Actually, the homework implies a simple app. I'll put the create form in home.html for simplicity as per "Create, edit and delete TODOs".
    # But wait, if I use home.html for list, I might want a separate page or a modal for create/edit.
    # Let's stick to a simple separate page for create/edit if needed, or just one page.
    # The plan said "home.html" for list and forms.
    # Let's handle POST in todo_list? No, better separate views.
    # If I use home.html for everything, I need to pass context.
    
    # Let's refine:
    # todo_list: shows list and a create form.
    # todo_update: shows edit form.
    # todo_delete: deletes and redirects.
    
    # Re-reading plan: "todo_create: Create a new TODO".
    # I'll implement todo_create to handle the POST request from the home page form.

def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        todo.title = request.POST.get('title')
        todo.description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        if due_date == '':
            due_date = None
        todo.due_date = due_date
        todo.is_resolved = request.POST.get('is_resolved') == 'on'
        todo.save()
        return redirect('todo_list')
    return render(request, 'update.html', {'todo': todo}) # Need a template for update

def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.delete()
    return redirect('todo_list')

def todo_toggle_status(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.is_resolved = not todo.is_resolved
    todo.save()
    return redirect('todo_list')
