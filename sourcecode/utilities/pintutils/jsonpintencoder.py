# This file is part of the OceanInsightUVVIS library https://github.com/UoMMIB/OceanInsightUVVIS/
# Copyright (C) 2021 Alex Henderson (alex.henderson@manchester.ac.uk)
# SPDX-License-Identifier: MIT

import json

import pint


class JsonPintEncoder(json.JSONEncoder):
    """
    Class extending :class:`json.JSONEncoder` to handle :class:`pint` Quantity and Unit objects.

    Code taken directly from `stackoverflow`_

    .. _`stackoverflow`: https://stackoverflow.com/questions/65338261/combine-multiple-json-encoders
    """

    def default(self, obj):
        """
        If a :class:`pint.Quantity` or :class:`pint.Unit` object is passed in `obj`, a string representation of the
        object will be returned. If the object is not one of these types, the base implementation is called
        (to raise a :class:`TypeError`).

        :param obj: a :class:`pint` object
        :type obj: :class:`pint.Quantity` or :class:`pint.Unit`
        :return: a string representation of the pint object
        :rtype: str
        """

        if isinstance(obj, pint.Quantity):
            return str(obj)
        if isinstance(obj, pint.Unit):
            return str(obj)
        # If we get to here, we can't handle this type.
        # Let the base class default method raise the TypeError.
        return super().default(obj)
