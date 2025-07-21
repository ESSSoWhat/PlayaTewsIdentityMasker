from typing import Union, List

from ...python import EventListener

from .CSWBase import ControlClient, ControlHost


class ControlViewer:
    """
    Control for viewing data without modification
    """
    class Config:
        def __init__(self, value=None):
            self.value = value

    class Client(ControlClient):
        def __init__(self):
            ControlClient.__init__(self)

            self._on_config_evl = EventListener()
            self._call_on_msg('_cfg', self._on_msg_config)

        def _on_msg_config(self, cfg):
            self._on_config_evl.call(cfg)

        def call_on_config(self, func_or_list):
            """
            Call when configuration changes
            """
            self._on_config_evl.add(func_or_list)

        def _on_reset(self):
            pass

    class Host(ControlHost):
        def __init__(self):
            ControlHost.__init__(self)

        def set_config(self, cfg : 'ControlViewer.Config'):
            """
            Set configuration
            """
            self._send_msg('_cfg', cfg) 