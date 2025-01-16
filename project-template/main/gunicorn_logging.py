import collections
import datetime
import json
import os
import traceback


# Log to stdout.
accesslog = "-"
errorlog = "-"


class JsonFormatter:
    def __init__(self, fields, *args, **kwargs):
        self.fields = [
            (key, val)
            for piece in fields.split(" ")
            for (key, val) in (piece.split(":"),)
        ]

    def format(self, record):
        rtn = collections.OrderedDict()
        for key, field in self.fields:
            if field == "time":
                val = datetime.datetime.utcnow().isoformat()
            elif field == "app":
                val = "gunicorn"
            elif field == "project":
                val = os.environ.get("PROJECT_NAME", "bedrock")
            elif field == "message":
                val = record.getMessage()
            elif field == "exc_info":
                val = getattr(record, field, None)
                if val is not None:
                    val = "".join(traceback.format_exception(val[0], value=val[1], tb=val[2]))
            else:
                val = getattr(record, field, None)
            rtn[key] = val
        return json.dumps(rtn)


# Ensure the two named loggers that Gunicorn uses are configured to use the custom
# JSON formatter.
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        }
    },
    "formatters": {
        "console": {
            "format": "level:levelname time:time app:app project:project channel:name message:message exception:exc_info",
            # Coopting the above string to specify the fields and ordering of the JSON
            # emitted by this class
            "class": "main.gunicorn_logging.JsonFormatter",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING"
    },
    "loggers": {
        "gunicorn.access": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "gunicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
