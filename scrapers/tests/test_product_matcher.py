import unittest

from core.product_matcher import classify_match, match, normalize
from live_ingest import relevant


class AutomaticMatchingTests(unittest.TestCase):
    def result(self, query, name, **extra):
        return classify_match({'name': name, **extra}, [{'name': query, 'model': query}])

    def test_accepts_standalone_components_and_normalized_models(self):
        cases = [
            ('RTX 5070', 'Tarjeta de video MSI GeForce RTX™5070 12GB Graphics Card'),
            ('RTX 5070 Ti', 'Tarjeta de video GeForce RTX5070Ti 16GB'),
            ('RTX 4070 Ti Super', 'Tarjeta GeForce RTX4070TiSuper'),
            ('RTX 5070 12 GB', 'GeForce RTX 5070 12GB'),
            ('Ryzen 5 7600', 'Procesador AMD R5-7600 AM5 con Cooler'),
            ('Ryzen 5 7600', 'Procesador AMD Ryzen 5 7600 incluye disipador Wraith Stealth'),
            ('Ryzen 5 7600', 'Procesador Ryzen 5 7600 con gráficos Radeon'),
            ('Ryzen 7 7800X3D', 'Procesador AMD Ryzen 7 7800X3D AM5'),
            ('Core i5 14600K', 'Procesador Intel Core i5-14600K'),
            ('Core Ultra 7 265K', 'Procesador Intel Core Ultra 7 265K'),
            ('RX 9070 XT', 'Tarjeta de video Radeon RX9070XT 16GB'),
            ('RTX 5070', 'Graphics card NVIDIA RTX 5070 for PC'),
        ]
        for query, name in cases:
            with self.subTest(query=query, name=name):
                self.assertEqual(self.result(query, name)['classification'], 'automatico')
                self.assertTrue(relevant({'name': name}, query))

    def test_excludes_computers_accessories_and_bundles(self):
        cases = [
            ('RTX 5070', 'Laptop MSI RTX 5070 16GB RAM 1TB SSD'),
            ('RTX 5070', 'Notebook GeForce RTX 5070'),
            ('RTX 5070', 'Portátil RTX 5070'),
            ('RTX 5070', 'ASUS ROG Strix G16 RTX 5070'),
            ('RTX 5070', 'NVIDIA RTX 5070 Mini PC'),
            ('RTX 5070', 'Gaming Computer RTX 5070'),
            ('RTX 5070', 'MSI RTX 5070 16GB DDR5 1TB SSD'),
            ('RTX 5070', 'RTX 5070 support bracket'),
            ('RTX 5070', 'Waterblock para RTX 5070'),
            ('RTX 5070', 'Cable de alimentación RTX 5070'),
            ('RTX 5070', 'Combo RTX 5070 + fuente 750W'),
            ('Ryzen 5 7600', 'Laptop AMD Ryzen 5 7600'),
            ('Ryzen 5 7600', 'Desktop AMD Ryzen 5 7600'),
            ('Ryzen 5 7600', 'Ryzen 5 7600 + RTX 5070'),
            ('Ryzen 5 7600', 'Motherboard compatible con AMD Ryzen 5 7600'),
            ('Ryzen 5 7600', 'Disipador para procesador Ryzen 5 7600'),
            ('Ryzen 5 7600', 'Ryzen 5 7600 cooler'),
            ('Ryzen 5 7600', 'Bundle Ryzen 5 7600 + motherboard'),
            ('Ryzen 5 7600', 'Kit de actualización Ryzen 5 7600'),
        ]
        for query, name in cases:
            with self.subTest(name=name):
                result = self.result(query, name)
                self.assertEqual(result['classification'], 'omitido')
                self.assertIsNotNone(result['reason'])
                self.assertFalse(relevant({'name': name}, query))

    def test_variants_are_not_interchangeable_in_either_direction(self):
        for left, right in [
            ('RTX 5070', 'RTX 5070 Ti'), ('RTX 4070 Ti', 'RTX 4070 Ti Super'),
            ('RX 9070', 'RX 9070 XT'), ('RX 7900 XT', 'RX 7900 XTX'),
            ('Ryzen 5 7600', 'Ryzen 5 7600X'), ('Ryzen 7 7800X', 'Ryzen 7 7800X3D'),
            ('Core i5 14600K', 'Core i5 14600KF'), ('Ryzen 5 5500', 'Ryzen 5 Pro 5500'),
            ('RTX 5070', 'RX 5070'), ('Ryzen 5 7600', 'RX 7600'),
        ]:
            for query, name in ((left, right), (right, left)):
                with self.subTest(query=query, name=name):
                    self.assertEqual(self.result(query, name)['classification'], 'omitido')
                    self.assertFalse(relevant({'name': name}, query))

    def test_sku_cannot_override_incompatible_type_or_variant(self):
        candidate = {'name': 'RTX 5070', 'model': '5070', 'sku_global': 'SAME'}
        for name in ('Laptop RTX 5070', 'RTX 5070 Ti', 'RTX 5070 bracket'):
            self.assertEqual(classify_match({'name': name, 'sku': 'SAME'}, [candidate])['score'], 0)

    def test_specific_gpu_requires_capacity_brand_and_edition(self):
        for query, name in [
            ('RTX 5060 Ti 16GB', 'RTX 5060 Ti 8GB'),
            ('MSI RTX 5070', 'ASUS RTX 5070'),
            ('MSI Ventus RTX 5070', 'MSI Gaming Trio RTX 5070'),
            ('RTX 5070 12GB', 'RTX 5070'),
        ]:
            self.assertEqual(self.result(query, name)['classification'], 'omitido')

    def test_accepts_ram_and_ssd_by_technology_and_specifications(self):
        cases = [
            ('Memoria RAM DDR5 De 8GB', 'Kingston FURY Beast Memoria RAM 8GB DDR5 5600MT/s'),
            ('Memoria RAM DDR5 De 8GB', 'Memoria RAM para Laptop DDR5 8GB 5600Mhz'),
            ('SSD NVMe 1TB', 'Kingston NV3 SSD NVMe PCIe 4.0 de 1TB'),
            ('SSD', 'SSD Kingston A400 480GB SATA'),
        ]
        for query, name in cases:
            with self.subTest(query=query, name=name):
                self.assertEqual(self.result(query, name)['classification'], 'automatico')
                self.assertTrue(relevant({'name': name}, query))

    def test_rejects_ram_and_ssd_with_different_technology_or_specs(self):
        cases = [
            ('Memoria RAM DDR5 De 8GB', 'Laptop HP 8GB DDR5 512GB SSD'),
            ('Memoria RAM DDR5 De 8GB', 'Memoria RAM 8GB DDR4'),
            ('SSD NVMe 1TB', 'Disco SSD SATA 1TB'),
            ('SSD NVMe 1TB', 'SSD NVMe 512GB'),
        ]
        for query, name in cases:
            with self.subTest(query=query, name=name):
                self.assertEqual(self.result(query, name)['classification'], 'omitido')
                self.assertFalse(relevant({'name': name}, query))

    def test_generic_evidence_resolves_new_models_without_model_rules(self):
        query = 'G502 X'
        compatible = 'Mouse Logitech G502 X Lightspeed inalámbrico'
        different = 'Mouse Logitech G305 inalámbrico'
        self.assertEqual(self.result(query, compatible)['classification'], 'automatico')
        self.assertTrue(relevant({'name': compatible}, query))
        self.assertEqual(self.result(query, different)['classification'], 'omitido')
        self.assertFalse(relevant({'name': different}, query))

    def test_component_does_not_select_laptop_in_catalog(self):
        laptop = {'name': 'Laptop RTX 5070', 'model': '5070'}
        gpu = {'name': 'NVIDIA RTX 5070', 'model': '5070'}
        result = classify_match({'name': 'Tarjeta de video RTX 5070 12GB'}, [laptop, gpu])
        self.assertEqual(result['classification'], 'automatico')
        self.assertEqual(result['product'], gpu)

    def test_ambiguous_catalog_is_skipped_without_manual_review(self):
        catalog = [{'name': 'RTX 5070', 'model': '5070', 'idproducto': value} for value in (1, 2)]
        result = classify_match({'name': 'RTX 5070'}, catalog)
        self.assertEqual(result['classification'], 'omitido')
        self.assertEqual(result['reason'], 'Coincidencia ambigua')
        self.assertIsNone(match({'name': 'RTX 5070'}, catalog))

    def test_sharing_a_gpu_does_not_identify_a_laptop(self):
        result = self.result('Laptop MSI RTX 5070', 'Laptop ASUS RTX 5070')
        self.assertEqual(result['classification'], 'omitido')

    def test_empty_names_do_not_match(self):
        self.assertEqual(self.result('', '')['classification'], 'omitido')
        self.assertFalse(relevant({'name': ''}, ''))
        self.assertEqual(normalize('RTX™ 5070®'), 'rtx 5070')


if __name__ == '__main__':
    unittest.main()
