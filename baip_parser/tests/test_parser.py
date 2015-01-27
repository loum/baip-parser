# pylint: disable=R0904,C0103,W0142,W0212
""":class:`baip_parser.TestParser` tests.

"""
import unittest2
import os
import tempfile
import openpyxl

import baip_parser


class TestParser(unittest2.TestCase):
    """:class:`baip_parser.Parser` test cases.
    """
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    def test_init(self):
        """Initialise a baip_parser.Parser object.
        """
        parser = baip_parser.Parser()
        msg = 'Object is not a baip_parser.Parser'
        self.assertIsInstance(parser, baip_parser.Parser, msg)

    def test_open_xlsx_file_handle_file_undefined(self):
        """Create an openpyxl.Workbook() object: file undefined.
        """
        # Given a dummy file.
        dummy_file_obj = tempfile.NamedTemporaryFile(suffix='.xlsx')
        dummy_file = dummy_file_obj.name
        dummy_file_obj.close()

        # When an attempting to create an openpyxl.Workbook object.
        parser = baip_parser.Parser()
        parser.open(dummy_file)

        # Then _workbook attribute should not be set.
        msg = 'Failed xlsx open should not set workbook'
        self.assertIsNone(parser.workbook, msg)

        # And _filepath attribute should not be set.
        msg = 'Failed xlsx open should not set filepath'
        self.assertIsNone(parser.filepath, msg)

    def test_open_xlsx_file_handle_file_defined(self):
        """Create an openpyxl.Workbook() object: file defined.
        """
        # Given a valid file.
        file = os.path.join('baip_parser',
                            'tests',
                            'files',
                            'BA-CLM-CLM-121-CRDPathway-v04.xlsx')

        # When an attempting to create an openpyxl.Workbook object.
        parser = baip_parser.Parser()
        parser.open(file)

        # Then _workbook attribute should be set.
        msg = 'xlsx open should set workbook'
        self.assertIsInstance(parser.workbook, openpyxl.Workbook, msg)

        # And _filepath attribute should be set.
        msg = 'Failed xlsx open should set filepath'
        self.assertEqual(parser.filepath, file, msg)

    def test_skip_sheet_no_sheets_to_skip(self):
        """Skip sheets: no sheets to skip.
        """
        # Given an empty list of sheet names to skip.
        parser = baip_parser.Parser()
        parser.skip_sheets = []

        # When I check if I should skip a sheet.
        received = parser.skip_sheet('CLM-122-006')

        # Then the sheet SHOULD NOT be skipped.
        msg = 'No sheets set to skip should return False'
        self.assertFalse(received, msg)

    def test_skip_sheet_existing_sheets_to_skip(self):
        """Skip sheets: sheets to skip.
        """
        # Given a list of sheet names to skip.
        parser = baip_parser.Parser()
        parser.skip_sheets = ['CLM-122-006', 'apple']

        # When I check if I should skip a sheet.
        received = parser.skip_sheet('CLM-122-006')

        # Then the sheet SHOULD be skipped.
        msg = 'Sheet set to skip should return True'
        self.assertTrue(received, msg)

    def test_parse_sheets_all_sheets_in_workbook(self):
        """Parse sheets: all sheets in workbook.
        """
        # Given a workbook.
        file = os.path.join('baip_parser',
                            'tests',
                            'files',
                            'BA-CLM-CLM-121-CRDPathway-v04.xlsx')
        parser = baip_parser.Parser()
        parser.open(file)

        # And a list of cells to extract.
        parser.cells_to_extract = ['B1']

        # When I parse the workbook.
        received = parser.parse_sheets()

        # I should receive a populated dictionary structure.
        filename = 'BA-CLM-CLM-121-CRDPathway-v04.xlsx'
        expected = {'%s|AAA-000-001' % filename: {'B1': u'AAA-000-001'},
                    '%s|CLM-121-001' % filename: {'B1': u'CLM-121-001'},
                    '%s|CLM-121-002' % filename: {'B1': u'CLM-121-002'},
                    '%s|CLM-121-003' % filename: {'B1': u'CLM-121-003'},
                    '%s|CLM-121-004' % filename: {'B1': u'CLM-121-004'},
                    '%s|CLM-121-013' % filename: {'B1': u'CLM-121-013'},
                    '%s|CLM-121-014' % filename: {'B1': u'CLM-121-014'},
                    '%s|CLM-121-015' % filename: {'B1': u'CLM-121-015'},
                    '%s|CLM-121-016' % filename: {'B1': u'CLM-121-016'},
                    '%s|CLM-121-017' % filename: {'B1': u'CLM-121-017'},
                    '%s|CLM-121-018' % filename: {'B1': u'CLM-121-018'},
                    '%s|CLM-121-019' % filename: {'B1': u'CLM-121-019'},
                    '%s|CLM-121-020' % filename: {'B1': u'CLM-121-020'},
                    '%s|CLM-121-021' % filename: {'B1': u'CLM-121-021'},
                    '%s|CLM-121-022' % filename: {'B1': u'CLM-121-022'},
                    '%s|CLM-121-023' % filename: {'B1': u'CLM-121-023'},
                    '%s|CLM-121-024' % filename: {'B1': u'CLM-121-024'},
                    '%s|CLM-121-025' % filename: {'B1': u'CLM-121-025'},
                    '%s|ControlSheet' % filename: {'B1': None},
                    '%s|Instructions' % filename: {'B1': None},
                    '%s|WorkbookLog' % filename: {'B1': u'Date'}}
        msg = 'Expected dictionary values error: parse all worksheets'
        self.assertDictEqual(received, expected, msg)

    def test_parse_sheets_skip_sheets_in_workbook(self):
        """Parse sheets: skip sheets in workbook.
        """
        # Given a workbook.
        file = os.path.join('baip_parser',
                            'tests',
                            'files',
                            'BA-CLM-CLM-121-CRDPathway-v04.xlsx')
        parser = baip_parser.Parser()
        parser.open(file)

        # And a list of cells to extract.
        parser.cells_to_extract = ['B1']

        # And a list of sheets to skip.
        parser.skip_sheets = ['ControlSheet',
                              'Instructions',
                              'WorkbookLog']

        # When I parse the workbook.
        received = parser.parse_sheets()

        # I should receive a populated dictionary structure.
        filename = 'BA-CLM-CLM-121-CRDPathway-v04.xlsx'
        expected = {'%s|AAA-000-001' % filename: {'B1': u'AAA-000-001'},
                    '%s|CLM-121-001' % filename: {'B1': u'CLM-121-001'},
                    '%s|CLM-121-002' % filename: {'B1': u'CLM-121-002'},
                    '%s|CLM-121-003' % filename: {'B1': u'CLM-121-003'},
                    '%s|CLM-121-004' % filename: {'B1': u'CLM-121-004'},
                    '%s|CLM-121-013' % filename: {'B1': u'CLM-121-013'},
                    '%s|CLM-121-014' % filename: {'B1': u'CLM-121-014'},
                    '%s|CLM-121-015' % filename: {'B1': u'CLM-121-015'},
                    '%s|CLM-121-016' % filename: {'B1': u'CLM-121-016'},
                    '%s|CLM-121-017' % filename: {'B1': u'CLM-121-017'},
                    '%s|CLM-121-018' % filename: {'B1': u'CLM-121-018'},
                    '%s|CLM-121-019' % filename: {'B1': u'CLM-121-019'},
                    '%s|CLM-121-020' % filename: {'B1': u'CLM-121-020'},
                    '%s|CLM-121-021' % filename: {'B1': u'CLM-121-021'},
                    '%s|CLM-121-022' % filename: {'B1': u'CLM-121-022'},
                    '%s|CLM-121-023' % filename: {'B1': u'CLM-121-023'},
                    '%s|CLM-121-024' % filename: {'B1': u'CLM-121-024'},
                    '%s|CLM-121-025' % filename: {'B1': u'CLM-121-025'}}
        msg = 'Expected dictionary values error: skipped worksheets'
        self.assertDictEqual(received, expected, msg)
