from djstripe import webhooks


@webhooks.handler("payment_intent.succeeded")
def my_handler(event, **kwargs):
    print("Received something")