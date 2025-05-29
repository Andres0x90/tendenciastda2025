from rest_framework.routers import DefaultRouter

from products.front.views.ProductsFrontView import ProductsFrontView
from products.views import ProductView

router = DefaultRouter()
router.register(r'products', ProductView, "products")
router.register('front/products', ProductsFrontView, basename='products_front')

urlpatterns = router.urls