from types import SimpleNamespace

from django.test import SimpleTestCase

from .engine import recommend_similar_products


class RecommendationEngineTests(SimpleTestCase):
    def setUp(self):
        self.products = [
            SimpleNamespace(id=1, name="Wireless Headphones", description="Bluetooth audio noise cancelling headphones"),
            SimpleNamespace(id=2, name="Bluetooth Earbuds", description="Wireless audio earbuds for music"),
            SimpleNamespace(id=3, name="Garden Shovel", description="Steel garden digging shovel for soil"),
            SimpleNamespace(id=4, name="Noise Cancelling Headset", description="Wireless headphones for travel"),
        ]

    def test_returns_related_products_and_excludes_source(self):
        results = recommend_similar_products(self.products, target_product_id=1, limit=2)
        result_ids = [item.id for item in results]
        self.assertEqual(len(results), 2)
        self.assertNotIn(1, result_ids)
        self.assertNotIn(3, result_ids)

    def test_missing_product_returns_empty_list(self):
        self.assertEqual(recommend_similar_products(self.products, 999), [])

    def test_single_product_returns_empty_list(self):
        self.assertEqual(recommend_similar_products(self.products[:1], 1), [])

    def test_empty_descriptions_are_handled(self):
        empty = [
            SimpleNamespace(id=1, name="", description=""),
            SimpleNamespace(id=2, name="", description=""),
        ]
        self.assertEqual(recommend_similar_products(empty, 1), [])

    def test_non_positive_limit_returns_empty_list(self):
        self.assertEqual(recommend_similar_products(self.products, 1, limit=0), [])
