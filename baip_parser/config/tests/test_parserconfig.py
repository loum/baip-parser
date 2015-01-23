# pylint: disable=R0904,C0103
""":class:`baip_parser.ParserConfig` tests.

"""
import unittest2
import os

import baip_parser


class TestParserConfig(unittest2.TestCase):
    """:class:`baip_parser.ParserConfig` test cases.
    """
    @classmethod
    def setUpClass(cls):
        cls._file = os.path.join('baip_parser',
                                 'config',
                                 'tests',
                                 'files',
                                 'baip-parser.conf')

    def setUp(self):
        self._conf = baip_parser.ParserConfig()

    def test_init(self):
        """Initialise a ParserConfig object.
        """
        msg = 'Object is not a baip_parser.ParserConfig'
        self.assertIsInstance(self._conf, baip_parser.ParserConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        self._conf.set_config_file(self._file)
        self._conf.parse_config()

        received = self._conf.thread_sleep
        expected = 10.0
        msg = 'ParserConfig.thread_sleep not as expected'
        self.assertEqual(received, expected, msg)

        received = self._conf.inbound_dir
        expected = '/var/tmp/baip-parser'
        msg = 'ParserConfig.inbound_dir not as expected'
        self.assertEqual(received, expected, msg)

        received = self._conf.archive_dir
        expected = '/var/tmp/baip-parser/archive'
        msg = 'ParserConfig.archive_dir not as expected'
        self.assertEqual(received, expected, msg)

        received = self._conf.skip_sheets
        expected = ['ControlSheet', 'Instructions', 'WorkbookLog']
        msg = 'ParserConfig.skip_lists not as expected'
        self.assertListEqual(received, expected, msg)

        received = self._conf.cells_to_extract
        expected = ['B1', 'B2']
        msg = 'ParserConfig.cells_to_extract not as expected'
        self.assertListEqual(received, expected, msg)

        received = self._conf.cell_order
        expected = ['B2', 'B1']
        msg = 'ParserConfig.cell_order not as expected'
        self.assertListEqual(received, expected, msg)

        received = self._conf.ignore_if_empty
        expected = ['B1', 'B2']
        msg = 'ParserConfig.ignore_if_empty not as expected'
        self.assertListEqual(received, expected, msg)

        received = self._conf.cell_map
        expected = {'B1': ['banana'],
                    'B2': ['apple'],
                    'B3': ['orange', 'grapes']}
        msg = 'ParserConfig.cell_map not as expected'
        self.assertDictEqual(received, expected, msg)

    def tearDown(self):
        self._conf = None
        del self._conf

    @classmethod
    def tearDownClass(cls):
        cls._file = None
        del cls._file
