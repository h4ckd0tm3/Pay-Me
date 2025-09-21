# Pay Me 💳

A modern Flask web application that generates payment QR codes and PayPal links for easy money transfers. Users can enter an amount and choose between PayPal payments or SEPA bank transfers with automatically generated EPC QR codes.

## Features

- **PayPal Integration**: Direct links to PayPal.me for instant payments
- **SEPA Bank Transfers**: Generate EPC QR codes for European bank transfers
- **Configurable**: All payment details configured via environment variables
- **Modern UI**: Glass-morphism design with responsive layout
- **Docker Ready**: Containerized with Alpine Linux for production deployment

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/h4ckd0tm3/Pay-Me.git
   cd Pay-Me
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your payment details
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

### Docker Deployment

#### Using Docker directly

1. **Build the image**
   ```bash
   docker build -t pay-me .
   ```

2. **Run with environment variables**
   ```bash
   docker run -p 5001:5001 \
     -e PAYEE_NAME="Your Name" \
     -e IBAN="YOUR_IBAN" \
     -e BIC="YOUR_BIC" \
     -e PAYPAL_USERNAME="your_paypal" \
     -e QR_TEXT="your-domain.com" \
     pay-me
   ```

#### Using Pre-built Image from GitHub Container Registry

   ```bash
   docker run -p 5001:5001 \
     -e PAYEE_NAME="Your Name" \
     -e IBAN="YOUR_IBAN" \
     -e BIC="YOUR_BIC" \
     -e PAYPAL_USERNAME="your_paypal" \
     -e QR_TEXT="your-domain.com" \
     ghcr.io/h4ckd0tm3/pay-me:main
   ```


#### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  pay-me:
    build: .
    ports:
      - "5001:5001"
    environment:
      - PAYEE_NAME=Your Name
      - IBAN=YOUR_IBAN_HERE
      - BIC=YOUR_BIC_HERE
      - PAYPAL_USERNAME=your_paypal_username
      - QR_TEXT=your-domain.com
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

#### Using Pre-built Image from GitHub Container Registry

```yaml
version: '3.8'

services:
  pay-me:
    image: ghcr.io/h4ckd0tm3/pay-me:main
    ports:
      - "5001:5001"
    environment:
      - PAYEE_NAME=Your Name
      - IBAN=YOUR_IBAN_HERE
      - BIC=YOUR_BIC_HERE
      - PAYPAL_USERNAME=your_paypal_username
      - QR_TEXT=your-domain.com
    restart: unless-stopped
```

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PAYEE_NAME` | Name displayed on payment page | `John Doe` |
| `IBAN` | Bank account IBAN for transfers | `DE89370400440532013000` |
| `BIC` | Bank BIC/SWIFT code | `COBADEFFXXX` |
| `PAYPAL_USERNAME` | PayPal.me username | `johndoe` |
| `QR_TEXT` | Text embedded in QR code | `pay.example.com` |

### Configuration with Docker

#### Method 1: Environment File

Create a `.env` file:
```bash
PAYEE_NAME=John Doe
IBAN=DE89370400440532013000
BIC=COBADEFFXXX
PAYPAL_USERNAME=johndoe
QR_TEXT=pay.example.com
```

Use with Docker:
```bash
docker run -p 5001:5001 --env-file .env pay-me
```

Or with Docker Compose:
```yaml
services:
  pay-me:
    build: .
    ports:
      - "5001:5001"
    env_file:
      - .env
```

#### Method 2: Docker Secrets (Production)

For production deployments, use Docker secrets:

```yaml
version: '3.8'

services:
  pay-me:
    image: ghcr.io/[username]/pay-me:main
    ports:
      - "5001:5001"
    environment:
      - PAYEE_NAME=John Doe
      - IBAN_FILE=/run/secrets/iban
      - BIC_FILE=/run/secrets/bic
      - PAYPAL_USERNAME=johndoe
      - QR_TEXT=pay.example.com
    secrets:
      - iban
      - bic

secrets:
  iban:
    file: ./secrets/iban.txt
  bic:
    file: ./secrets/bic.txt
```

### Health Check

Add health check to your Docker Compose:

```yaml
services:
  pay-me:
    # ... other config
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:5001/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Development

### Project Structure

```
Pay-Me/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container configuration
├── entrypoint.sh      # Container startup script
├── .env.example       # Environment template
├── templates/         # Jinja2 templates
│   ├── layout.html
│   ├── index.html
│   └── pay.html
└── static/           # Static assets
    └── css/
        └── main.less # LESS stylesheets
```

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Test endpoints
curl http://localhost:5000/
curl http://localhost:5000/10.50
```

## Security Considerations

- Never commit `.env` files with real payment details
- Use Docker secrets for production deployments
- Implement rate limiting for production use
- Consider adding HTTPS termination with a reverse proxy
- Validate and sanitize all user inputs
- Monitor for suspicious payment requests

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub