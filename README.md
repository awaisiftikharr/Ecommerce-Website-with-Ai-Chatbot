# SmartFinds — AI-Powered E-Commerce Store

SmartFinds is a Django e-commerce application with product browsing, cart and checkout flows, account registration/login, a lightweight product-help chatbot, and content-based product recommendations.

## Main capabilities

- Product catalogue with keyword search and pagination
- Product detail pages
- TF-IDF + cosine-similarity recommendations based on product names and descriptions
- Customer accounts and session authentication
- Cart and checkout demonstration flows
- Rule-based product chatbot for simple availability and price questions

## Technology

Python · Django · SQLite · scikit-learn · HTML templates · JavaScript

## Repository layout

```text
ecommerce_project/
  ecommerce_project/       # Django settings and URL configuration
  store/                   # Products, customers, carts, checkout and templates
  recommendations/         # Reusable recommendation engine and tests
  media/                   # Sample product images
  manage.py
  requirements.txt
```

## Local setup

Use Python 3.12 or a version compatible with the pinned dependencies.

```bash
cd ecommerce_project
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Environment and security

Django reads these settings from environment variables:

- `DJANGO_SECRET_KEY` — required for production; use a unique random secret.
- `DJANGO_DEBUG` — defaults to true for local development. Set false in production.
- `DJANGO_ALLOWED_HOSTS` — comma-separated hostnames; defaults to localhost values.

Example (PowerShell):

```powershell
$env:DJANGO_SECRET_KEY = "replace-with-a-new-long-random-secret"
$env:DJANGO_DEBUG = "false"
$env:DJANGO_ALLOWED_HOSTS = "your-domain.com"
python manage.py check --deploy
```

The previous settings file contained a hard-coded development Django secret. It has been removed from the current settings file. Configure a new secret in your deployment environment; do not reuse the old value. Earlier Git commits may still contain it, so rotate it before deploying.

## Recommendation engine

The reusable implementation lives in `ecommerce_project/recommendations/engine.py`. It combines product names and descriptions, builds TF-IDF vectors, ranks products using cosine similarity, excludes the source product, and returns the top related products. The product detail view calls this service.

Run its tests from the `ecommerce_project/` directory:

```bash
python manage.py test recommendations
python manage.py check
```

## Limitations

The recommender is a content-based baseline, not collaborative filtering or a personalized model trained on purchase history. It uses product catalogue text fields. The checkout flow is a demonstration, not a payment-provider integration. Review authorization, payment processing, and production deployment settings before real-world use.
