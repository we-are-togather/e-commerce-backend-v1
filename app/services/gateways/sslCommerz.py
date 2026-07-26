# gateways/sslcommerz.py

import httpx

from app.core.config import settings


class SSLCommerzGateway:

    @property
    def url(self):

        if settings.SSLCOMMERZ_SANDBOX:
            return settings.SSLCOMMERZ_SANDBOX_URL

        return settings.SSLCOMMERZ_LIVE_URL


    async def create_session(self, payment, customer):

        payload = {

            "store_id": settings.SSLCOMMERZ_STORE_ID,
            "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,

            "total_amount": float(payment.amount),

            "currency": "BDT",

            "tran_id": payment.reference,

            "success_url": f"{settings.BASE_URL}/payments/sslcommerz/success",

            "fail_url": f"{settings.BASE_URL}/payments/sslcommerz/fail",

            "cancel_url": f"{settings.BASE_URL}/payments/sslcommerz/cancel",

            "ipn_url": f"{settings.BASE_URL}/payments/sslcommerz/ipn",

            "cus_name": customer.name,

            "cus_email": customer.email,

            "cus_phone": customer.phone,

            "shipping_method": "Courier",

            "product_name": "Order",

            "product_category": "General",

            "product_profile": "general"

        }

        async with httpx.AsyncClient(timeout=30) as client:

            response = await client.post(
                self.url,
                data=payload
            )

        response.raise_for_status()

        return response.json()