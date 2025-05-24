from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class AuthFrontView(ViewSet):
    renderer_classes = [TemplateHTMLRenderer]

    def list(self, request):
        return Response(template_name='auth/front/templates/login.html')

    def create(self, request):
        return Response(template_name='auth/front/templates/auth.html')