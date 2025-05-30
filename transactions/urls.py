from rest_framework import routers

from transactions import views
from transactions.front.views.TransactionsFrontView import TransactionsFrontView

router = routers.DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transactions')
router.register('front/transactions', TransactionsFrontView, basename='transactions_front')

urlpatterns = router.urls