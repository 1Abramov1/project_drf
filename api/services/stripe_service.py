import stripe
from django.conf import settings
from rest_framework import serializers

# Настройка API ключа
stripe.api_key = settings.STRIPE_API_KEY


def create_product(name, description=None, metadata=None):
    """
    Создает продукт в Stripe.

    Args:
        name: Название продукта
        description: Описание продукта
        metadata: Дополнительные метаданные

    Returns:
        dict: {'id': product_id, 'name': name}
    """
    try:
        product = stripe.Product.create(
            name=name,
            description=description,
            active=True,
            metadata=metadata or {}
        )
        return {
            'id': product.id,
            'name': product.name
        }
    except stripe.error.StripeError as e:
        raise serializers.ValidationError(f"Ошибка создания продукта: {e.user_message}")


def create_price(product_id, amount, currency="usd", nickname=None):
    """
    Создает цену для продукта в Stripe.

    Args:
        product_id: ID продукта в Stripe
        amount: Сумма в долларах (например 100.00)
        currency: Валюта (по умолчанию USD)
        nickname: Описание цены

    Returns:
        dict: {'id': price_id, 'product_id': product_id}
    """
    try:
        # Конвертируем доллары в центы
        unit_amount = int(amount * 100)

        price = stripe.Price.create(
            product=product_id,
            unit_amount=unit_amount,
            currency=currency.lower(),
            active=True,
            nickname=nickname
        )
        return {
            'id': price.id,
            'product_id': price.product
        }
    except stripe.error.StripeError as e:
        raise serializers.ValidationError(f"Ошибка создания цены: {e.user_message}")


def create_checkout_session(price_id, success_url, cancel_url, metadata=None):
    """
    Создает сессию Checkout для оплаты.

    Args:
        price_id: ID цены в Stripe
        success_url: URL для перенаправления после успешной оплаты
        cancel_url: URL для перенаправления при отмене
        metadata: Дополнительные метаданные

    Returns:
        dict: {'id': session_id, 'url': checkout_url}
    """
    try:
        session = stripe.checkout.Session.create(
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {},
            payment_method_types=['card'],
        )
        return {
            'id': session.id,
            'url': session.url,
            'payment_status': session.payment_status,
        }
    except stripe.error.StripeError as e:
        raise serializers.ValidationError(f"Ошибка создания сессии: {e.user_message}")
