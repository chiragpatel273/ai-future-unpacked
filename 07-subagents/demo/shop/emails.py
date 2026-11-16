OUTBOX = []  # emails we "sent" (a real shop would call a mail service here)

CONFIRMATION = """Hi!

Thanks for your order #{id}. Here's what you bought:

{lines}

Total: ${total:.2f}

We'll email you again when it ships.
The Tiny Shop team
"""


def order_confirmation(order):
    lines = "\n".join(f"  {i.qty} x {i.name}  ${i.price:.2f}" for i in order.items)
    body = CONFIRMATION.format(id=order.id, lines=lines, total=order.total)
    OUTBOX.append({"to": order.email, "subject": f"Order #{order.id} confirmed", "body": body})
    return body
