# pylint: disable=R0903,C0111,R0902
"""The :class:`baip_parser.Writer` supports the CSV to file output

"""
__all__ = [
    "Writer",
]
import csv

from logga.log import log


class Writer(object):
    """
    .. attribute:: outfile

        name of the output file to write to

    .. attribute:: headers

        name and order of the column headers

    .. attribute:: write_out_headers

        write the column names in the first row (default ``True``)

    .. attribute:: header_field_lengths

        dictionary of header keys and associated field lengths

    .. attribute:: header_field_thresholds

        dictionary of header keys and associated minimum field length
        thresholds

    """
    _outfile = None
    _headers = []
    _write_out_headers = True
    _header_field_lengths = {}
    _header_field_thresholds = {}

    def __init__(self, outfile=None):
        """Writer initialiser.

        """
        if outfile is not None:
            self._outfile = outfile

    def __call__(self, data):
        self.write(data)

    @property
    def outfile(self):
        return self._outfile

    @outfile.setter
    def outfile(self, value=None):
        self._outfile = value

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, values=None):
        del self._headers[:]
        self._headers = []

        if values is not None and isinstance(values, list):
            self._headers.extend(values)

    @property
    def write_out_headers(self):
        return self._write_out_headers

    @write_out_headers.setter
    def write_out_headers(self, value=False):
        self._write_out_headers = value

    @property
    def header_field_lengths(self):
        return self._header_field_lengths

    @header_field_lengths.setter
    def header_field_lengths(self, values):
        self._header_field_lengths.clear()

        if values is not None and isinstance(values, dict):
            self._header_field_lengths = values

    @property
    def header_field_thresholds(self):
        return self._header_field_thresholds

    @header_field_thresholds.setter
    def header_field_thresholds(self, values):
        self._header_field_thresholds.clear()

        if values is not None and isinstance(values, dict):
            self._header_field_thresholds = values

    def write(self, data, word_boundary=False):
        """Class callable that writes list of tuple values in *data*.

        **Args:**
            *data*: list of tuples to write out

            *word_boundary*: if ``True``, attempts to tidy-up a truncated
            string by removing the last word in the sentence

        """
        log.debug('Preparing "%s" for output' % self.outfile)
        fh = open(self.outfile, 'wb')

        writer = csv.DictWriter(fh, delimiter=',', fieldnames=self.headers)
        if self.write_out_headers:
            writer.writerow(dict((fn, fn) for fn in self.headers))

        log.debug('Received %d records to write' % len(data))
        counter = 0
        for row in data:
            counter += 1
            row = self.truncate_row(row, word_boundary)
            row = self.length_check(row)
            log.debug('Writing out row: %s' % str(row))
            writer.writerow(dict(zip(self.headers, row)))

        fh.close()
        log.debug('%d records written to "%s"' % (counter, self.outfile))

    def truncate_row(self, row, word_boundary=False):
        """Check if the field length is flagged as having a maximum
        value.  If so, the field will be truncated.

        Obtains the field length from the :attr:`header_field_lengths`
        attribute.

        **Args:**
            *row*: tuple structure representing the a line row to output

            *word_boundary*: if ``True``, will truncate the string
            on the last word boundary (drops off the last word)

        """
        truncated_row = []

        index = 0
        for value in row:
            header = self.headers[index]
            if self.header_field_lengths.get(header) is not None:
                field_length = self.header_field_lengths.get(header)
                if len(value) > field_length:
                    log.debug('Truncate header "%s" value to length: %d' %
                              (header, field_length))
                    value = value[:field_length]

                    if word_boundary:
                        # Tidy up around word boundary - drop the last word.
                        value = value.rsplit(' ', 1)[0]

                    log.debug('New header value: "%s"' % value)

            truncated_row.append(value)

            index += 1

        return tuple(truncated_row)

    def length_check(self, row):
        """Determines the field value length and checks against the
        column threshold to see whether the column value is acceptable.

        Obtains the field length from the :attr:`header_field_lengths`
        attribute.

        If the column value length threshold is not met, then the value
        will be replaced by the empty string.

        **Args:**
            *row*: tuple structure representing the a line row to output

        """
        new_row = []

        index = 0
        for value in row:
            header = self.headers[index]
            if self.header_field_thresholds.get(header) is not None:
                field_threshold = self.header_field_thresholds.get(header)
                log.debug('Header "%s" length threshold: %d' %
                          (header, field_threshold))
                if len(value) <= field_threshold:
                    value = str()
                    log.debug('New header "%s" value: "%s"' %
                              (header, value))

            new_row.append(value)

            index += 1

        return tuple(new_row)

    def header_aliases(self, headers_displayed, header_aliases):
        """Substitute the raw header_values in *headers_displayed* with
        the aliases defined in *header_alises*.

        **Args:**
            *headers_displayed*: headers to display

            *header_aliases*: dictionary structure that maps the raw
            header value to the alias.  Typical form is::

                {'AGENT_NAME': ['Agent Name'],
                 ...}

            values are provided as a list of alias names so that duplicate
            alias names can be provided for the same source header name.
            For example::

                {'AGENT_NAME': ['Agent Name', 'Agent Name 2']}

            would replace the first occurrence of ``AGENT_NAME`` with
            ``Agent Name`` and the second occurence with ``Agent Name 2``.

        """
        log.debug('Substituting header aliases as per: "%s"' %
                  str(header_aliases))

        local_header_aliases = dict(header_aliases)

        new_header_list = []
        for i in headers_displayed:
            log.debug('Substituting alias for header "%s"' % i)
            aliases = local_header_aliases.get(i)
            if aliases is not None:
                alias = aliases.pop(0)
                log.debug('Header "%s" alias is "%s"' % (i, alias))
                new_header_list.append(alias)
            else:
                log.debug('Header "%s" has no alias' % i)
                new_header_list.append(i)

        return new_header_list
