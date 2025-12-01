from __future__ import annotations
from ..pattern import Pattern
from typing import Any

import logging
logger = logging.getLogger(__name__)

class Globals:
    """
    The Globals class encapsulates a namespace of global variables that can be accessed
    throughout isobar. This is particularly useful to alter parameters shared across the
    composition, which can then be accessed in patterns using the PGlobals class.
    """
    dict = {}
    on_change_callbacks = []
    sync_client = None
    sync_server = None

    @classmethod
    def get(cls, key):
        """
        Returns the value stored in `key`.
        Args:
            key: The key to query.

        Returns:
            The value, which can be of any type.

        Raises:
            KeyError: If the key does not exist in the globals dict.
        """
        if key not in Globals.dict:
            raise KeyError("Global variable does not exist: %s" % key)
        value = Globals.dict[key]
        return Pattern.value(value)

    @classmethod
    def set(cls,
            key,
            value: Any = None,
            quantize: float = None):
        """
        Set global parameters.
        Can either be used to set a single parameter or, if `key` is a dict, a dict of multiple
        parameters concurrently.

        Args:
            key: A key name, or a dict of key-value pairs.
            value: The value to set the key to
            quantize: If set, the time (in beats) to quantize the setting of the parameter to.
        """

        from ..timelines import Timeline

        timeline = Timeline.get_shared_timeline()

        if timeline is not None:
            if quantize is None:
                quantize = timeline.defaults.quantize

            if quantize is not None and quantize > 0:
                timeline._schedule_action(lambda: Globals.set(key, value, 0), quantize)
                return
        
        if isinstance(key, dict):
            for key, value in key.items():
                Globals.dict[key] = value
                for callback in Globals.on_change_callbacks:
                    callback(key, value)
        else:
            Globals.dict[key] = value
            for callback in Globals.on_change_callbacks:
                callback(key, value)

    @classmethod
    def add_on_change_callback(cls, callback):
        Globals.on_change_callbacks.append(callback)

    @classmethod
    def enable_interprocess_sync(cls):
        """
        If enabled, synchronises Globals state between all isobar processes running
        on the local machine. Requires rpyc for state connections.

        Raises:
            RuntimeError: If the required rpyc package is not installed.
        """
        try:
            from .sync import GlobalsSyncClient, GlobalsSyncServer
            try:
                cls.sync_client = GlobalsSyncClient()
                logger.info("Created GlobalsSyncClient")
            except ConnectionRefusedError:
                logger.info("Creating GlobalsSyncServer")
                cls.sync_server = GlobalsSyncServer()
                cls.sync_client = GlobalsSyncClient()
        except ModuleNotFoundError:
            raise ModuleNotFoundError("The rpyc package is required for inter-process sync: pip install rpyc")
