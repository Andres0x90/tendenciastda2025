from typing import Any

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from commons.jwt_utils import JWTUtils
from commons.permissions import Permissions
from products.models import Product
from products.serializers import ProductRequestSerializer, ProductDataSerializer
from products.services import ProductService
import logging


class ProductView(ViewSet):
    def __init__(self, **kwargs: Any):
        self.product_service = ProductService()
        self.forbidden_response = Response({
        "message": "You don't have permissions to perform this action.",
    }, status=status.HTTP_403_FORBIDDEN)
        super().__init__(**kwargs)

    header_param = openapi.Parameter('authorization', openapi.IN_HEADER, description="authorization token header param",
                                     type=openapi.IN_HEADER)

    @action(detail=False, methods=['get'], url_path="healthcheck")
    def healthcheck(self, request):
        return Response("Hello world" ,status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProductRequestSerializer, responses={201: ProductDataSerializer()},
                         manual_parameters=[header_param])
    def create(self, request):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.CREATE_PRODUCT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Calling create product service with user {token_info['user']}")
        product_request_serializer: ProductRequestSerializer = ProductRequestSerializer(data=request.data)
        if product_request_serializer.is_valid(raise_exception=True):
            product: Product = product_request_serializer.create(product_request_serializer.data)
            product_saved: Product = self.product_service.create_product(product)
            product_serializer: ProductDataSerializer = ProductDataSerializer(product_saved)
            logging.info(f"Create product service called successfully with user {token_info['user']}")
            return Response(product_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={200: ProductDataSerializer(),
                                    404: "{'error': 'Product not found'}"},
                         manual_parameters=[header_param])
    def retrieve(self, request, pk=None):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.VIEW_PRODUCT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Calling retrieve product service with user {token_info['user']}")

        try:
            logging.info(f"Retrieve product service called successfully with user {token_info['user']}")
            return Response(self.product_service.get_product_by_id(pk).to_dict(), status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            logging.error(f"There was an error retrieving product service with user {token_info['user']}")
            return Response({
                "error": "Product not found",
            },status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: ProductDataSerializer(many=True)}, manual_parameters=[header_param])
    def list(self, request):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.VIEW_PRODUCT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Calling list products service with user {token_info['user']}")

        products = self.product_service.get_all_products()
        response = []
        for product in products:
            response.append(product.to_dict())

        logging.info(f"List products service called successfully with user {token_info['user']}")
        return Response(response, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProductRequestSerializer, responses={200: ProductDataSerializer()}, manual_parameters=[header_param])
    def update(self, request, pk=None):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.UPDATE_PRODUCT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Calling update product service with user {token_info['user']}")

        product_request_serializer: ProductRequestSerializer = ProductRequestSerializer(data=request.data)
        if product_request_serializer.is_valid(raise_exception=True):
            product: Product = product_request_serializer.create(product_request_serializer.data)
            product.id = pk
            product_saved: Product = self.product_service.update_product(product)
            logging.info(f"Update product service called successfully with user {token_info['user']}")
            return Response(product_saved.to_dict(), status=status.HTTP_200_OK)

        logging.error(f"There was an error calling update product service with user {token_info['user']}")

    @swagger_auto_schema(responses={200: "'message': 'This product has been deleted successfully'",
                                    404: "{'error': 'Product not found'}"}, manual_parameters=[header_param])
    def destroy(self, request, pk=None):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.DELETE_PRODUCT not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Calling delete product service with user {token_info['user']}")

        try:
            self.product_service.delete_product(pk)
            logging.info(f"Delete product service called successfully with user {token_info['user']}")
            return Response({
                "message": "This product has been deleted successfully",
            },status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            logging.error(f"There was an error retrieving product in delete product service with user {token_info['user']}")
            return Response({
                "error": "Product not found",
            },status=status.HTTP_404_NOT_FOUND)

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']