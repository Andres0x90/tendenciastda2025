import statistics
from decimal import Decimal
from uuid import UUID

from django.db import connection
from django.db.models import QuerySet, Sum
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

from clients.models import Client
from products.models import Product
from transactions.email_service import EmailService
from transactions.models import Transaction, ProductPerTransaction, Report
from transactions.serializers import TransactionDataSerializer
import io
from reportlab.pdfgen import canvas


class TransactionService:
    def __init__(self):
        self.cursor = connection.cursor()
    def create_transaction(self, transaction: Transaction, products_per_transaction: list[ProductPerTransaction]) -> Transaction:
        transaction.status = 'PAGADO'
        for product_per_transaction in products_per_transaction:
            product_per_transaction.transaction = transaction

            if product_per_transaction.quantity > product_per_transaction.product.quantity:
                raise Exception(f"El producto {product_per_transaction.product.name} no cuenta con suficiento stock para realizar esta transaccion")

            product_per_transaction.total = product_per_transaction.product.price * product_per_transaction.quantity
            transaction.total += product_per_transaction.total

        data_serializer = TransactionDataSerializer(data=transaction.to_dict())
        if data_serializer.is_valid(raise_exception=True):
            data_serializer.save()
            data_saved = data_serializer.data
            for product_per_transaction in products_per_transaction:
                product_per_transaction.save()
                stock = product_per_transaction.product.quantity - product_per_transaction.quantity
                product_per_transaction.product.quantity = stock
                Product.objects.bulk_update([product_per_transaction.product], fields=['quantity'])
            EmailService.send(transaction.client.email, transaction)
            return data_serializer.map_to_entity(data_saved)

        raise Exception("Ocurrio un error al efectuar la transaccion")

    def get_transactions_by_id(self, transaction_id: UUID) -> Transaction:
        return Transaction.objects.get(id=transaction_id)

    def get_all_transactions(self) -> QuerySet:
        return Transaction.objects.all()

    def get_transaction_to_update(self, old_transaction: Transaction, transaction_to_update: Transaction) -> Transaction:
        old_transaction.status = transaction_to_update.status
        return old_transaction

    def update_transaction(self, transaction: Transaction) -> Transaction | None:
        old_transaction: Transaction = self.get_transactions_by_id(transaction.id)
        updated_transaction = self.get_transaction_to_update(old_transaction, transaction)
        Transaction.objects.bulk_update(objs=[updated_transaction], fields=['status'])
        return updated_transaction

    def delete_transaction(self, transaction_id: UUID) -> None:
        transaction = self.get_transactions_by_id(transaction_id)
        transaction.delete()

    def generate_sales_report(self) -> Report:
        return Report(
            total_clients=self.get_total_clients(),
            total_products=self.get_total_products(),
            num_sales=self.get_num_sales(),
            total_sales=self.get_total_sales(),
            best_selling_product=self.get_best_selling_product(),
            selling_by_products=self.get_selling_by_products()
        )

    def generate_sales_report_pdf(self):
        report = self.generate_sales_report()
        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        page.setFont('Helvetica-Bold', 15)
        page.drawString(100, 800, report.title)
        page.setFont('Times-Roman', 13)
        page.drawString(100, 760, f"Fecha de creacion: {report.created_date}")
        page.drawString(100, 730, f"Clientes: {report.total_clients}")
        page.drawString(100, 700, f"Productos: {report.total_products}")
        page.drawString(100, 670, f"Numero de ventas: {report.num_sales}")
        page.drawString(100, 640, f"Ventas totales: {report.total_sales}")
        page.drawString(100, 610, f"Producto mas vendido: {report.best_selling_product}")
        page.setFont('Helvetica-Bold', 15)
        page.drawString(100, 570, "Ventas por productos")
        data = [["Producto", "Venta total"]]
        tabla_style = TableStyle([
            ('BACKGROUND', (1, 1), (-2, -2), colors.green),
            ('TEXTCOLOR', (0, 0), (1, -1), colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.gray),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.gray),
        ])

        for key, value in report.selling_by_products.items():
            data.append([key, value])

        table = Table(data)
        table.setStyle(tabla_style)
        table.wrapOn(page, 400, 600)
        table.drawOn(page, 100, 490)

        draw = Drawing(400, 250)
        bar = VerticalBarChart()
        data.pop(0)
        bar.categoryAxis.categoryNames  = [row[0] for row in data]
        bar.data = [[float(row[1]) for row in data]]
        bar.bars[0].fillColor = colors.darkblue
        bar.width = 400
        bar.height = 250
        bar.valueAxis.valueMin = 0
        bar.valueAxis.valueStep = 50000
        title = Label()
        title.setOrigin(100, 310)
        title.setText("Ventas Por Productos")
        title.fontSize = 14

        draw.add(bar)
        draw.add(title)
        draw.save()
        draw.drawOn(page, 100, 140)

        page.showPage()
        page.save()
        buffer.seek(0)
        return buffer

    def get_total_clients(self) -> int:
        return Client.objects.count()

    def get_total_products(self) -> int:
        return Product.objects.count()

    def get_num_sales(self) -> int:
        return Transaction.objects.filter(status='PAGADO').count()

    def get_total_sales(self) -> Decimal:
        return Transaction.objects.filter(status='PAGADO').aggregate(Sum('total'))['total__sum']

    def get_best_selling_product(self) -> str:
        self.cursor.execute("select products.name, sum(total) as total_by_product from transactions_productpertransaction "
                            "inner join products on transactions_productpertransaction.product_id = products.id "
                            "group by product_id ORDER BY total_by_product DESC")

        product_name, total = self.cursor.fetchone()
        return product_name

    def get_selling_by_products(self) -> dict[str, Decimal]:
        self.cursor.execute("select products.name, sum(total) as total_by_product from transactions_productpertransaction "
                            "inner join products on transactions_productpertransaction.product_id = products.id "
                            "group by product_id")
        selling_by_product: dict[str, Decimal] = {}

        for product_name, total in self.cursor.fetchall():
            selling_by_product[product_name] = Decimal(total)

        return selling_by_product