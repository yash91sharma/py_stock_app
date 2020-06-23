import unittest
import os
import stock_fc
import pandas as pd

class TestStockfcMethods(unittest.TestCase):
    def test_get_stock_list(self):
        stock_list = stock_fc.get_stock_list(['All'])
        self.assertIsInstance(stock_list, list)
        self.assertGreater(len(stock_list), 30)

    def test_get_summary(self):
        stock_list = stock_fc.get_stock_list(['All'])
        returned_list = stock_fc.get_summary(stock_list)
        self.assertEqual(len(returned_list), 2)
        self.assertIsInstance(returned_list[0], float)
        self.assertIsInstance(returned_list[1], int)
    
    def test_get_sector_list(self):
        return_data = stock_fc.get_sector_stock_list()
        self.assertEqual(len(return_data), 2)
        self.assertIsInstance(return_data[0], list)
        self.assertIsInstance(return_data[1], list)
    
    def test_import_daily_record(self):
        df = stock_fc.import_daily_record(os.path.dirname(__file__) + '/data/test_datasets/daily_record_test.csv')
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df.columns), 6)
        self.assertEqual(len(df), 5)
    
    def test_import_txn_master(self):
        df = stock_fc.import_txn_master(os.path.dirname(__file__) + '/data/test_datasets/txn_master_test.csv')
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df.columns), 6)
        self.assertEqual(len(df), 5)
    
    def test_get_stock_history(self):
        df = stock_fc.get_stock_history('GOOG', '2020-01-01','2020-02-02')
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df.columns), 9)
        self.assertEqual(len(df), 21)

if __name__ == '__main__':
    unittest.main()