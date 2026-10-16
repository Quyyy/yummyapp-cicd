import unittest
from unittest.mock import patch
from yummy_app import YummyApp
import gps_service


# ================================================================
# CAP DO 1: Bo test co ban cho san (~35% Coverage)
# ================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang"""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


# ================================================================
# CAP DO 2: Kiem thu Mocking va xu ly ngoai le (Dua Coverage >= 85%)
# ================================================================
#class TestMediumLevel(unittest.TestCase):
    """Kiem thu chuc nang ap dung ma khuyen mai (apply_promo_code)"""

    def test_promo_online_valid(self):
        """Kich ban 1: Online hop le, ap dung ma GIAM10 thanh cong"""
        app = YummyApp(network_status="online", os_version=15)
        total_after_discount = app.apply_promo_code(100000.0, "GIAM10")
        self.assertAlmostEqual(total_after_discount, 90000.0)

    def test_promo_offline_raises_connection_error(self):
        """Kich ban 2: Offline nem ngoai le ConnectionError"""
        app = YummyApp(network_status="offline", os_version=15)
        with self.assertRaises(ConnectionError) as ctx:
            app.apply_promo_code(100000.0, "GIAM10")
        self.assertIn("Khong co ket noi mang", str(ctx.exception))

    def test_promo_special_code_valid_on_os_15(self):
        """Kich ban 3: Ma dac biet NEW_OS_ONLY hop le tren OS 15"""
        app = YummyApp(network_status="online", os_version=15)
        total_after_discount = app.apply_promo_code(100000.0, "NEW_OS_ONLY")
        self.assertAlmostEqual(total_after_discount, 80000.0)

    def test_promo_special_code_on_os_14_raises_value_error(self):
        """Kich ban 4: Ma dac biet tren OS 14 bi nem ValueError"""
        app = YummyApp(network_status="online", os_version=14)
        with self.assertRaises(ValueError) as ctx:
            app.apply_promo_code(100000.0, "NEW_OS_ONLY")
        self.assertIn("yeu cau HDH phien ban 15 tro len", str(ctx.exception))

    def test_promo_invalid_code_raises_value_error(self):
        """Kich ban bo sung: Ma khuyen mai khong ton tai trong he thong"""
        app = YummyApp(network_status="online", os_version=15)
        with self.assertRaises(ValueError) as ctx:
            app.apply_promo_code(100000.0, "MA_KHONG_TON_TAI")
        self.assertIn("Ma khuyen mai khong hop le", str(ctx.exception))


#class TestHardLevel(unittest.TestCase):
    """Kiem thu chuc nang tim nha hang voi Mocking GPS (get_nearby_restaurants)"""

    @patch('yummy_app.gps_service.get_current_location')
    def test_nearby_restaurants_in_range(self, mock_gps):
        """Kich ban 5: Mock GPS tra ve toa do trong vung (10.0, 105.0)"""
        mock_gps.return_value = (10.0, 105.0)
        app = YummyApp()
        restaurants = app.get_nearby_restaurants()
        self.assertEqual(restaurants, ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"])
        mock_gps.assert_called_once()

    @patch('yummy_app.gps_service.get_current_location')
    def test_nearby_restaurants_out_of_range(self, mock_gps):
        """Kich ban 6: Mock GPS tra ve toa do ngoai vung (20.0, 110.0)"""
        mock_gps.return_value = (20.0, 110.0)
        app = YummyApp()
        restaurants = app.get_nearby_restaurants()
        self.assertEqual(restaurants, [])
        mock_gps.assert_called_once()

    @patch('yummy_app.gps_service.get_current_location')
    def test_nearby_restaurants_gps_signal_lost(self, mock_gps):
        """Kich ban 7: Mock GPS nem ngoai le GPSSignalLostError"""
        mock_gps.side_effect = gps_service.GPSSignalLostError()
        app = YummyApp()
        result = app.get_nearby_restaurants()
        self.assertEqual(result, "Khong the xac dinh vi tri.")
        mock_gps.assert_called_once()

    def test_gps_service_real_function(self):
        """Kiem thu truc tiep ham get_current_location trong gps_service de dat coverage 100%"""
        loc = gps_service.get_current_location()
        self.assertEqual(loc, (10.0, 105.0))


if __name__ == '__main__':
    unittest.main()
