from qt_utils.model_loaders import get_user_model
import stripe

def clear_stripe_customers():
        User = get_user_model()
        users = User.objects.filter(customer__isnull=False)

        for user in users:
            stripe.Customer.delete(user.customer.id)
