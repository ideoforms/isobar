from __future__ import annotations

import inspect
import traceback

from .event import Event
from ...pattern import Pattern
from ...constants import EVENT_TYPE_ACTION, EVENT_ACTION, EVENT_ACTION_ARGS

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..track import Track


class ActionEvent(Event):
    def __init__(self, event_values: dict, track: Track):
        super().__init__(event_values, track)

        self.type = EVENT_TYPE_ACTION
        self.action = event_values[EVENT_ACTION]
        self.args = {}
        if EVENT_ACTION_ARGS in event_values:
            self.args = dict((key, Pattern.value(value)) for key, value in event_values[EVENT_ACTION_ARGS].items())

    def perform(self) -> bool:
        try:
            fn = self.action
            try:
                fn_params = inspect.signature(fn).parameters
                for key in self.args.keys():
                    if key not in fn_params:
                        raise Exception("Named argument not found in callback args: %s" % key)
            except ValueError:
                #------------------------------------------------------------------------
                # inspect.signature does not work on cython/pybind11 bindings, and
                # raises a ValueError. In these cases, simply pass the arguments
                # without validation.
                #------------------------------------------------------------------------
                pass
            self.action(**self.args)
            return True
        except StopIteration:
            raise StopIteration()
        except Exception as e:
            print("Exception when handling scheduled action: %s" % e)
            traceback.print_exc()
            return False