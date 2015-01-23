# pylint: disable=R0902,R0903,R0904,C0111,W0142
"""The :class:`baip_parser.ParserConfig` is the configuration parser for
the GeoUtils ingest facility.

"""
__all__ = ["ParserConfig"]


from configa.config import Config
from configa.setter import (set_scalar,
                            set_list,
                            set_dict)


class ParserConfig(Config):
    """:class:`baip_parser.ParserConfig` class.

    """
    _thread_sleep = 2.0
    _inbound_dir = None
    _archive_dir = None
    _skip_sheets = []
    _cells_to_extract = []
    _cell_order = []
    _ignore_if_empty = []
    _cell_map = {}

    def __init__(self, config_file=None):
        """:class:`baip_parser.ParserConfig` initialisation.

        """
        Config.__init__(self, config_file)

    @property
    def thread_sleep(self):
        return self._thread_sleep

    @set_scalar
    def set_thread_sleep(self, value):
        pass

    @property
    def inbound_dir(self):
        return self._inbound_dir

    @set_scalar
    def set_inbound_dir(self, value):
        pass

    @property
    def archive_dir(self):
        return self._archive_dir

    @set_scalar
    def set_archive_dir(self, value):
        pass

    @property
    def skip_sheets(self):
        return self._skip_sheets

    @set_list
    def set_skip_sheets(self, value):
        pass

    @property
    def cells_to_extract(self):
        return self._cells_to_extract

    @set_list
    def set_cells_to_extract(self, value):
        pass

    @property
    def cell_order(self):
        return self._cell_order

    @set_list
    def set_cell_order(self, values):
        pass

    @property
    def ignore_if_empty(self):
        return self._ignore_if_empty

    @set_list
    def set_ignore_if_empty(self, values):
        pass

    @property
    def cell_map(self):
        return self._cell_map

    @set_dict
    def set_cell_map(self, values):
        pass

    def parse_config(self):
        """Read config items from the configuration file.

        """
        Config.parse_config(self)

        kwargs = [{'section': 'parse',
                   'option': 'thread_sleep',
                   'cast_type': 'float'},
                  {'section': 'parse',
                   'option': 'inbound_dir'},
                  {'section': 'parse',
                   'option': 'archive_dir'},
                  {'section': 'parse',
                   'option': 'skip_sheets',
                   'is_list': True},
                  {'section': 'parse',
                   'option': 'cells_to_extract',
                   'is_list': True},
                  {'section': 'parse',
                   'option': 'cell_order',
                   'is_list': True},
                  {'section': 'parse',
                   'option': 'ignore_if_empty',
                   'is_list': True}]

        for kwarg in kwargs:
            self.parse_scalar_config(**kwarg)

        del kwargs[:]
        kwargs = [{'section': 'cell_map',
                   'key_case': 'upper',
                   'is_list': True}]
        for kwarg in kwargs:
            self.parse_dict_config(**kwarg)
