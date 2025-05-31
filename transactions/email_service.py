from django.core.mail import EmailMessage

from sales_system.settings import EMAIL_HOST_USER
from transactions.models import Transaction
import logging

class EmailService:
    @staticmethod
    def send(email, transaction: Transaction):
        transaction_dict = transaction.to_dict()
        message = (f"Señor usuario confirmamos que su transaccion fue realzada exitosamente con la siguiente informacion: <br><br>"
                   f"<b>ID de Transaccion:</b> {transaction_dict['id']} <br>"
                   f"<b>Cedula cliente: </b> {transaction_dict['client']} <br>"
                   f"<b>============== Productos ===========  </b> <br>")
        for product_dict in transaction_dict['products']:
            message += (f"<b>Producto:</b> {product_dict['product']} <br>"
                        f"<b>Cantidad: </b> {product_dict['quantity']} <br>"
                        f"<b>Total producto: </b> {product_dict['total']} <br>")

        message += (f"<b>======================================</b> <br>"
                    f"<b>Metodo de pago: </b> {transaction_dict['payment_method']} <br>"
                    f"<b>Estado de la transaccion: </b> {transaction_dict['status']} <br>"
                    f"<b>Total: </b> {transaction_dict['total']} <br>")


        email = EmailMessage(
            subject=f"Confirmacion de transaccion {transaction.id}",
            body=message,
            from_email=EMAIL_HOST_USER,
            to=[email],
        )
        email.content_subtype = "html"
        try:
            email.send()
        except Exception as e:
            logging.error(f"There was an error sending the email due to {e}")