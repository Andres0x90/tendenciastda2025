from django.db.models import QuerySet

from products.models import Product
from products.serializers import ProductDataSerializer
import logging

class ProductService:
    def create_product(self, product: Product) -> Product:
        data_serializer = ProductDataSerializer(data=product.to_dict())
        if data_serializer.is_valid(raise_exception=True):
            data_serializer.save()
            data_saved = data_serializer.data
            return data_serializer.map_to_entity(data_saved)

        logging.error(f"There was an error when saving product with data {product.to_dict()}")
        raise Exception("Ocurrio un error al guardar el producto")

    def get_product_by_id(self, product_id: int) -> Product:
        return Product.objects.get(id=product_id)

    def get_all_products(self) -> QuerySet:
        return Product.objects.all()

    def get_product_to_update(self, old_product: Product, product_to_update: Product) -> Product:
        old_product.name = product_to_update.name
        old_product.price = product_to_update.price
        old_product.quantity = product_to_update.quantity
        old_product.category = product_to_update.category
        old_product.subcategory = product_to_update.subcategory
        return old_product

    def update_product(self, product: Product) -> Product | None:
        old_product: Product = self.get_product_by_id(product.id)
        updated_product = self.get_product_to_update(old_product, product)
        data_serializer = ProductDataSerializer(data=updated_product.to_dict())

        if data_serializer.is_valid(raise_exception=True):
            Product.objects.bulk_update(objs=[updated_product], fields=['name', 'price', 'quantity', 'category', 'subcategory'])
            return updated_product

    def delete_product(self, product_id: int) -> None:
        product = self.get_product_by_id(product_id)
        product.delete()