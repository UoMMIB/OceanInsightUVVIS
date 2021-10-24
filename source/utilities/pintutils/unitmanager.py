# This file is part of the OceanInsightUVVIS library https://github.com/UoMMIB/OceanInsightUVVIS/
# Copyright (C) 2021 Alex Henderson (alex.henderson@manchester.ac.uk)
# SPDX-License-Identifier: MIT

from numbers import Number
from typing import Dict

import pint


def unitmanager(label: str, unit: pint.Unit = None, value: Number = None) -> Dict[str, str]:
    """
    Formats a quantity label suitable for use on the x-axis of a chart.

    Units are output in their shortform (nm for nanometer).
    If `unit` is not provided, the quantity will be treated as dimensionless.

    Example for a wavelength of 280 nm::

        >>> from utilities.pintutils import unitmanager
        >>> ureg = unitmanager.pint.UnitRegistry()
        >>> output = unitmanager.unitmanager('wavelength', ureg.nanometer, 280)
        >>> output
        {'name': 'wavelength', 'unit': 'nm', 'label': 'wavelength (nm)', 'value': 280, 'quantity': '280 nm'}
        >>> print(output['label'])
        wavelength (nm)
        >>> print(f'peak position = {output["quantity"]}')
        peak position = 280 nm

    Example for unitless absorbance::

        >>> from utilities.pintutils import unitmanager
        >>> ureg = unitmanager.pint.UnitRegistry()
        >>> output = unitmanager.unitmanager('absorbance')
        >>> output
        {'name': 'absorbance', 'unit': '', 'label': 'absorbance'}
        >>> print(output['label'])
        absorbance

    :param label: Name of the unit, for example 'wavelength'
    :type label: str
    :param unit: Name of the unit using the :py:class:`pint` method of describing units.
    :type unit: :py:class:`pint.Unit`, optional
    :param value: Value of the unit, for example 280 (for wavelength = 280 nm)
    :type value: Number, optional
    :return: Dictionary containing the name, unit, axis label (and quantity if provided)
    :rtype: Dict[str, str]
    """

    if unit == None:
        ureg = pint.UnitRegistry()
        unit = ureg.dimensionless

    output = dict()
    output['name'] = label
    output['unit'] = f"{unit:~}"

    if output['unit'] == '':
        output['label'] = f"{label}"
    else:
        output['label'] = f"{label} ({unit:~})"

    if value:
        output['value'] = value

        if output['unit'] == '':
            output['quantity'] = f"{value}"
        else:
            output['quantity'] = f"{value} {unit:~}"

    return output
