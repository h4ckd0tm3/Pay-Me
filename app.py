import os
from flask import Flask, render_template, redirect, url_for, request
from segno import helpers
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Payment configuration from environment variables
PAYEE_NAME = os.getenv('PAYEE_NAME', 'Max Musterperson')
IBAN = os.getenv('IBAN', 'AT1234560000000123')
BIC = os.getenv('BIC', 'BKAUATWW')
PAYPAL_USERNAME = os.getenv('PAYPAL_USERNAME', 'M Musterperson')
QR_TEXT = os.getenv('QR_TEXT', 'Pay-Me!')


@app.route('/')
def main():
    if request.args.get("amount") is not None:
        return redirect(f"/{request.args.get('amount')}")
    return render_template("index.html")


@app.route('/<amount>')
def pay(amount):
    try:
        amount = amount.replace(",", ".")
        amount = float(amount)
        if amount < 0:
            raise ValueError("Negative Number")

        qrcode = helpers.make_epc_qr(name=PAYEE_NAME, iban=IBAN, bic=BIC,
                                     amount=amount, text=QR_TEXT)
        return render_template("pay.html", amount=f"{amount:.2f}", qrcode=qrcode, 
                             payee_name=PAYEE_NAME, iban=IBAN, bic=BIC, paypal_username=PAYPAL_USERNAME)
    except ValueError:
        # Handle the exception
        return redirect(url_for("main"))


if __name__ == '__main__':
    app.run()
