# pylint: disable=R0903,C0111,R0902
"""The :class:`baip_parser.ParserDaemon` supports the daemonisation
facility for the BAIP parser.

"""
__all__ = ["ParserDaemon"]

import os
import signal
import time
import re
import tempfile

import baip_parser
import daemoniser
from logga.log import log


class ParserDaemon(daemoniser.Daemon):
    """:class:`ParserDaemon`

    """
    dry = False
    batch = False
    conf = None
    inbound_dir = None

    def __init__(self,
                 pidfile,
                 filename=None,
                 inbound_dir=None,
                 dry=False,
                 batch=False,
                 conf=None):
        """:class:`ParserDaemon` initialisation.

        """
        super(ParserDaemon, self).__init__(pidfile=pidfile)

        self.filename = filename
        self._inbound_dir = inbound_dir
        self.dry = dry
        self.batch = batch
        self.conf = conf

        # If a file is provided on the command line, we want to
        # force a single iteration.
        if (self.filename is not None or self._inbound_dir is not None):
            self.batch = True

    @property
    def inbound_dir(self):
        return self._inbound_dir

    @inbound_dir.setter
    def inbound_dir(self, value):
        self._inbound_dir = value

    def _start(self, event):
        """Override the :meth:daemoniser.Daemon._start` method.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        self.process(event)

    def process(self, event, files_to_process=None):
        """Ingest thread wrapper.  Each call to this method is
        effectively an ingest process.

        **Args:**
            *event*: a :mod:`threading.Event` based internal semaphore
            that can be set via the :mod:`signal.signal.SIGTERM` signal
            event to perform a function within the running proess.

        **Kwargs:**
            *files_to_process* override the file to process (will bypass
            a file system search)

        """
        # Check if we process the argument or the attribute filename
        # value.
        if files_to_process is None:
            if self.filename is not None:
                files_to_process = [self.filename]
            else:
                filter = self.conf.file_filter
                files_to_process = self.source_files(file_filter=filter)

        while not event.isSet():
            results = []
            for file_to_process in files_to_process:
                log.info('Processing file: %s' % file_to_process)
                parser = baip_parser.Parser()
                parser.open(file_to_process)
                parser.cells_to_extract = self.conf.cells_to_extract
                parser.skip_sheets = self.conf.skip_sheets

                results.append(parser.parse_sheets())

            self.dump(results, self.dry)

            if self.dry:
                print('Dry run iteration complete')
                event.set()
            elif self.batch:
                print('Batch run iteration complete')
                event.set()
            else:
                time.sleep(self.conf.thread_sleep)

    def source_files(self, directory=None, file_filter=None):
        """Checks inbound directory (defined by the
        :attr:`geoutils.IngestConfig.inbound_dir` config option) for valid
        NITF files to be processed.

        **Returns:**
            list of matching files

        """
        files_to_process = []

        directory_to_check = self.conf.inbound_dir
        if directory is not None:
            directory_to_check = directory
        elif self.inbound_dir is not None:
            directory_to_check = self.inbound_dir
            self.batch = True

        reg_c = None
        if file_filter is not None:
            reg_c = re.compile(file_filter)

        log.debug('Sourcing files at "%s" with filter "%s"' %
                  (directory_to_check, file_filter))
        for dirpath, dirnames, filenames in os.walk(directory_to_check):
            for filename in filenames:
                if reg_c is not None:
                    reg_match = reg_c.match(os.path.basename(filename))
                    if not reg_match:
                        continue

                files_to_process.append(os.path.join(dirpath, filename))

        return files_to_process

    def dump(self, results, dry=False):
        """Present the results data structure into a format that can be
        readily output by the :class:`baip_parser.Writer`.

        **Args:**
            *results*: the data to write

            *dry*: only report, do not execute

        """
        data = []
        for result in results:
            for key, value in result.iteritems():
                reduced_values = self.length_check(value)

                if not self.skip_set(reduced_values):
                    line_item = []
                    for cell in self.conf.cell_order:
                        tmp_value = reduced_values[cell]

                        if isinstance(tmp_value, unicode):
                            # Remove the non-breaking hyphen.
                            # These really should be put in as a
                            # configuration item.  Fugly ...
                            tmp_value = tmp_value.replace(u'\u2011', '-')
                            tmp_value = tmp_value.replace(u'\u00B1', '-')
                            tmp_value = tmp_value.replace(u'\u2019', '-')

                        line_item.append(tmp_value)

                    data.append(tuple(line_item))

        writer = baip_parser.Writer()
        outfile_obj = tempfile.NamedTemporaryFile(suffix='.csv')
        outfile = outfile_obj.name
        outfile_obj.close()
        writer.outfile = outfile
        writer.header_field_lengths = self.conf.header_field_lengths
        writer.cell_field_thresholds = self.conf.cell_field_thresholds
        writer.headers = writer.header_aliases(self.conf.cell_order,
                                               self.conf.cell_map)
        if not dry:
            writer.write(data, word_boundary=True)
        else:
            log.info('Skipping dump in dry mode')

        return outfile

    def skip_set(self, data):
        """Check the dictionary based *data* structure and see if we
        can fiter out keys with empty values.

        If no fields are set to be skipped if empty, then the skip check
        ignored

        **Args:**
            *data:* the input dictionary data structure to check

        **Returns:**
            Boolean ``True`` if data structure should be skipped.
            Boolean ``False`` otherwise

        """
        log.debug('Checking if row can be skipped ...')
        skip = True

        for empty_field in self.conf.ignore_if_empty:
            if data.get(empty_field) is not None:
                skip = False
                log.debug('setting skip to: %s' % skip)
                break

        if skip and not(len(self.conf.ignore_if_empty)):
            log.debug('No fields to check have been defined')
            skip = False

        log.debug('Can row: %s be skipped? %s' % (data, skip))

        return skip

    def length_check(self, data):
        """Determines the field value length and checks against the
        column threshold to see whether the column value is acceptable.

        Obtains the field length from the :attr:`cell_field_lengths`
        configuration setting.

        If the column value length threshold is not met, then the value
        will be replaced with ``None``.

        **Args:**
            *data*: dictionary structure representing the a cell value
            parsed in the form::

                {<cell>: <value>}

        **Returns:**
            the updated (if length threshold is breached) dictionary
            values

        """
        new_data = dict(data)

        for cell, length in self.conf.cell_field_thresholds.iteritems():
            if new_data.get(cell) is not None:
                # We have a value.  Check the length.
                if len(new_data.get(cell)) <= length:
                    new_data[cell] = None

        return new_data
