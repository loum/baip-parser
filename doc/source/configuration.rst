.. BAIP Parser Configuration Items

.. toctree::
       :maxdepth: 2

.. _config_items:

Configuration
=============

Conventions
-----------

All BAIP Parser configuration items are held within the ``parser.conf`` file.
By default, the ``baip-parser`` utility will look for ``parser.conf` at
``/etc/baip/conf``.  However, this can be overridden with the ``-c`` switch.

Configuration uses the Python :mod:`ConfigParser` module that follows
a structure similar to what you would find on Microsoft Windows INI files.

The configuration file consists of sections, led by a ``[section]`` header
and followed by a series of ``name: value`` entries.  For example::

    [section]
    name: value

``name: value`` entries that begin with a ``#`` are the default values for
that particular setting.  This means that the code is hardwired with
that value.  To override, simply uncomment the existing ``name: value``
pair and replace with your new value.  For example::

    [section]
    #name: value
    name: new value

Here, the original ``#name: value`` has been left in place so you have
a quick reference to the default value (but you don't have to do this
if you feel it clutters your view).

Configuration Items
-------------------

Thread Sleep
^^^^^^^^^^^^
``baip-parser`` supports daemonisation.  This means that you can set an
inbound directory and ``baip-parser`` will periodically poll that directory
for new files to process.

The period between polls can be controlled by the ``thread_sleep``
configuration setting::

    thread_sleep: 2.0

Default setting is 2 seconds.  Partial seconds are accepted.

Inbound Directory
^^^^^^^^^^^^^^^^^
``inbound_dir`` sets the source directory to read ingest files from::

    inbound_dir: /var/tmp/baip-parser

Excel File Name Filter
^^^^^^^^^^^^^^^^^^^^^^
``file_filter`` is the regular expression filtering to apply on files
within ``inbound_dir``.  Files matching ``file_filter`` will be returned::

    file_filter: [^~].*\.xlsx$

Skip Excel Worksheets
^^^^^^^^^^^^^^^^^^^^^
``skip_sheets`` is a comma-separated list of Excel Worksheet names that will
be ignored during processing::

    skip_sheets: ControlSheet,Instructions,WorkbookLog

Worksheet Cells to Extract
^^^^^^^^^^^^^^^^^^^^^^^^^^
``cells_to_extract`` are the Excel Worksheet cell values to extract::

    cells_to_extract: B1,B2

Output Cell Ordering
^^^^^^^^^^^^^^^^^^^^
``cell_order`` is a comma-separated list of cell ID ordering to apply to the
output::

    cell_order: B2,B1

Ignore Cells During Output Empty
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``ignore_if_empty`` is a comma-separated list of cell IDs which, in combination,
can be ignored during the output phase if their values are all empty
(or ``None``)::

    ignore_if_empty: B2,B1

Ignore Cell Value Length Threshold
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``cell_field_thresholds`` is a key/value arrangement that represents the
minimum cell value length (in characters) that will be accepted for output
display::

    [cell_field_thresholds]
    B2: 10

In the case above, if cell ``B2`` has a value character length of 10 or less
then it will be truncated and treated as an empty value.

Cell Alias Names
^^^^^^^^^^^^^^^^
``cell_map`` provides a key/value arrangement of cell IDs to human-readable
output header names.  Cell values can be displayed multiple times by providing
a comma-separated list of header names::

    [cell_map]
    B1: banana,grapes
    B2: apple

Field Maximum Output Length
^^^^^^^^^^^^^^^^^^^^^^^^^^^
``header_field_lengths`` provides a key/value arrangement of cell alias names
and their maximum value length of output::

    [header_field_lengths]
    apple: 5

In the case above, the apple header column will truncate the value to a
maximum of 5 characters.

.. note::
   Word boundaries are honored during truncation
