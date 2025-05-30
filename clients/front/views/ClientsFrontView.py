from django.shortcuts import redirect
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
import requests

class ClientsFrontView(ViewSet):
    renderer_classes = [TemplateHTMLRenderer]

    def list(self, request):
        response = requests.get(request.build_absolute_uri('/api/clients/'), headers={'authorization': request.GET.get('token')})
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return Response({'clients': response.json(), 'token': request.GET.get('token')} ,template_name='clients/front/templates/clients.html')

    @action(detail=False, methods=['GET'], url_path='update')
    def update_view(self, request):
        response = requests.get(request.build_absolute_uri(f'/api/clients/{request.GET.get('id')}'), headers={'authorization': request.GET.get('token')})
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return Response({'client': response.json(), 'token': request.GET.get('token')} ,template_name='clients/front/templates/update.html')

    @action(detail=False, methods=['POST'], url_path='update-client')
    def update_client(self, request):
        response = requests.put(request.build_absolute_uri(f'/api/clients/{request.GET.get('id')}/'),
                                headers={'authorization': request.GET.get('token')},
                                data={'document': request.GET.get('id'), **request.data})
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return redirect(f'/api/front/clients/?token={request.GET.get("token")}')

    def create(self, request):
        response = requests.post(request.build_absolute_uri(f'/api/clients/'),
                                headers={'authorization': request.GET.get('token')},
                                data=request.data)
        if response.status_code != 201:
            return Response(template_name='auth/front/templates/forbidden.html')
        return redirect(f'/api/front/clients/?token={request.GET.get("token")}')

    @action(detail=False, methods=['GET'], url_path='delete')
    def delete_view(self, request):
        response = requests.delete(request.build_absolute_uri(f'/api/clients/{request.GET.get('id')}/'),
                                headers={'authorization': request.GET.get('token')})
        if response.status_code != 204:
            return Response(template_name='auth/front/templates/forbidden.html')
        return redirect(f'/api/front/clients/?token={request.GET.get("token")}')