import unittest
from unittest.mock import MagicMock, patch

import ingest
import live_ingest


GPU = {'idproducto': 7, 'name': 'NVIDIA RTX 5070', 'model': '5070', 'sku_global': 'AUTO-NVIDIA-RTX-5070'}


def offer(name, price=100, available=True):
    return {'name': name, 'price': price, 'available': available, 'url': 'https://example.test/' + str(price)}


class IngestionTests(unittest.TestCase):
    def test_save_rejects_incompatible_offer_before_writing(self):
        cursor = MagicMock()
        with self.assertRaises(ValueError):
            live_ingest.save_offer(cursor, 1, GPU, offer('Laptop RTX 5070'))
        cursor.execute.assert_not_called()

    def test_save_reactivates_offer_updates_image_and_keeps_price_history(self):
        cursor = MagicMock()
        cursor.fetchone.side_effect = [(5,), (120, 1)]
        item = {**offer('Tarjeta de video RTX 5070'), 'image': 'https://example.test/gpu.jpg'}
        live_ingest.save_offer(cursor, 1, GPU, item)
        calls = cursor.execute.call_args_list
        self.assertIn('estado=1', calls[0].args[0])
        price = next(call for call in calls if call.args[0].startswith('INSERT INTO precio'))
        self.assertEqual(price.args[1], (5, 100, 120, 'GTQ', 1))
        cursor.execute.assert_any_call('UPDATE producto SET imagen=%s WHERE idproducto=%s', (item['image'], 7))

    def test_same_price_and_stock_do_not_duplicate_history(self):
        cursor = MagicMock()
        cursor.fetchone.side_effect = [(5,), (100, 1)]
        live_ingest.save_offer(cursor, 1, GPU, offer('GeForce RTX 5070'))
        self.assertFalse(any(call.args[0].startswith('INSERT INTO precio') for call in cursor.execute.call_args_list))

    def test_only_best_valid_offer_is_saved_without_pending_matches(self):
        db = MagicMock()
        cursor = db.cursor.return_value
        cursor.fetchone.side_effect = [(1,), (1,), (1,)]
        scraper = MagicMock()
        scraper.return_value.search.return_value = [
            offer('Laptop RTX 5070', 10), offer('RTX 5070 Ti', 20),
            offer('Tarjeta de video RTX 5070', 80, False),
            offer('MSI GeForce RTX 5070', 120), offer('ASUS GeForce RTX 5070', 100),
            offer('RTX 5070', float('nan')),
        ]
        with patch.multiple(live_ingest, SCRAPERS={'test': scraper}), \
             patch.object(live_ingest, 'connect_db', return_value=db), \
             patch.object(live_ingest, 'load_catalog', return_value=[GPU]), \
             patch.object(live_ingest, 'revalidate_offers', return_value=1), \
             patch.object(live_ingest, 'catalog_product', return_value=GPU) as catalog, \
             patch.object(live_ingest, 'save_offer') as save:
            result = live_ingest.run('RTX 5070')
        self.assertEqual(result['offers'], 1)
        self.assertEqual(result['skipped'], 5)
        self.assertEqual(result['invalidated'], 1)
        self.assertEqual(catalog.call_args.args[2]['name'], 'ASUS GeForce RTX 5070')
        self.assertEqual(save.call_args.args[3]['price'], 100)
        queries = ' '.join(call.args[0] for call in cursor.execute.call_args_list)
        self.assertNotIn('producto_match_pendiente', queries)
        self.assertIn('UPDATE scraper_log', queries)
        db.commit.assert_called_once()

    def test_invalid_first_result_cannot_create_a_catalog_product(self):
        cursor = MagicMock()
        self.assertIsNone(live_ingest.catalog_product(cursor, 'RTX 5070', offer('Laptop RTX 5070')))
        cursor.execute.assert_not_called()

    def test_generic_brand_or_category_query_cannot_reuse_a_catalog_product(self):
        cursor = MagicMock()
        self.assertIsNone(live_ingest.catalog_product(cursor, 'Audifonos Xiaomi', offer('Audifonos Xiaomi Redmi Buds 6')))
        cursor.execute.assert_not_called()

    def test_new_product_uses_full_query_and_real_brand_id(self):
        cursor = MagicMock()
        cursor.fetchone.side_effect = [(2,), (42,), (7, 'NVIDIA RTX 5070 Ti', 'RTX 5070 Ti', 'AUTO-NVIDIA-RTX-5070-TI')]
        with patch.object(live_ingest, 'load_catalog', return_value=[{'name': 'Laptop RTX 5070 Ti', 'model': '5070'}]):
            product = live_ingest.catalog_product(cursor, 'RTX 5070 Ti', offer('Tarjeta RTX5070Ti'))
        insert = next(call for call in cursor.execute.call_args_list if call.args[0].startswith('INSERT INTO producto '))
        self.assertEqual(insert.args[1][1], 42)
        self.assertEqual(insert.args[1][2], 'NVIDIA RTX 5070 Ti')
        self.assertEqual(insert.args[1][3], 'RTX 5070 Ti')
        self.assertEqual(product['model'], 'RTX 5070 Ti')

    def test_revalidation_disables_bad_offers_and_preserves_history(self):
        cursor = MagicMock()
        cursor.fetchall.return_value = [(1, 7, 'Laptop RTX 5070', None), (2, 7, 'GeForce RTX 5070', None)]
        self.assertEqual(ingest.revalidate_offers(cursor, 1, [GPU]), 1)
        cursor.execute.assert_any_call('UPDATE producto_tienda SET estado=0 WHERE idproducto_tienda=%s', (1,))
        self.assertFalse(any('DELETE' in call.args[0] for call in cursor.execute.call_args_list))

    def test_store_failure_rolls_back_and_records_error(self):
        db = MagicMock()
        cursor = db.cursor.return_value
        cursor.fetchone.return_value = (1,)
        scraper = MagicMock()
        scraper.return_value.search.side_effect = RuntimeError('scraper failed')
        with patch.multiple(live_ingest, SCRAPERS={'test': scraper}), \
             patch.object(live_ingest, 'connect_db', return_value=db), \
             patch.object(live_ingest, 'load_catalog', return_value=[GPU]), \
             patch.object(live_ingest, 'revalidate_offers', return_value=1):
            result = live_ingest.run('RTX 5070')
        self.assertEqual(result['stores']['test']['errors'], 1)
        self.assertEqual(result['invalidated'], 0)
        cursor.execute.assert_any_call('ROLLBACK TO SAVEPOINT ingesta_tienda')
        self.assertTrue(any('UPDATE scraper_log' in call.args[0] for call in cursor.execute.call_args_list))

    def test_empty_results_still_revalidate_old_offers(self):
        db = MagicMock()
        db.cursor.return_value.fetchone.return_value = (1,)
        scraper = MagicMock()
        scraper.return_value.search.return_value = []
        with patch.multiple(live_ingest, SCRAPERS={'test': scraper}), \
             patch.object(live_ingest, 'connect_db', return_value=db), \
             patch.object(live_ingest, 'load_catalog', return_value=[GPU]), \
             patch.object(live_ingest, 'revalidate_offers', return_value=1) as revalidate:
            result = live_ingest.run('RTX 5070')
        revalidate.assert_called_once()
        self.assertEqual(result['invalidated'], 1)
        self.assertEqual(result['offers'], 0)

    def test_uncertain_valid_offer_is_retained_for_review(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        item = offer('Mouse Logitech G502 inalámbrico')
        live_ingest.save_review_candidate(cursor, 1, item, 72.5)
        insert = cursor.execute.call_args_list[-1]
        self.assertIn('INSERT INTO producto_match_pendiente', insert.args[0])
        self.assertEqual(insert.args[1][-1], 72.5)

    def test_cli_uses_the_same_automatic_flow(self):
        with patch.object(live_ingest, 'run', return_value={'offers': 1}) as run:
            self.assertEqual(ingest.ingest('intelaf', 'RTX 5070'), {'offers': 1})
        run.assert_called_once_with('RTX 5070', stores=('intelaf',))


if __name__ == '__main__':
    unittest.main()
