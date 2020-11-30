from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError


class Product(models.Model):
    code = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    inventory = models.PositiveIntegerField(default=0)

    def increase_inventory(self, amount):
        try:
            assert amount >= 0
            self.inventory = self.inventory + amount
            self.save()
        except:
            raise ValidationError('Error at increase_inventory because of amount is not positive')

    def decrease_inventory(self, amount):
        try:
            assert self.inventory >= amount
            self.inventory = self.inventory - amount
            self.save()
        except:
            raise ValidationError('Error at decrease_inventory because of amount is bigger than inventory')

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    balance = models.PositiveIntegerField(default=20000)

    def deposit(self, amount):
        try:
            assert amount >= 0
            self.balance = self.balance + amount
            self.save()
        except:
            raise ValidationError('Error at deposit because of amount is not positive')

    def spend(self, amount):
        try:
            assert self.balance >= amount
            self.balance = self.balance - amount
            self.save()
        except:
            raise ValidationError('Error at spend because of amount is bigger than balance')


class OrderRow(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.IntegerField(default=0)
    order = models.ForeignKey('Order', related_name='rows', on_delete=models.CASCADE, null=True, blank=True)


class Order(models.Model):
    # Status values. DO NOT EDIT
    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4
    STATUS_CHOICES = [(STATUS_SHOPPING, 'در حال خرید'), (STATUS_SUBMITTED, 'ثبت‌شده'), (STATUS_CANCELED, 'لغوشده'),
                      (STATUS_SENT, 'ارسال‌شده')]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    order_time = models.DateTimeField(auto_now_add=True, blank=True)
    total_price = models.IntegerField(default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, null=True, blank=True)

    @staticmethod
    def initiate(customer):
        try:
            assert Order.objects.filter(customer=customer, status=1).count() == 0
            order1_ = Order.objects.create(customer=customer, status=1)
            order1_.save()
            return order1_
        except:
            raise ValidationError('Error at initiate because of customer has order in SHOPPING status')

    def add_product(self, product, amount):
        try:
            assert self.status == 1
            assert amount > 0
            assert product.inventory >= amount
            if self.rows.filter(product=product).count() != 0:
                a = self.rows.get(product=product)
                assert a.amount + amount <= product.inventory
                a.amount = a.amount + amount
                self.total_price += amount * product.price
                a.save()
            else:
                OrderRow.objects.create(product=product, amount=amount, order_id=self.id).save()
                self.total_price += amount * product.price
            self.save()
        except:
            raise ValidationError('Error because of status or amount is not positive or is bigger than inventory')

    def remove_product(self, product, amount=None):

        try:
            a = self.rows.get(product=product)
            assert amount >= 0
            if (a is not None) & (amount is not None) & (amount != 0) & (amount != a.amount):
                assert self.status == 1
                assert a.amount > amount
                a.amount = a.amount - amount
                self.total_price -= amount * product.price
                a.save()
            else:
                self.total_price -= a.amount*product.price
                a.delete()
            self.save()
        except:
            raise ValidationError('Error because of status or amount is not positive or is bigger than row amount')

    def submit(self):
        try:
            assert self.status == 1
            a = self.rows.all()
            assert a.count() != 0
            for o in a:
                assert o.amount <= o.product.inventory
            assert self.total_price <= self.customer.balance
            self.customer.spend(self.total_price)
            for o in a:
                o.product.decrease_inventory(o.amount)
            self.status = 2
            self.save()
        except:
            raise ValidationError('Error because of status or amount or total_price or empty order')

    def cancel(self):
        try:
            assert self.status != 4
            self.customer.deposit(self.total_price)
            self.total_price = 0
            a = self.rows.all()
            for o in a:
                o.product.increase_inventory(o.amount)
            self.status = 3
            self.save()
        except:
            raise ValidationError('Error because of status')

    def send(self):
        try:
            assert self.status == 2
            self.status = 4
            self.save()
        except:
            raise ValidationError('Error because of status')