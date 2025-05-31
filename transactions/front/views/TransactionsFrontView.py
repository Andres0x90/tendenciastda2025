from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
import requests

class TransactionsFrontView(ViewSet):
    renderer_classes = [TemplateHTMLRenderer]

    def list(self, request):
        response = requests.get(request.build_absolute_uri('/api/transactions/'), headers={'authorization': request.GET.get('token')})
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return Response({'transactions': response.json(),
                         'token': request.GET.get('token'),
                         'products_number': range(1, int(request.GET.get('products_number'))+1) if request.GET.get('products_number') else None},
                        template_name='transactions/front/templates/transactions.html')

    @action(detail=False, methods=['GET'], url_path='update')
    def update_view(self, request):
        response = requests.get(request.build_absolute_uri(f"/api/transactions/{request.GET.get('id')}"), headers={'authorization': request.GET.get('token')})
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return Response({'transaction': response.json(), 'token': request.GET.get('token')} ,template_name='transactions/front/templates/update.html')

    @action(detail=False, methods=['POST'], url_path='update-transaction')
    def update_transaction(self, request):
        body = {
            'id': request.data['id'],
            "client": request.data['client'],
            "products": [],
            "payment_method": request.data['payment_method'],
            "status": request.data['status'],
        }

        response = requests.put(request.build_absolute_uri(f"/api/transactions/{request.GET.get('id')}/"),
                                headers={'authorization': request.GET.get('token'), "Content-Type": "application/json"},
                                json=body)

        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return redirect(f"/api/front/transactions/?token={request.GET.get('token')}")

    def create(self, request):
        products_per_transaction = []
        for product, quantity in zip(request.data.getlist('product'), request.data.getlist('quantity')):
            products_per_transaction.append({'product': int(product), 'quantity': int(quantity)})

        body = {
            "client": request.data['client'],
            "products": products_per_transaction,
            "payment_method": request.data['payment_method'],
            "status": request.data['status'],
        }

        response = requests.post(request.build_absolute_uri(f"/api/transactions/"),
                                headers={'authorization': request.GET.get('token'), "Content-Type": "application/json"},
                                json=body)
        if response.status_code != 201:
            return Response(template_name='auth/front/templates/forbidden.html')
        return redirect(f"/api/front/transactions/?token={request.GET.get('token')}")

    @action(detail=False, methods=['GET'], url_path='delete')
    def delete_view(self, request):
        response = requests.delete(request.build_absolute_uri(f"/api/transactions/{request.GET.get('id')}/"),
                                headers={'authorization': request.GET.get('token')})
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return redirect(f"/api/front/transactions/?token={request.GET.get('token')}")

    @action(detail=False, methods=['post'], url_path='report')
    def report(self, request):
        response = requests.get(request.build_absolute_uri(f"/api/transactions/pdf/report/"),
                                headers={'authorization': request.GET.get('token')})
        if response.status_code != 200:
            return Response(template_name='auth/front/templates/forbidden.html')
        return HttpResponse(
            response.content,
            content_type='application/pdf',
            headers={'Content-Disposition': 'attachment; filename="sales_report.pdf"'},
            status=200
        )