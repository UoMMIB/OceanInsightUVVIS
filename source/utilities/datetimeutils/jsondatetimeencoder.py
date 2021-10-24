# This file is part of the OceanInsightUVVIS library https://github.com/UoMMIB/OceanInsightUVVIS/
# Copyright (C) 2021 Alex Henderson (alex.henderson@manchester.ac.uk)
# SPDX-License-Identifier: MIT

from datetime import date, time, datetime
import json


class JsonDatetimeEncoder(json.JSONEncoder):
    """
    Class extending :class:`json.JSONEncoder` to handle :class:`datetime` objects.

    Code taken directly from `stackoverflow`_

    .. _`stackoverflow`: https://stackoverflow.com/questions/65338261/combine-multiple-json-encoders
    """

    def default(self, obj):
        """
        If a :class:`datetime.date`, :class:`datetime.time`, or :class:`datetime.datetime` object is passed in `obj`,
        the object's `isoformat` string will be returned. If the object is not one of these types,
        the base implementation is called (to raise a :class:`TypeError`).

        :param obj: a :class:`datetime` object
        :type obj: :class:`datetime.date`, :class:`datetime.time` or :class:`datetime.datetime`
        :return: a string containing the isoformat (ISO 8601) string of the input
        :rtype: str
        """
        if isinstance(obj, (date, time, datetime)):
            return obj.isoformat()
        # If we get to here, we can't handle this type.
        # Let the base class default method raise the TypeError.
        return super().default(obj)
