import operator
from app.services.orders.data_class import PromotionTarget, OrderItem,OrderContext

from decimal import Decimal

from app.enums.discount_enums import RewardType


def evaluate_rule(rule, order) -> bool:
    OPERATORS = {
    "eq": operator.eq,
    "ne": operator.ne,
    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,
    }
    if rule.rule_type == "minimum_order_amount":
        return OPERATORS[rule.operator](
            order.subtotal,
            rule.value,
        )

    elif rule.rule_type == "minimum_quantity":
        return OPERATORS[rule.operator](
            order.total_quantity,
            rule.value,
        )

    elif rule.rule_type == "customer_group":
        return OPERATORS[rule.operator](
            order.customer_group,
            rule.value,
        )

    elif rule.rule_type == "payment_method":
        return OPERATORS[rule.operator](
            order.payment_method,
            rule.value,
        )

    elif rule.rule_type == "shipping_zone":
        return OPERATORS[rule.operator](
            order.shipping_zone,
            rule.value,
        )

    elif rule.rule_type == "first_order":
        return order.is_first_order == rule.value

    return False

def promotion_matches(promotion, order):

    for rule in promotion.rules:

        if not evaluate_rule(rule, order):
            return False
    return True



# =================================================
#               Targets
# =================================================

class TargetEvaluation:
    def get_matching_items(
        self,
    order: OrderContext,
    targets: list[PromotionTarget],
) -> list[OrderItem]:

        matched_items = []

        for item in order.items:

            if self._is_item_matched(item, targets):

                matched_items.append(item)

        return matched_items
    
    def _is_item_matched(
            self,
        item: OrderItem,
        targets: list[PromotionTarget],
    ) -> bool:

        include = False

        for target in targets:

            matched = False

            if target.target_type == "product":
                matched = item.product_id == target.target_id

            elif target.target_type == "variant":
                matched = item.variant_id == target.target_id

            elif target.target_type == "category":
                matched = item.category_id == target.target_id

            elif target.target_type == "brand":
                matched = item.brand_id == target.target_id

            elif target.target_type == "order":
                matched = True

            if matched:

                if target.excluded:
                    return False

                include = True

        return include
    

class PromotionActionValidator:

    def execute(
        self,
        order_context,
        matched_result,
        actions,
    ):
        """
        Execute all promotion actions.

        Parameters
        ----------
        order_context : OrderContext
        matched_result : TargetMatchResult
        actions : list[PromotionAction]

        Returns
        -------
        dict
        """

        result = {
            "discount": Decimal("0"),
            "shipping_discount": Decimal("0"),
            "gift_products": [],
            "loyalty_points": 0,
            "cashback": Decimal("0"),
            "affected_items": [],
        }

        for action in actions:

            reward_type = action.reward_type

            if reward_type == RewardType.PERCENTAGE_DISCOUNT:
                self._percentage_discount(
                    matched_result,
                    action.action_config,
                    result,
                )

            elif reward_type == RewardType.FIXED_AMOUNT_DISCOUNT:
                self._fixed_amount_discount(
                    matched_result,
                    action.action_config,
                    result,
                )

            elif reward_type == RewardType.FIXED_PRICE:
                self._fixed_price(
                    matched_result,
                    action.action_config,
                    result,
                )

            elif reward_type == RewardType.BUY_X_GET_Y:
                self._buy_x_get_y(
                    matched_result,
                    action.action_config,
                    result,
                )

            elif reward_type == RewardType.BUNDLE_PRICE:
                self._bundle_price(
                    matched_result,
                    action.action_config,
                    result,
                )

            elif reward_type == RewardType.FREE_SHIPPING:
                self._free_shipping(
                    order_context,
                    action.action_config,
                    result,
                )

            elif reward_type == RewardType.GIFT_PRODUCT:
                self._gift_product(
                    action.action_config,
                    result,
                )

            elif reward_type == RewardType.LOYALTY_POINTS:
                self._loyalty_points(
                    action.action_config,
                    result,
                )

            else:
                raise ValueError(f"Unsupported reward type: {reward_type}")

        return result

    def _percentage_discount(
        self,
        matched_result,
        config,
        result,
    ):
        subtotal = sum(
            item.subtotal
            for item in matched_result.discount_items
        )

        discount = (
            subtotal *
            Decimal(config["discount"])
            / Decimal("100")
        )

        if config.get("maximum_discount"):
            discount = min(
                discount,
                Decimal(config["maximum_discount"]),
            )

        result["discount"] += discount
        result["affected_items"].extend(
            matched_result.discount_items
        )

    def _fixed_amount_discount(
        self,
        matched_result,
        config,
        result,
    ):
        result["discount"] += Decimal(config["discount"])
        result["affected_items"].extend(
            matched_result.discount_items
        )

    def _fixed_price(
        self,
        matched_result,
        config,
        result,
    ):
        # TODO:
        # Calculate the difference between the current total
        # and the configured fixed price.
        pass

    def _buy_x_get_y(
        self,
        matched_result,
        config,
        result,
    ):
        # TODO:
        # Use qualifier_items and reward_items to determine
        # how many reward items are free or discounted.
        pass

    def _bundle_price(
        self,
        matched_result,
        config,
        result,
    ):
        # TODO:
        # Calculate bundle savings based on bundle_price.
        pass

    def _free_shipping(
        self,
        order_context,
        config,
        result,
    ):
        result["shipping_discount"] = order_context.shipping_fee

    def _gift_product(
        self,
        config,
        result,
    ):
        result["gift_products"].append(
            {
                "product_id": config["gift_product_id"],
                "quantity": config.get("quantity", 1),
            }
        )

    def _loyalty_points(
        self,
        config,
        result,
    ):
        result["loyalty_points"] += config["points"]
    
    



