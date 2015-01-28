# pylint: disable=R0904,C0103
""":class:`baip_parser.Writer` tests.

"""
import unittest2
import tempfile
import datetime
import os

import baip_parser
from filer.files import remove_files


class TestWriter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._writer = baip_parser.Writer()
        cls._dir = tempfile.mkdtemp()

    def test_init(self):
        """Initialise a Writer object.
        """
        msg = 'Object is not an baip_parser.Writer'
        self.assertIsInstance(self._writer, baip_parser.Writer, msg)

    def test_write(self):
        """Write out the headers and content.
        """
        hdrs = ['JOB_ITEM_ID',
                'JOB_BU_ID',
                'CONNOTE_NBR',
                'BARCODE',
                'ITEM_NBR',
                'JOB_TS',
                'CREATED_TS',
                'NOTIFY_TS',
                'PICKUP_TS',
                'PIECES',
                'CONSUMER_NAME',
                'DP_CODE',
                'AGENT_NAME']
        self._writer.headers = hdrs

        data = [(20,
                 1,
                 '="TEST_REF_NOT_PROC"',
                 '="aged_parcel_unmatched"',
                 '="00393403250082030047"',
                 '="%s"' % self._now,
                 '="%s"' % self._now,
                 None,
                 None,
                 20,
                 'Con Sumertwenty',
                 'VIC999',
                 'VIC Test Newsagent 999'),
                (22,
                 1,
                 '="ARTZ061184"',
                 '="JOB_TEST_REF_NOT_PROC_PCKD_UP"',
                 '="00393403250082030048"',
                 '="%s"' % self._now,
                 '="%s"' % self._now,
                 None,
                 None,
                 22,
                 'Con Sumertwentytwo',
                 'VIC999',
                 'VIC Test Newsagent 999')]

        outfile = os.path.join(self._dir, 'test.csv')
        self._writer.outfile = outfile

        self._writer(data)

        # Clean up.
        remove_files(outfile)

    def test_truncate_row_empty_header_field_length(self):
        """Truncate row: empty header_field_length.
        """
        # Given an empty header_field_length
        old_header_field_lengths = self._writer.header_field_lengths
        self._writer.header_field_lengths = {}

        # And a list of headers to display
        old_headers = self._writer.headers
        hdrs = ['JOB_ITEM_ID',
                'AGENT_NAME']
        self._writer.headers = hdrs

        # And a data structure to output
        row = (20, 'VIC Test Newsagent 999')

        # When I truncate the row fields
        received = self._writer.truncate_row(row)

        # Then the original row should not be changed.
        expected = row
        msg = 'Row values have been altered'
        self.assertTupleEqual(received, expected, msg)

        # Clean up.
        self._writer.header_field_lengths = old_header_field_lengths
        self._writer.headers = old_headers

    def test_truncate_row(self):
        """Truncate row.
        """
        # Given an empty header_field_length
        old_header_field_lengths = self._writer.header_field_lengths
        self._writer.header_field_lengths = {'AGENT_NAME': 10}

        # And a list of headers to display
        old_headers = self._writer.headers
        hdrs = ['JOB_ITEM_ID',
                'AGENT_NAME']
        self._writer.headers = hdrs

        # And a data structure to output
        row = (20, 'VIC Test Newsagent 999')

        # When I truncate the row fields
        received = self._writer.truncate_row(row)

        # Then the original row should not be changed.
        expected = (20, 'VIC Test N')
        msg = 'Row values have not been truncated'
        self.assertTupleEqual(received, expected, msg)

        # Clean up.
        self._writer.header_field_length = old_header_field_lengths
        self._writer.headers = old_headers

    def test_truncate_row_word_boundary(self):
        """Truncate row: word boundary.
        """
        # Given an empty header_field_length
        old_header_field_lengths = self._writer.header_field_lengths
        self._writer.header_field_lengths = {'AGENT_NAME': 10}

        # And a list of headers to display
        old_headers = self._writer.headers
        hdrs = ['JOB_ITEM_ID',
                'AGENT_NAME']
        self._writer.headers = hdrs

        # And a data structure to output
        row = (20, 'VIC Test Newsagent 999')

        # When I truncate the row fields
        received = self._writer.truncate_row(row, word_boundary=True)

        # Then the original row should not be changed.
        expected = (20, 'VIC Test')
        msg = 'Row values have not been truncated: word boundary'
        self.assertTupleEqual(received, expected, msg)

        # Clean up.
        self._writer.header_field_lengths = old_header_field_lengths
        self._writer.headers = old_headers

    def test_write_truncated_rows(self):
        """Write out the headers and content: truncated rows.
        """
        # Given a list of headers
        old_headers = self._writer.headers
        hdrs = ['JOB_ITEM_ID',
                'AGENT_NAME']
        self._writer.headers = hdrs

        # And data to display
        data = [(20, 'VIC Test Newsagent 999')]

        # And a header column values to truncate
        old_header_field_lengths = self._writer.header_field_lengths
        self._writer.header_field_lengths = {'AGENT_NAME': 10}

        # When I nominate a file to write the output to
        outfile = os.path.join(self._dir, 'truncated.csv')
        self._writer.outfile = outfile
        self._writer(data)

        # Then the output file should contain truncted values.
        received_fh = open(outfile)
        received = received_fh.read().rstrip()
        received_fh.close()

        expected_file = os.path.join('baip_parser',
                                     'tests',
                                     'results',
                                     'truncated.csv')
        expected_fh = open(expected_file)
        expected = expected_fh.read().rstrip()
        expected_fh.close()

        msg = 'Truncated outfile contents mismatch'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._writer.headers = old_headers
        self._writer.header_field_lengths = old_header_field_lengths
        remove_files(outfile)

    def test_header_aliases(self):
        """Substitue header aliases.
        """
        hdrs_to_display = ['DP_CODE',
                           'AGENT_NAME',
                           'JOB_BU_ID',
                           'CONNOTE_NBR',
                           'ITEM_NBR',
                           'CONSUMER_NAME',
                           'PIECES']
        aliases = {'DP_CODE': ['Agent'],
                   'AGENT_NAME': ['Agent Name'],
                   'JOB_BU_ID': ['Business Unit'],
                   'CONNOTE_NBR': ['Connote'],
                   'ITEM_NBR': ['Item Nbr'],
                   'PIECES': ['Pieces']}

        received = self._writer.header_aliases(hdrs_to_display,
                                               aliases)
        expected = ['Agent',
                    'Agent Name',
                    'Business Unit',
                    'Connote',
                    'Item Nbr',
                    'CONSUMER_NAME',
                    'Pieces']
        msg = 'Header alias substitution error'
        self.assertListEqual(received, expected, msg)

    def test_header_aliases_duplicate_source_headers(self):
        """Substitue header aliases: duplicate source header.
        """
        # Given I have a list of headers to display
        hdrs_to_display = ['DP_CODE',
                           'AGENT_NAME',
                           'JOB_BU_ID',
                           'CONNOTE_NBR',
                           'ITEM_NBR',
                           'CONSUMER_NAME',
                           'PIECES',
                           'DP_CODE']
        # And a map of header aliases (with duplicates)
        aliases = {'DP_CODE': ['Agent', 'Second Agent'],
                   'AGENT_NAME': ['Agent Name'],
                   'JOB_BU_ID': ['Business Unit'],
                   'CONNOTE_NBR': ['Connote'],
                   'ITEM_NBR': ['Item Nbr'],
                   'PIECES': ['Pieces']}

        # When I substitute the source headers with their aliases
        received = self._writer.header_aliases(hdrs_to_display, aliases)

        # Then the header list should be updated accordingly
        expected = ['Agent',
                    'Agent Name',
                    'Business Unit',
                    'Connote',
                    'Item Nbr',
                    'CONSUMER_NAME',
                    'Pieces',
                    'Second Agent']
        msg = 'Header alias (duplicate source headers) substitution error'
        self.assertListEqual(received, expected, msg)

    def test_length_check_empty_thresholds(self):
        """Column length threshold check: empty thresholds.
        """
        # Given the header field thresholds are not set
        old_header_field_thresholds = self._writer.header_field_thresholds
        self._writer.header_field_thresholds = {}

        # And a list of headers to display
        old_headers = self._writer.headers
        hdrs = ['JOB_ITEM_ID',
                'AGENT_NAME']
        self._writer.headers = hdrs

        # And a data structure to output
        row = (20, 'VIC Test Newsagent 999')

        # When I check the row value lengths against the threshold
        received = self._writer.length_check(row)

        # Then the original row should be changed.
        expected = (20, 'VIC Test Newsagent 999')
        msg = 'Row values have been altered (no thresholds set)'
        self.assertTupleEqual(received, expected, msg)

        # Clean up.
        self._writer.header_field_thresholds = old_header_field_thresholds
        self._writer.headers = old_headers

    def test_length_check(self):
        """Column length threshold check.
        """
        # Given the header field thresholds are set
        old_header_field_thresholds = self._writer.header_field_thresholds
        self._writer.header_field_thresholds = {'AGENT_NAME': 22}

        # And a list of headers to display
        old_headers = self._writer.headers
        hdrs = ['JOB_ITEM_ID',
                'AGENT_NAME']
        self._writer.headers = hdrs

        # And a data structure to output
        row = (20, 'VIC Test Newsagent 999')

        # When I check the row value lengths against the threshold
        received = self._writer.length_check(row)

        # Then the original row should be changed.
        expected = (20, '')
        msg = 'Row values have been altered (thresholds set)'
        self.assertTupleEqual(received, expected, msg)

        # Clean up.
        self._writer.header_field_thresholds = old_header_field_thresholds
        self._writer.headers = old_headers

    def test_write_length_check(self):
        """Column value length check.
        """
        # Given a list of headers
        old_headers = self._writer.headers
        hdrs = ['JOB_ITEM_ID',
                'AGENT_NAME']
        self._writer.headers = hdrs

        # And data to display
        data = [(20, 'VIC Test Newsagent 999')]

        # And a header field value length thresholds set
        old_header_field_thresholds = self._writer.header_field_thresholds
        self._writer.header_field_thresholds = {'AGENT_NAME': 22}

        # When I nominate a file to write the output to
        outfile = os.path.join(self._dir, 'thresholds.csv')
        self._writer.outfile = outfile
        self._writer(data)

        # Then the output file should contain truncted values.
        received_fh = open(outfile)
        received = received_fh.read().rstrip()
        received_fh.close()

        expected_file = os.path.join('baip_parser',
                                     'tests',
                                     'results',
                                     'thresholds.csv')
        expected_fh = open(expected_file)
        expected = expected_fh.read().rstrip()
        expected_fh.close()

        msg = 'Field value threshold outfile contents mismatch'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._writer.headers = old_headers
        self._writer.header_field_thresholds = old_header_field_thresholds
        remove_files(outfile)

    @classmethod
    def tearDownClass(cls):
        del cls._writer
        os.removedirs(cls._dir)
        del cls._dir
