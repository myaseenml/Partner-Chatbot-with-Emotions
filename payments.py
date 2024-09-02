from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
import stripe

payments_bp = Blueprint('payments_bp', __name__, template_folder='templates')

# Set your secret key. Remember to switch to your live secret key in production!
# You can find your API keys in the Stripe Dashboard
stripe.api_key = 'your_stripe_secret_key'

# Pricing information
PRODUCTS = {
    'basic': {'price': 300, 'words': 1000, 'name': '1000 Words Package'},
    'standard': {'price': 1300, 'words': 5000, 'name': '5000 Words Package'},
    'premium': {'price': 2400, 'words': 10000, 'name': '10000 Words Package'}
}

@payments_bp.route('/payments')
def payments():
    return render_template('payments.html', products=PRODUCTS)

@payments_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        product_id = request.form.get('product_id')
        product = PRODUCTS[product_id]

        # Create a Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product['name'],
                    },
                    'unit_amount': product['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payments_bp.success', _external=True),
            cancel_url=url_for('payments_bp.cancel', _external=True),
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return str(e)

@payments_bp.route('/success')
def success():
    # Handle the logic after successful payment here
    return render_template('success.html')

@payments_bp.route('/cancel')
def cancel():
    # Handle the logic for canceled payment here
    return render_template('cancel.html')
