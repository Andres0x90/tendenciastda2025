from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
import requests

class AuthFrontView(ViewSet):
    renderer_classes = [TemplateHTMLRenderer]

    def list(self, request):
        return Response(template_name='auth/front/templates/login.html')

    def create(self, request):
        response = requests.post(request.build_absolute_uri('/api/auth/login/'), {
            'username': request.data['username'],
            'password': request.data['password']
        })
        if response.status_code != 200:
            return Response({
                'errors': response.json()["message"],
            }, template_name='auth/front/templates/login.html')
        return redirect(f"/api/front/products/?token={response.json()['token']}")