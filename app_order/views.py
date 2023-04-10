from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView, FormMixin

from app_cart.services import CartServices
from app_users.views import MyRegistration
from .forms import OrderStepTwoForm, OrderStepThreeForm, OrderStepFourForm, OrderStepOneForm
from .models import Order
from app_cart.models import Cart, ProductInCart
from .services import OrderService

user = get_user_model()


class OrderStepOneView(MyRegistration):
    template_name = 'app_order/order_step_1.jinja2'
    success_url = reverse_lazy('order:order_step_2')

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(
                self, request.method.lower(), self.http_method_not_allowed
            )
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('order:order_step_2'))
        return super().post(request, *args, **kwargs)


class OrderStepTwoView(FormView):
    form_class = OrderStepTwoForm
    template_name = 'app_order/order_step_2.jinja2'

    def form_valid(self, form):
        self.request.session['delivery'] = form.cleaned_data['delivery_type']
        self.request.session['city'] = form.cleaned_data['city']
        self.request.session['address'] = form.cleaned_data['address']
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.request.session.get('delivery'):
            initial['delivery_type'] = self.request.session.get('delivery')
        if self.request.session.get('city'):
            initial['city'] = self.request.session.get('city')
        if self.request.session.get('address'):
            initial['address'] = self.request.session.get('address')
        return initial

    def get_success_url(self):
        return reverse('order:order_step_3')


class OrderStepThreeView(FormView):
    form_class = OrderStepThreeForm
    template_name = 'app_order/order_step_3.jinja2'

    def form_valid(self, form):
        self.request.session['payment'] = form.cleaned_data['payment_type']
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.request.session.get('payment'):
            initial['payment_type'] = self.request.session.get('payment')
        return initial

    def get_success_url(self):
        return reverse('order:order_step_4')


class OrderStepFourView(ListView):
    model = ProductInCart
    paginate_by = 5
    template_name = 'app_order/order_step_4.jinja2'
    context_object_name = 'products'

    def get_queryset(self):
        cart = CartServices(self.request).cart
        queryset = ProductInCart.objects.filter(cart=cart)
        return queryset

    def post(self, request, *args, **kwargs):
        cart = CartServices(request).cart
        Order.objects.create(
            cart=cart,
            delivery_type=request.session['delivery'],
            city=request.session['city'],
            address=request.session['address'],
            payment_type=request.session['payment'],
            total_price=request.session['total_price']
        )
        if request.session['payment'] == 'card':
            return HttpResponseRedirect(reverse('payment:payment_with_card'))
        elif request.session['payment'] == 'random':
            return HttpResponseRedirect(reverse('payment:payment_someones'))
        messages.success(request, 'Не можем перейти к оплате. Пожалйста проверьте детали заказа.')
        return redirect(request.META.get('HTTP_REFERER'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_service = OrderService(self.request)
        context['delivery'], context['payment'] = order_service.get_info_about_delivery_and_payment()
        context['user_phone'] = order_service.get_format_phone_number()
        context['total_price'] = order_service.get_total_price()
        self.request.session['total_price'] = float(context['total_price'])
        return context


class OrderListView(ListView):
    model = Order
    template_name = 'app_order/history.jinja2'
    context_object_name = 'orders'

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        context['carts'] = Cart.objects.all()
        return context


class OrderDetailView(DetailView):
    model = Order
    template_name = 'app_order/detail_order.jinja2'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = ProductInCart.objects.all()
        return context
