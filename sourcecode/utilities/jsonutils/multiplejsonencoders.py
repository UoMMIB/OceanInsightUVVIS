# This file is part of the OceanInsightUVVIS library https://github.com/UoMMIB/OceanInsightUVVIS/
# Copyright (C) 2021 Alex Henderson (alex.henderson@manchester.ac.uk)
# SPDX-License-Identifier: MIT

import json


class MultipleJsonEncoders(json.JSONEncoder):
    """
    Class extending :class:`json.JSONEncoder` to handle multiple JSONEncoders of different types.

    Code taken directly from `stackoverflow`_ with a small modification. If a number of different encoders are passed
    to the constructor, the input is tested against each in turn.

    Example::

        >>> from utilities.jsonutils.multiplejsonencoders import MultipleJsonEncoders
        >>> encoder = MultipleJsonEncoders(JsonPintEncoder, JsonDatetimeEncoder)
        >>> jsonoutput = json.dumps(something_with_pint_or_datetime, indent=4, cls=encoder)

    .. _`stackoverflow`: https://stackoverflow.com/questions/65338261/combine-multiple-json-encoders
    """
    def __init__(self, *encoders):
        super().__init__()
        self.encoders = encoders
        self.args = ()
        self.kwargs = {}

    def default(self, obj):
        """
        Managed internally
        """
        for encoder in self.encoders:
            try:
                return encoder(*self.args, **self.kwargs).default(obj)
            except TypeError:
                pass
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        enc = json.JSONEncoder(*args, **kwargs)
        enc.default = self.default
        return enc
