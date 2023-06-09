from contextlib import suppress

from bootstrap_modal_forms.generic import BSModalLoginView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import UpdateView

from app_order.services import OrderService
from .forms import UserCreateForm, UserLoginForm, MyUserChangeForm, MyPasswordResetForm, MySetPasswordForm

User = get_user_model()


class MyRegistration(CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'app_users/registration.jinja2'
    success_url = reverse_lazy('product:home')

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('profile'))
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = UserCreateForm(request.POST, request.FILES)
        self.object = None
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            with suppress(ObjectDoesNotExist):
                my_group = Group.objects.get(name='Пользователи')
                my_group.user_set.add(user)
            login(request, user)
            return HttpResponseRedirect(self.success_url)
        return self.form_invalid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    raise_exception = True
    form_class = MyUserChangeForm
    model = User
    template_name = 'app_users/profile.jinja2'

    def get_success_url(self):
        return reverse('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.info(self.request, "Профиль успешно сохранен")
        return super(ProfileView, self).form_valid(form)


class MyLoginView(LoginView):
    template_name = 'app_users/login.jinja2'
    authentication_form = UserLoginForm

    def get_success_url(self):

        if self.request.POST.get('next'):
            next_page = self.request.POST.get('next')
        else:
            next_page = reverse('product:home')
        return next_page


class ModalLoginView(BSModalLoginView):
    authentication_form = UserLoginForm
    template_name = 'app_users/login_modal.jinja2'
    extra_context = dict(success_url=reverse_lazy('create_order'))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('product:home')


class MyPasswordResetView(PasswordResetView):
    email_template_name = "app_users/password_reset_email.html"
    template_name = "app_users/password_reset_form.jinja2"
    form_class = MyPasswordResetForm



class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = "app_users/password_reset_done.jinja2"


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "app_users/password_reset_confirm.jinja2"
    form_class = MySetPasswordForm
    post_reset_login = True

    def get_success_url(self):
        return reverse_lazy('profile')


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "app_users/password_reset_complete.jinja2"


class AccountView(LoginRequiredMixin, TemplateView):
    """Личный кабинет пользователя"""
    template_name = 'app_users/account.jinja2'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_service = OrderService(self.request)
        context['last_order'] = order_service.get_last_order()
        return context


@require_GET
def validate_email(request):
    """Проверка доступности логина"""
    email = request.GET.get('email', None)
    response = {
        'is_taken': User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(response)


@require_GET
def validate_phone(request):
    """Проверка доступности телефона"""
    phoneNumber = request.GET.get('phoneNumber', None)
    response = {
        'is_taken': User.objects.filter(phoneNumber__iexact=phoneNumber).exists()
    }
    return JsonResponse(response)
