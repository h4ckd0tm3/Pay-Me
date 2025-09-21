import os
from flask import Flask, render_template, redirect, url_for, request, send_file
from segno import helpers
from dotenv import load_dotenv
import tempfile
import cairosvg

load_dotenv()

app = Flask(__name__)

# Payment configuration from environment variables
PAYEE_NAME = os.getenv('PAYEE_NAME', 'Max Musterperson')
IBAN = os.getenv('IBAN', 'AT1234560000000123')
BIC = os.getenv('BIC', 'BKAUATWW')
PAYPAL_USERNAME = os.getenv('PAYPAL_USERNAME', '')
QR_TEXT = os.getenv('QR_TEXT', 'Pay-Me!')


def generate_payment_preview_svg(amount, payee_name, paypal_username):
    """Generate SVG for payment preview using colors and fonts from CSS"""
    
    # Determine if PayPal is available
    has_paypal = paypal_username and paypal_username.strip()
    
    # Calculate positioning based on available payment methods
    if has_paypal:
        # Three methods: PayPal, Bank, QR
        methods_html = """
            <!-- PayPal -->
            <rect x="0" y="0" width="120" height="60" rx="12" ry="12" 
                  fill="rgba(255, 255, 255, 0.05)" 
                  stroke="rgba(255, 255, 255, 0.1)" stroke-width="1"/>
            <text x="60" y="25" text-anchor="middle" 
                  font-family="Noto Color Emoji, Noto Sans" 
                  font-size="24" fill="white">💳</text>
            <text x="60" y="45" text-anchor="middle" 
                  font-family="Noto Sans" 
                  font-size="14" fill="#888">PayPal</text>
            
            <!-- Bank Transfer -->
            <rect x="140" y="0" width="120" height="60" rx="12" ry="12" 
                  fill="rgba(255, 255, 255, 0.05)" 
                  stroke="rgba(255, 255, 255, 0.1)" stroke-width="1"/>
            <text x="200" y="25" text-anchor="middle" 
                  font-family="Noto Color Emoji, Noto Sans" 
                  font-size="24" fill="white">🏦</text>
            <text x="200" y="45" text-anchor="middle" 
                  font-family="Noto Sans" 
                  font-size="14" fill="#888">Bank Transfer</text>
            
            <!-- QR Code -->
            <rect x="280" y="0" width="120" height="60" rx="12" ry="12" 
                  fill="rgba(255, 255, 255, 0.05)" 
                  stroke="rgba(255, 255, 255, 0.1)" stroke-width="1"/>
            <text x="340" y="25" text-anchor="middle" 
                  font-family="Noto Color Emoji, Noto Sans" 
                  font-size="24" fill="white">📱</text>
            <text x="340" y="45" text-anchor="middle" 
                  font-family="Noto Sans" 
                  font-size="14" fill="#888">QR Code</text>"""
        transform = "translate(100, 230)"
    else:
        # Two methods: Bank, QR (centered)
        methods_html = """
            <!-- Bank Transfer -->
            <rect x="0" y="0" width="150" height="60" rx="12" ry="12" 
                  fill="rgba(255, 255, 255, 0.05)" 
                  stroke="rgba(255, 255, 255, 0.1)" stroke-width="1"/>
            <text x="75" y="25" text-anchor="middle" 
                  font-family="Noto Color Emoji, Noto Sans" 
                  font-size="24" fill="white">🏦</text>
            <text x="75" y="45" text-anchor="middle" 
                  font-family="Noto Sans" 
                  font-size="14" fill="#888">Bank Transfer</text>
            
            <!-- QR Code -->
            <rect x="170" y="0" width="150" height="60" rx="12" ry="12" 
                  fill="rgba(255, 255, 255, 0.05)" 
                  stroke="rgba(255, 255, 255, 0.1)" stroke-width="1"/>
            <text x="245" y="25" text-anchor="middle" 
                  font-family="Noto Color Emoji, Noto Sans" 
                  font-size="24" fill="white">📱</text>
            <text x="245" y="45" text-anchor="middle" 
                  font-family="Noto Sans" 
                  font-size="14" fill="#888">QR Code</text>"""
        transform = "translate(140, 230)"
    
    svg_template = f"""
    <svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#16213e;stop-opacity:1" />
            </linearGradient>
            <filter id="blur" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="10"/>
            </filter>
        </defs>
        
        <!-- Background -->
        <rect width="600" height="400" fill="url(#bgGradient)"/>
        
        <!-- Glass morphism card -->
        <rect x="50" y="50" width="500" height="300" rx="20" ry="20" 
              fill="rgba(255, 255, 255, 0.1)" 
              stroke="rgba(255, 255, 255, 0.2)" 
              stroke-width="1"/>
        
        <!-- Brand -->
        <text x="300" y="100" text-anchor="middle" 
              font-family="Noto Sans" 
              font-size="24" font-weight="100" fill="#cccccc">Pay</text>
        
        <!-- Amount -->
        <text x="300" y="160" text-anchor="middle" 
              font-family="Noto Sans" 
              font-size="48" font-weight="200" fill="#4a9eff">€ {amount}</text>
        
        <!-- Payee -->
        <text x="300" y="200" text-anchor="middle" 
              font-family="Noto Sans" 
              font-size="24" font-weight="100" fill="#cccccc">to {payee_name}</text>
        
        <!-- Payment methods -->
        <g transform="{transform}">
            {methods_html}
        </g>
        
        <!-- Powered by -->
        <text x="300" y="340" text-anchor="middle" 
              font-family="Noto Sans" 
              font-size="12" fill="#666">Powered by Pay Me</text>
    </svg>
    """
    return svg_template


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
        # Only pass PayPal username if it's configured
        paypal_user = PAYPAL_USERNAME if PAYPAL_USERNAME and PAYPAL_USERNAME.strip() else None
        return render_template("pay.html", amount=f"{amount:.2f}", qrcode=qrcode, 
                             payee_name=PAYEE_NAME, iban=IBAN, bic=BIC, paypal_username=paypal_user)
    except ValueError:
        # Handle the exception
        return redirect(url_for("main"))


@app.route('/<amount>/preview')
def image_preview(amount):
    try:
        amount = amount.replace(",", ".")
        amount_float = float(amount)
        if amount_float < 0:
            raise ValueError("Negative Number")
        
        # Generate SVG content
        paypal_user = PAYPAL_USERNAME if PAYPAL_USERNAME and PAYPAL_USERNAME.strip() else None
        svg_content = generate_payment_preview_svg(
            f"{amount_float:.2f}", 
            PAYEE_NAME, 
            paypal_user
        )
        
        # Create temporary file for the PNG
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            # Convert SVG to PNG using cairosvg
            cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                write_to=tmp_file.name,
                output_width=1200,  # 2x for better quality
                output_height=800
            )
            
            # Return the PNG file
            return send_file(tmp_file.name, 
                           mimetype='image/png',
                           as_attachment=False,
                           download_name=f'pay-{amount_float:.2f}-preview.png')
            
    except ValueError:
        return redirect(url_for("main"))
    except Exception as e:
        # Handle cairosvg errors gracefully
        return f"Error generating preview: {str(e)}", 500


if __name__ == '__main__':
    app.run()
