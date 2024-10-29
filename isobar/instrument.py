from typing import Any
from .timelines import Timeline


class InstrumentKeyword:
    def __init__(self, keyword: str, type: str, parameters: dict):
        self.keyword = keyword
        self.type = type
        self.parameters = parameters

class Instrument:
    def __init__(self, timeline, name: str = None, output_device = None):
        if output_device is None:
            output_device = timeline.output_device
        self.timeline: Timeline = timeline
        self.output_device = output_device
        self.defaults: dict = {}
        self.keywords = []
        self.name = name

    def set_defaults(self, **kwargs):
        self.defaults.update(**kwargs)

    def add_keyword(self, keyword: str, type: str, **kwargs):
        if type not in ["control", "attribute", "action", "param"]:
            raise ValueError("Invalid keyword type: %s" % type)
        keyword = InstrumentKeyword(keyword, type, parameters=kwargs)
        self.keywords.append(keyword)

    def __call__(self, **kwargs):
        values = self.defaults.copy()
        values.update(**kwargs)
        schedule_args = {}
        params = {}
        for schedule_arg in ["quantize", "count"]:
            if schedule_arg in values:
                schedule_args[schedule_arg] = values[schedule_arg]
                del values[schedule_arg]
        for keyword in self.keywords:
            if keyword.keyword in values:
                value = values[keyword.keyword]
                if keyword.type == "control":
                    self.timeline.schedule({
                        "type": "control",
                        "control": keyword.parameters["control"],
                        "value": value
                    }, count=1, output_device=self.output_device)
                elif keyword.type == "attribute":
                    obj = keyword.parameters["object"]
                    attr = keyword.parameters["attribute"]
                    self.timeline.schedule({
                        "type": "action",
                        "action": lambda: setattr(obj, attr, value)
                    }, count=1, output_device=self.output_device)
                elif keyword.type == "action":
                    action = keyword.parameters["action"]
                    self.timeline.schedule({
                        "type": "action",
                        "action": lambda action=action, value=value: action(value)
                    }, count=1, output_device=self.output_device)
                elif keyword.type == "param":
                    params[keyword.keyword] = value
                else:
                    raise ValueError("Invalid keyword type: %s" % keyword.type)
                del values[keyword.keyword]
        values["params"] = params
        print(values)
        
        self.timeline.schedule({
            **values
        }, name=self.name, **schedule_args)
    