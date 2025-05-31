from django.http import FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from commons.jwt_utils import JWTUtils
from commons.permissions import Permissions
from transactions.models import Transaction
from transactions.serializers import TransactionRequestSerializer, TransactionDataSerializer
from transactions.services import TransactionService
import logging

# Create your views here.

class TransactionViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction_service = TransactionService()
        self.forbidden_response = Response({
            "message": "You don't have permissions to perform this action.",
        }, status=status.HTTP_403_FORBIDDEN)

    header_param = openapi.Parameter('authorization', openapi.IN_HEADER, description="authorization token header param",
                                     type=openapi.IN_HEADER)

    @swagger_auto_schema(request_body=TransactionRequestSerializer, responses={201: TransactionDataSerializer()},
                         manual_parameters=[header_param])
    def create(self, request):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.CREATE_TRANSACTION not in token_info['permissions']:
            return self.forbidden_response
        try:
            logging.info(f"Calling create transaction service with user {token_info['user']}")
            transaction_request_serializer: TransactionRequestSerializer = TransactionRequestSerializer(data=request.data)
            if transaction_request_serializer.is_valid(raise_exception=True):
                transaction, products_per_transaction = transaction_request_serializer.create(transaction_request_serializer.data)
                transaction_saved: Transaction = self.transaction_service.create_transaction(transaction, products_per_transaction)
                transaction_serializer: TransactionDataSerializer = TransactionDataSerializer(transaction_saved)
                logging.info(f"Create transaction service called successfully with user {token_info['user']}")
                return Response(transaction_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"There was an error calling create transaction service with user {token_info['user']} and error {e.args[0]}")
            return Response({'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(responses={200: TransactionDataSerializer(),
                                    404: "{'error': 'Transaction not found'}"},
                         manual_parameters=[header_param])
    def retrieve(self, request, pk=None):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.VIEW_TRANSACTION not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Calling retrieve transaction service with user {token_info['user']}")
        try:
            logging.info(f"Retrieve transaction service called successfully with user {token_info['user']}")
            return Response(self.transaction_service.get_transactions_by_id(pk).to_dict(), status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            logging.error(f"There was an error retrieving a transaction with user {token_info['user']}")
            return Response({
                "error": "Transaction not found",
            },status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: TransactionDataSerializer(many=True)}, manual_parameters=[header_param])
    def list(self, request):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.VIEW_TRANSACTION not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Calling list transactions service with user {token_info['user']}")
        transactions = self.transaction_service.get_all_transactions()
        response = []
        for transaction in transactions:
            response.append(transaction.to_dict())

        logging.info(f"List transactions service called successfully with user {token_info['user']}")
        return Response(response, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=TransactionRequestSerializer, responses={200: TransactionDataSerializer()},
                         manual_parameters=[header_param])
    def update(self, request, pk=None):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.UPDATE_TRANSACTION not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Calling update transaction service with user {token_info['user']}")
        transaction_request_serializer: TransactionRequestSerializer = TransactionRequestSerializer(data=request.data)
        if transaction_request_serializer.is_valid(raise_exception=True):
            transaction, _ = transaction_request_serializer.create(transaction_request_serializer.data)
            transaction.id = pk
            transaction_saved: Transaction = self.transaction_service.update_transaction(transaction)
            logging.info(f"Update transaction service called successfully with user {token_info['user']}")
            return Response(transaction_saved.to_dict(), status=status.HTTP_200_OK)

        logging.error(f"There was an error updating a transaction with user {token_info['user']}")

    @swagger_auto_schema(responses={200: "'message': 'This Transaction has been deleted successfully'",
                                    404: "{'error': 'Transaction not found'}"},
                         manual_parameters=[header_param])
    def destroy(self, request, pk=None):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.DELETE_TRANSACTION not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Calling delete transaction service with user {token_info['user']}")
        try:
            self.transaction_service.delete_transaction(pk)
            logging.info(f"Delete transaction service called successfully with user {token_info['user']}")
            return Response({
                "message": "This transaction has been deleted successfully",
            },status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            logging.error(f"There was an error retrieving a transaction in delete transaction service with user {token_info['user']}")
            return Response({
                "error": "Transaction not found",
            },status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(manual_parameters=[header_param])
    @action(detail=True, methods=['GET'], url_path='report')
    def generate_report(self, request, pk=None):
        if 'authorization' not in request.headers:
            return self.forbidden_response

        token_info = JWTUtils.decode(request.headers['authorization'])
        if Permissions.VIEW_TRANSACTION not in token_info['permissions']:
            return self.forbidden_response

        logging.info(f"Calling generate transactions report service with user {token_info['user']}")

        if pk == "json":
            logging.info(f"Generate transactions report service called successfully with json format and user {token_info['user']}")
            return Response(self.transaction_service.generate_sales_report().to_dict(), status=status.HTTP_200_OK)

        if pk == "pdf":
            logging.info(f"Generate transactions report service called successfully with pdf format and user {token_info['user']}")
            return FileResponse(self.transaction_service.generate_sales_report_pdf(),
                            as_attachment=True, filename="sales_report.pdf",
                            status=status.HTTP_200_OK)

        logging.error(f"There was an error calling generate transactions report with user {token_info['user']}")
        return Response(status=status.HTTP_404_NOT_FOUND)

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']