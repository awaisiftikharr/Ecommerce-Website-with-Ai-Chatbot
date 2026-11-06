# Product Recommendation Module

Reusable content-based recommendations for SmartFinds. The engine combines product names and descriptions, vectorizes text with TF-IDF, ranks catalogue items by cosine similarity, excludes the source product, and safely handles missing/empty text. Run tests from `ecommerce_project/` with `python manage.py test recommendations`.
