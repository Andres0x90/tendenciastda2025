from django.shortcuts import redirect
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
import requests

class ProductsFrontView(ViewSet):
    renderer_classes = [TemplateHTMLRenderer]

    def list(self, request):
        response = requests.get(request.build_absolute_uri('/api/products/'), headers={'authorization': request.GET.get('token')})
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return Response({'products': response.json(), 'token': request.GET.get('token')} ,template_name='products/front/templates/products.html')

    @action(detail=False, methods=['GET'], url_path='update')
    def update_view(self, request):
        response = requests.get(request.build_absolute_uri(f'/api/products/{request.GET.get('id')}'), headers={'authorization': request.GET.get('token')})
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return Response({'product': response.json(), 'token': request.GET.get('token')} ,template_name='products/front/templates/update.html')

    @action(detail=False, methods=['POST'], url_path='update-product')
    def update_product(self, request):
        response = requests.put(request.build_absolute_uri(f'/api/products/{request.GET.get('id')}/'),
                                headers={'authorization': request.GET.get('token')},
                                data=request.data)
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return redirect(f'/api/front/products/?token={request.GET.get("token")}')

    def create(self, request):
        response = requests.post(request.build_absolute_uri(f'/api/products/'),
                                headers={'authorization': request.GET.get('token')},
                                data=request.data)
        if response.status_code != 201:
            return Response(template_name='auth/front/templates/forbidden.html')
        return redirect(f'/api/front/products/?token={request.GET.get("token")}')

    @action(detail=False, methods=['GET'], url_path='delete')
    def delete_view(self, request):
        response = requests.delete(request.build_absolute_uri(f'/api/products/{request.GET.get('id')}/'),
                                headers={'authorization': request.GET.get('token')})
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return redirect(f'/api/front/products/?token={request.GET.get("token")}')