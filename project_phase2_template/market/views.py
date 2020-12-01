from django.http import HttpResponse , JsonResponse
from .models import Product
import json



########################################################################################################################

def product_insert(request):

    if request.method != 'POST':  # request must be POST
        response_data = {'message': 'request method should be POST'}
        return JsonResponse(response_data, status=400)

    try:
       
        json_data = json.loads(request.body)  # get new product variables from request body
        code = json_data['code']
        name = json_data['name']
        price = json_data['price']
        inventory = 0

        try:  # inventory is optional
            assert json_data['inventory']
            inventory = json_data['inventory']

        except KeyError:  # if inventory is not set
            inventory = 0

        

        Product.objects.create(code=code, name=name, price=price, inventory=inventory).save()  # creat new product
        response_data = {"id": Product.objects.get(code=code).id}# represent product id
       
        return JsonResponse(response_data, status=201)  # if every thing is ok

    except:

        response_data = {"message": "Duplicate code or bad type variable"}  # any problem in insert new product

        return JsonResponse(response_data, status=400)  # if a problem occur


########################################################################################################################


def product_list(request):
    if request.method != 'GET':
        response_data = {"message": "request method should be GET"}
        return JsonResponse(response_data, status=400)

    search_object = request.GET.get('search', '')
    if search_object == '':
        products = Product.objects.all()
        data = {"products": list(products.values("id", "code", "name", "price", "inventory"))}

        return JsonResponse(data, status=200)

    products = Product.objects.filter(name__contains=search_object)
    data = {"products": list(products.values("id", "code", "name", "price", "inventory"))}

    return JsonResponse(data, status=200)


########################################################################################################################


def product_show_by_id(request, product_id):
    if request.method != 'GET':
        response_data = {"message": "request method should be GET"}
        return JsonResponse(response_data, status=400)

    if Product.objects.filter(id=product_id).count() != 0:
        instance = Product.objects.get(id=product_id)
        data = {
            "id": instance.id,
            "code": instance.code,
            "name": instance.name,
            "price": instance.price,
            "inventory": instance.inventory
        }
        return JsonResponse(data, status=200)

    else:
        response_data = {"message": "Product Not Found."}
        return JsonResponse(response_data, status=404)


########################################################################################################################

def product_edit_inventory_id(request, product_id):
    if request.method != 'POST':
        return JsonResponse({"message": "request method should be POST"}, status=400)

    json_data = json.loads(request.body)
    amount = json_data['amount']

    if Product.objects.filter(id=product_id).count() != 0:

        instance = Product.objects.get(id=product_id)

        try:

            if amount > 0:

                instance.increase_inventory(amount)

            elif amount < 0:

                assert amount < instance.inventory
                instance.decrease_inventory(-1 * amount)
            data = {
                "id": instance.id,
                "code": instance.code,
                "name": instance.name,
                "price": instance.price,
                "inventory": instance.inventory
            }

            return JsonResponse(data, status=200)

        except:
            return JsonResponse({"message": "Not enough inventory"}, status=400)

    else:
        return JsonResponse({"message": "Product Not Found."}, status=404)

########################################################################################################################
