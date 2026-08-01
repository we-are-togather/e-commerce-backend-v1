import requests

from app.services.orders.data_class import OrderContext
from app.services.orders.discounts import TargetEvaluation
from app.services.orders.discounts import (
    evaluate_rule,
    promotion_matches,
    TargetEvaluation,
    PromotionActionValidator
)
from app.repositories.order_repositories import (
    get_promotions_by_coupon_code,
    # get_target
)


def get_discount(db,order, coupon_code):
    
    promotion_coupon = get_promotions_by_coupon_code(db, coupon_code)
    # targets = get_target(db, promotion.targets)

    if promotion_matches(promotion_coupon.promotions, order):  # promotion rule
        target_eval = TargetEvaluation()
        matches_results = target_eval.get_matching_items(order, promotion_coupon.promotions.targets)
        actions = PromotionActionValidator()
        result = actions.execute(order, matches_results)
        return result
    return None
        
def get_delivary_charge(shipping_detail):
    return 100

def get_current_currency_rate(currency):
    pass

async def get_currency_rate(from_currency: str, to_currency: str) -> float:
        """
        Get the latest exchange rate.

        Example:
            get_rate("USD", "BDT")
        """
        BASE_URL = "https://open.er-api.com/v6/latest"
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        response = await requests.get(
            f"{BASE_URL}/{from_currency}",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if data["result"] != "success":
            raise Exception("Failed to fetch exchange rates.")

        rates = data["rates"]

        if to_currency not in rates:
            raise ValueError(f"Unsupported currency: {to_currency}")

        return rates[to_currency]