from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from clients.models import Client
from clients.serializers import ClientDataSerializer
from commons.jwt_utils import JWTUtils
from commons.permissions import Permissions
import logging


# Create your views here.
class ClientView(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientDataSerializer
    forbidden_response = Response({
        "message": "You don't have permissions to perform this action.",
    }, status=status.HTTP_403_FORBIDDEN)

    header_param = openapi.Parameter('authorization', openapi.IN_HEADER, description="authorization token header param",
                                     type=openapi.IN_HEADER)

    @swagger_auto_schema(request_body=ClientDataSerializer, responses={201: ClientDataSerializer()},
                         manual_parameters=[header_param])
    def create(self, request, *args, **kwargs):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.CREATE_CLIENT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Create client service called successfully with user {token_info['user']}")
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: ClientDataSerializer()},
                         manual_parameters=[header_param])
    def retrieve(self, request, *args, **kwargs):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.VIEW_CLIENT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Retrieve client service called successfully with user {token_info['user']}")
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: ClientDataSerializer(many=True)}, manual_parameters=[header_param])
    def list(self, request, *args, **kwargs):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.VIEW_CLIENT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"List clients service called successfully with user {token_info['user']}")
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=ClientDataSerializer, responses={200: ClientDataSerializer()}, manual_parameters=[header_param])
    def update(self, request, *args, **kwargs):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.UPDATE_CLIENT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Update client service called successfully with user {token_info['user']}")
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(request_body=ClientDataSerializer, responses={200: ClientDataSerializer()}, manual_parameters=[header_param])
    def partial_update(self, request, *args, **kwargs):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.UPDATE_CLIENT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Partial update client service called successfully with user {token_info['user']}")
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[header_param])
    def destroy(self, request, *args, **kwargs):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.DELETE_CLIENT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Delete client service called successfully with user {token_info['user']}")
        return super().destroy(request, *args, **kwargs)