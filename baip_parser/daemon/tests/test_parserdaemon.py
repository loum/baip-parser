# pylint: disable=R0904,C0103
""":class:`baip_parser.ParserDaemon` tests.

"""
import unittest2
import os

import baip_parser
from filer.files import remove_files


class TestParserDaemon(unittest2.TestCase):
    """:class:`baip_parser.ParserDaemon` test cases.
    """
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        cls._conf = baip_parser.ParserConfig()

    def setUp(self):
        self._parserd = baip_parser.ParserDaemon(pidfile=None,
                                                 conf=self._conf)

    def test_init(self):
        """Initialise a ParserDaemon object.
        """
        msg = 'Object is not a baip_parser.ParserDaemon'
        self.assertIsInstance(self._parserd, baip_parser.ParserDaemon, msg)

    def test_source_files_valid_directory_no_filter(self):
        """Walk directory for files: no filter.
        """
        # Given a source directory that contains files.
        parserd = baip_parser.ParserDaemon(pidfile=None,
                                           conf=baip_parser.ParserConfig())
        source_dir = os.path.join('baip_parser',
                                  'daemon',
                                  'tests',
                                  'files',
                                  'BA_reports')

        # When sourcing files with no filtering.
        received = parserd.source_files(directory=source_dir)
        expected = [os.path.join(source_dir,
                                 'CLM1.2',
                                 'BA-CLM-CLM-122-CRDPathway-v04.xlsx'),
                    os.path.join(source_dir,
                                 'CLM1.2',
                                 'BA-CLM-CLM-123-CRDPathway-v04.xlsx'),
                    os.path.join(source_dir,
                                 'CLM1.2',
                                 '~$BA-CLM-CLM-123-CRDPathway-v04.xlsx'),
                    os.path.join(source_dir,
                                 'CLM1.2',
                                 'BA-CLM-CLM-121-CRDPathway-v04.xlsx'),
                    os.path.join(source_dir,
                                 'CLM1.2',
                                 'BA-CLM-CLM-120-CoalAvailability-v28.docx'),
                    os.path.join(source_dir,
                                 'NAM1.3',
                                 'BA-NIC-NAM-130-WaterDependentAssetRegister-AssetList-20141118.xlsx'),
                    os.path.join(source_dir,
                                 'NAM1.3',
                                 'BA-NIC-NAM-130-CoverPrelims-v14.docx'),
                    os.path.join(source_dir,
                                 'M02',
                                 'BA-M02-AS-v07.xlsx'),
                    os.path.join(source_dir,
                                 'M02',
                                 'BA-M02-AS-001-CoverPrelims-v34.docx')]
        msg = 'Sourcing files with no filter error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_source_files_valid_directory_with_xlsx_filter(self):
        """Walk directory for files: with xlsx filter.
        """
        # Given a source directory that contains files.
        source_dir = os.path.join('baip_parser',
                                  'daemon',
                                  'tests',
                                  'files',
                                  'BA_reports')

        # When sourcing files with xlsx filtering.
        received = self._parserd.source_files(directory=source_dir,
                                              file_filter='[^~].*\.xlsx$')
        expected = [os.path.join(source_dir,
                                 'CLM1.2',
                                 'BA-CLM-CLM-122-CRDPathway-v04.xlsx'),
                    os.path.join(source_dir,
                                 'CLM1.2',
                                 'BA-CLM-CLM-123-CRDPathway-v04.xlsx'),
                    os.path.join(source_dir,
                                 'CLM1.2',
                                 'BA-CLM-CLM-121-CRDPathway-v04.xlsx'),
                    os.path.join(source_dir,
                                 'NAM1.3',
                                 'BA-NIC-NAM-130-WaterDependentAssetRegister-AssetList-20141118.xlsx'),
                    os.path.join(source_dir,
                                 'M02',
                                 'BA-M02-AS-v07.xlsx')]
        msg = 'Sourcing files with xlsx filter error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_start_dry_run(self):
        """ParserDaemon dry run.
        """
        # Given a filename
        test_file = os.path.join('baip_parser',
                                 'tests',
                                 'files',
                                 'BA-CLM-CLM-121-CRDPathway-v04.xlsx')
        old_file = self._parserd.filename
        self._parserd.filename = test_file

        # and skip sheets are set
        old_skip_sheets = self._parserd.conf.skip_sheets
        self._parserd.conf.skip_sheets = ['ControlSheet',
                                          'Instructions',
                                          'WorkbookLog']

        # and cells to extract is set
        old_cells_to_extract = self._parserd.conf.cells_to_extract
        self._parserd.conf.cells_to_extract = ['B1', 'B10']

        # and cell ordering is set
        old_cell_order = self._parserd.conf.cells_to_extract
        self._parserd.conf.cell_order = ['B10', 'B1']

        # and the header aliases have been set.
        old_cell_map = self._parserd.conf.cell_map
        self._parserd.conf.cell_map = {'B10': ['name'],
                                       'B1': ['sheet_name']}

        # and I run the parser daemon in dry mode
        old_dry = self._parserd.dry
        self._parserd.dry = True
        self._parserd._start(self._parserd.exit_event)

        # Clean up.
        self._parserd.dry = old_dry
        self._parserd.filename = old_file
        self._parserd.conf.skip_sheets = old_skip_sheets
        self._parserd.conf.cells_to_extract = old_cells_to_extract
        self._parserd.conf.cell_order = old_cell_order
        self._parserd.conf.cell_map = old_cell_map
        self._parserd.exit_event.clear()

    def test_start_dry_run_with_inbound_directory(self):
        """ParserDaemon dry run: with inbound directory.
        """
        # Given an inbound directory
        inbound_dir = os.path.join('baip_parser', 'tests', 'files')
        old_inbound_dir = self._parserd.inbound_dir
        self._parserd.inbound_dir = inbound_dir

        # and a non-opened excel file filter
        old_file_filter = self._parserd.conf.file_filter
        self._parserd.conf.file_filter = '[^~].*\.xlsx'

        # and skip sheets are set
        old_skip_sheets = self._parserd.conf.skip_sheets
        self._parserd.conf.skip_sheets = ['ControlSheet',
                                          'Instructions',
                                          'WorkbookLog',
                                          'Description',
                                          'Water-dependent asset register',
                                          'Asset list',
                                          'pivot table',
                                          'AAA-000-001']

        # And cells to extract is set
        old_cells_to_extract = self._parserd.conf.cells_to_extract
        self._parserd.conf.cells_to_extract = ['B1',
                                               'B2',
                                               'B3',
                                               'B4',
                                               'B6',
                                               'B8',
                                               'B9',
                                               'B10',
                                               'B11']

        # And cell ordering is set
        old_cell_order = self._parserd.conf.cells_to_extract
        self._parserd.conf.cell_order = ['B10',
                                         'B1',
                                         'B2',
                                         'B3',
                                         'B4',
                                         'B6',
                                         'B8',
                                         'B9',
                                         'B10',
                                         'B11']

        # And the header aliases have been set.
        old_cell_map = self._parserd.conf.cell_map
        self._parserd.conf.cell_map = {'B1': ['field_element_number'],
                                       'B2': ['field_data_source'],
                                       'B3': ['field_image_source'],
                                       'B4': ['field_other_source'],
                                       'B6': ['field_updated_by'],
                                       'B8': ['field_element_type'],
                                       'B9': ['field_figure_table_number'],
                                       'B10': ['name', 'description'],
                                       'B11': ['field_alt_text']}

        # And empty fields to skip have been set
        old_ignore_if_empty = self._parserd.conf.ignore_if_empty
        self._parserd.conf.ignore_if_empty = ['B10',
                                              'B2',
                                              'B3',
                                              'B4',
                                              'B6',
                                              'B8',
                                              'B9',
                                              'B11']

        # And I run the parser daemon in dry mode
        old_dry = self._parserd.dry
        self._parserd.dry = True
        self._parserd._start(self._parserd.exit_event)

        # Clean up.
        self._parserd.dry = old_dry
        self._parserd.inbound_dir = old_inbound_dir
        self._parserd.conf.file_filter = old_file_filter
        self._parserd.conf.skip_sheets = old_skip_sheets
        self._parserd.conf.cells_to_extract = old_cells_to_extract
        self._parserd.conf.cell_order = old_cell_order
        self._parserd.conf.cell_map = old_cell_map
        self._parserd.conf.ignore_if_empty = old_ignore_if_empty
        self._parserd.exit_event.clear()

    def test_start_dry_run_with_inbound_directory_headers_truncated(self):
        """ParserDaemon dry run: with inbound directory.
        """
        # Given an inbound directory
        inbound_dir = os.path.join('baip_parser', 'tests', 'files')
        old_file = self._parserd.inbound_dir
        self._parserd.inbound_dir = inbound_dir

        # and skip sheets are set
        old_skip_sheets = self._parserd.conf.skip_sheets
        self._parserd.conf.skip_sheets = ['ControlSheet',
                                          'Instructions',
                                          'WorkbookLog',
                                          'Description',
                                          'Water-dependent asset register',
                                          'Asset list',
                                          'pivot table',
                                          'AAA-000-001']

        # And cells to extract is set
        old_cells_to_extract = self._parserd.conf.cells_to_extract
        self._parserd.conf.cells_to_extract = ['B1',
                                               'B2',
                                               'B3',
                                               'B4',
                                               'B6',
                                               'B8',
                                               'B9',
                                               'B10',
                                               'B11']

        # And cell ordering is set
        old_cell_order = self._parserd.conf.cells_to_extract
        self._parserd.conf.cell_order = ['B10',
                                         'B1',
                                         'B2',
                                         'B3',
                                         'B4',
                                         'B6',
                                         'B8',
                                         'B9',
                                         'B10',
                                         'B11']

        # And the header aliases have been set.
        old_cell_map = self._parserd.conf.cell_map
        self._parserd.conf.cell_map = {'B1': ['field_element_number'],
                                       'B2': ['field_data_source'],
                                       'B3': ['field_image_source'],
                                       'B4': ['field_other_source'],
                                       'B6': ['field_updated_by'],
                                       'B8': ['field_element_type'],
                                       'B9': ['field_figure_table_number'],
                                       'B10': ['name', 'description'],
                                       'B11': ['field_alt_text']}

        # And empty fields to skip have been set
        old_ignore_if_empty = self._parserd.conf.ignore_if_empty
        self._parserd.conf.ignore_if_empty = ['B10',
                                              'B2',
                                              'B3',
                                              'B4',
                                              'B6',
                                              'B8',
                                              'B9',
                                              'B11']

        # And header field lengths have been set
        old_header_field_lengths = self._parserd.conf.header_field_lengths
        self._parserd.conf.header_field_lengths = {'name': 10}

        # And I run the parser daemon in dry mode
        old_dry = self._parserd.dry
        self._parserd.dry = True
        self._parserd._start(self._parserd.exit_event)

        # Clean up.
        self._parserd.dry = old_dry
        self._parserd.filename = old_file
        self._parserd.conf.skip_sheets = old_skip_sheets
        self._parserd.conf.cells_to_extract = old_cells_to_extract
        self._parserd.conf.cell_order = old_cell_order
        self._parserd.conf.cell_map = old_cell_map
        self._parserd.conf.ignore_if_empty = old_ignore_if_empty
        self._parserd.conf.header_field_lengths = old_header_field_lengths
        self._parserd.exit_event.clear()

    def test_start_dry_run_with_inbound_directory_header_thresholds(self):
        """ParserDaemon dry run: with inbound directory (header thresholds).
        """
        # Given an inbound directory
        inbound_dir = os.path.join('baip_parser', 'tests', 'files')
        old_file = self._parserd.inbound_dir
        self._parserd.inbound_dir = inbound_dir

        # and skip sheets are set
        old_skip_sheets = self._parserd.conf.skip_sheets
        self._parserd.conf.skip_sheets = ['ControlSheet',
                                          'Instructions',
                                          'WorkbookLog',
                                          'Description',
                                          'Water-dependent asset register',
                                          'Asset list',
                                          'pivot table',
                                          'AAA-000-001']

        # And cells to extract is set
        old_cells_to_extract = self._parserd.conf.cells_to_extract
        self._parserd.conf.cells_to_extract = ['B1',
                                               'B2',
                                               'B3',
                                               'B4',
                                               'B6',
                                               'B8',
                                               'B9',
                                               'B10',
                                               'B11']

        # And cell ordering is set
        old_cell_order = self._parserd.conf.cells_to_extract
        self._parserd.conf.cell_order = ['B10',
                                         'B1',
                                         'B2',
                                         'B3',
                                         'B4',
                                         'B6',
                                         'B8',
                                         'B9',
                                         'B10',
                                         'B11']

        # And the header aliases have been set.
        old_cell_map = self._parserd.conf.cell_map
        self._parserd.conf.cell_map = {'B1': ['field_element_number'],
                                       'B2': ['field_data_source'],
                                       'B3': ['field_image_source'],
                                       'B4': ['field_other_source'],
                                       'B6': ['field_updated_by'],
                                       'B8': ['field_element_type'],
                                       'B9': ['field_figure_table_number'],
                                       'B10': ['name', 'description'],
                                       'B11': ['field_alt_text']}

        # And empty fields to skip have been set
        old_ignore_if_empty = self._parserd.conf.ignore_if_empty
        self._parserd.conf.ignore_if_empty = ['B10',
                                              'B2',
                                              'B3',
                                              'B4',
                                              'B6',
                                              'B8',
                                              'B9',
                                              'B11']

        # And header field thresholds have been set
        old_header_field_thresholds = self._parserd.conf.header_field_thresholds
        self._parserd.conf.header_field_thresholds = {'name': 200}

        # And I run the parser daemon in dry mode
        old_dry = self._parserd.dry
        self._parserd.dry = True
        self._parserd._start(self._parserd.exit_event)

        # Clean up.
        self._parserd.dry = old_dry
        self._parserd.filename = old_file
        self._parserd.conf.skip_sheets = old_skip_sheets
        self._parserd.conf.cells_to_extract = old_cells_to_extract
        self._parserd.conf.cell_order = old_cell_order
        self._parserd.conf.cell_map = old_cell_map
        self._parserd.conf.ignore_if_empty = old_ignore_if_empty
        self._parserd.conf.header_field_lengths = old_header_field_thresholds
        self._parserd.exit_event.clear()

    def test_dump(self):
        """Write out the results to file.
        """
        # Given I want to write out my parsed data into CSV format
        results = [{
            'CLM-121-003': {
                'B1': 'CLM-121-003',
                'B10': u'Isopach (thickness) map of Walloon Coal Measures (Ingram and Robinson, 1996) and comparison with thickness of Walloon Coal Measures recorded at coal seam gas, coal exploration, petroleum exploration and stratigraphic wells in the Clarence-Moreton bioregion'},
            'CLM-121-002': {
                'B1': 'CLM-121-002',
                'B10': u'Identified coal resources and operating and historical coal mines in the Clarence-Moreton bioregion (additional historical coal mines in Queensland that are not included in the OZMIN database are described in Cameron, 1970)'
            }
        }]

        # and cells to extract is set
        old_cells_to_extract = self._parserd.conf.cells_to_extract
        self._parserd.conf.cells_to_extract = ['B1', 'B10']

        # and cell ordering is set
        old_cell_order = self._parserd.conf.cells_to_extract
        self._parserd.conf.cell_order = ['B10', 'B1']

        # and the header aliases have been set.
        old_cell_map = self._parserd.conf.cell_map
        self._parserd.conf.cell_map = {'B10': ['name'],
                                       'B1': ['sheet_name']}

        # When I dump results to file
        outfile = self._parserd.dump(results)

        # Then a CSV file should be produced
        msg = 'Dump CSV file was not produced'
        self.assertTrue(os.path.exists(outfile), msg)

        # And the content should match
        outfile_fh = open(outfile)
        received = outfile_fh.read().rstrip()

        results_file = os.path.join('baip_parser',
                                    'daemon',
                                    'tests',
                                    'results',
                                    'dump_results_01.csv')
        results_fh = open(results_file)
        expected = results_fh.read().rstrip()
        msg = 'Dump CSV content mis-match'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._parserd.conf.cell_order = old_cell_order
        self._parserd.conf.cells_to_extract = old_cells_to_extract
        self._parserd.conf.cell_order = old_cell_order
        self._parserd.conf.cell_map = old_cell_map
        remove_files(outfile)

    def test_skip_set_single_value(self):
        """Skip set of empty values: single value.
        """
        # Given a list of fields to ignore if empty
        old_ignore_if_empty = self._parserd.conf.ignore_if_empty
        self._parserd.conf.ignore_if_empty = ['B1', 'B2']

        # And a parsed data structure has a single non-empty field
        result = {
            'B1': u'CLM-121-001',
            'B2': None,
        }

        # When I filter out empty values
        received = self._parserd.skip_set(result)

        # The data structure should be flagged to not skip
        msg = 'Filtered data structure (single empty value) error'
        self.assertFalse(received, msg)

        # Clean up.
        self._parserd.conf.ignore_if_empty = old_ignore_if_empty

    def test_skip_set_all_values_not_empty(self):
        """Skip set of empty values: all values not empty.
        """
        # Given a list of fields to ignore if empty
        old_ignore_if_empty = self._parserd.conf.ignore_if_empty
        self._parserd.conf.ignore_if_empty = ['B1', 'B2']

        # And a parsed data strucutre
        result = {
            'B1': u'CLM-121-001',
            'B2': 'not_empty',
        }

        # When I filter out empty values
        received = self._parserd.skip_set(result)

        # The data structure should be flagged to not skip
        msg = 'Filtered data structure (no empty values) error'
        self.assertFalse(received, msg)

        # Clean up.
        self._parserd.conf.ignore_if_empty = old_ignore_if_empty

    def test_skip_set_all_values_empty(self):
        """Skip set of empty values: all values empty.
        """
        # Given a list of fields to ignore if empty
        old_ignore_if_empty = self._parserd.conf.ignore_if_empty
        self._parserd.conf.ignore_if_empty = ['B1', 'B2']

        # And a parsed data strucutre
        result = {
            'B1': None,
            'B2': None,
        }

        # When I filter out empty values
        received = self._parserd.skip_set(result)

        # The data structure should be flagged to skip
        msg = 'Filtered data structure (no empty values) error'
        self.assertTrue(received, msg)

        # Clean up.
        self._parserd.conf.ignore_if_empty = old_ignore_if_empty

    def test_skip_set_no_field_defined(self):
        """Skip set of empty values: no fields defined.
        """
        # Given an empty list of fields to ignore if value is empty
        old_ignore_if_empty = self._parserd.conf.ignore_if_empty
        self._parserd.conf.ignore_if_empty = []

        # And a parsed data structure with no values
        result = {
            'B1': None,
            'B2': None,
        }

        # When I filter out empty values
        received = self._parserd.skip_set(result)

        # The data structure should be flagged to not skip
        msg = 'Filtered data structure (no defined fields) error'
        self.assertFalse(received, msg)

        # Clean up.
        self._parserd.conf.ignore_if_empty = old_ignore_if_empty

    def tearDown(self):
        del self._parserd

    @classmethod
    def tearDownClass(cls):
        del cls._conf
