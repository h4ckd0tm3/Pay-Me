import math
import os
from io import BytesIO

import cairosvg
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, send_file, url_for
from segno import helpers

load_dotenv()

app = Flask(__name__)

PAYEE_NAME = os.getenv('PAYEE_NAME', 'Max Musterperson')
IBAN = os.getenv('IBAN', 'AT1234560000000123')
BIC = os.getenv('BIC', 'BKAUATWW')
PAYPAL_USERNAME = os.getenv('PAYPAL_USERNAME', '')
QR_TEXT = os.getenv('QR_TEXT', 'Pay-Me!')


def parse_amount(raw):
    """Parse and validate a payment amount string. Returns a float or raises ValueError."""
    raw = raw.replace(",", ".")
    value = float(raw)
    if not math.isfinite(value) or value < 0:
        raise ValueError("Invalid amount")
    return value


def get_paypal_user():
    """Return the PayPal username if configured, else None."""
    return PAYPAL_USERNAME if PAYPAL_USERNAME and PAYPAL_USERNAME.strip() else None


@app.route('/')
def main():
    if request.args.get("amount") is not None:
        return redirect(f"/{request.args.get('amount')}")
    return render_template("index.html")


@app.route('/<amount>')
def pay(amount):
    try:
        amount = parse_amount(amount)
    except ValueError:
        return redirect(url_for("main"))

    qrcode = helpers.make_epc_qr(
        name=PAYEE_NAME, iban=IBAN, bic=BIC,
        amount=amount, text=QR_TEXT,
    )
    return render_template(
        "pay.html",
        amount=f"{amount:.2f}",
        qrcode=qrcode,
        payee_name=PAYEE_NAME,
        iban=IBAN,
        bic=BIC,
        paypal_username=get_paypal_user(),
    )


@app.route('/<amount>/preview')
def image_preview(amount):
    try:
        amount_float = parse_amount(amount)
    except ValueError:
        return redirect(url_for("main"))

    has_paypal = get_paypal_user() is not None
    svg_content = render_template(
        "preview.svg",
        amount=f"{amount_float:.2f}",
        payee_name=PAYEE_NAME,
        has_paypal=has_paypal,
        methods_transform="translate(100, 235)" if has_paypal else "translate(140, 235)",
    )

    try:
        png_buffer = BytesIO()
        cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to=png_buffer,
            output_width=1200,
            output_height=800,
        )
        png_buffer.seek(0)
        return send_file(
            png_buffer,
            mimetype='image/png',
            as_attachment=False,
            download_name=f'pay-{amount_float:.2f}-preview.png',
        )
    except Exception:
        return redirect(url_for("main"))


if __name__ == '__main__':
    app.run()
