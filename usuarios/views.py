from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CrearUsuarioForm, RegistroUsuarioForm, EditarUsuarioForm



def manage_users(request):
    
    usuarios = User.objects.all().select_related("perfil")
    
    return render(request, "usuarios/manage_users.html", {
        "usuarios": usuarios
    })

def crear_usuario(request):
    """Creación interna por el administrador con asignación de rol"""
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            rol = form.cleaned_data['rol']

            user.set_password(password)
            user.save()

            # Asignar rol al perfil
            user.perfil.rol = rol
            user.perfil.save()

            messages.success(request, "Usuario creado correctamente.")
            return redirect('manage_users')

    else:
        form = CrearUsuarioForm()

    return render(request, "usuarios/crear_usuario.html", {'form': form})

def registrar_usuario(request):
    """Registro de usuario sin rol (asignado luego por admin)"""
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()

            messages.success(request, "Usuario creado correctamente. Un administrador asignará su rol.")
            return redirect('login')

    else:
        form = RegistroUsuarioForm()

    return render(request, "usuarios/registrar.html", {"form": form})

def toggle_user_status(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    usuario.is_active = not usuario.is_active
    usuario.save()

    estado = "activado" if usuario.is_active else "desactivado"
    messages.success(request, f"Usuario {estado} correctamente.")

    return redirect("manage_users")

def editar_usuario(request, user_id):
    usuario = User.objects.get(id=user_id)

    if request.method == "POST":
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect("manage_users")
    else:
        # precargar el rol
        initial_data = { "rol": usuario.perfil.rol }
        form = EditarUsuarioForm(instance=usuario, initial=initial_data)

    return render(request, "usuarios/editar_usuario.html", {
        "form": form,
        "usuario": usuario
    })