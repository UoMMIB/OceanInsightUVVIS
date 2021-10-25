# This file is part of the OceanInsightUVVIS library https://github.com/UoMMIB/OceanInsightUVVIS/
# Copyright (C) 2021 Alex Henderson (alex.henderson@manchester.ac.uk)
# SPDX-License-Identifier: MIT

from datetime import datetime, date, time
import json
from pathlib import Path
from typing import Optional

import pandas as pd
from pint import UnitRegistry
import pytz  # timezone utility

from utilities.pintutils.unitmanager import unitmanager
from utilities.jsonutils.multiplejsonencoders import MultipleJsonEncoders
from utilities.pintutils.jsonpintencoder import JsonPintEncoder
from utilities.datetimeutils.jsondatetimeencoder import JsonDatetimeEncoder


class UVVisSpectrum:
    """
    Class to read the Ocean Insight uv-vis spectral file format.

    The file must be in 'ASCII (with header data)' text format.

    Public properties:
        * `_filename`: a string containing the file's location.
        * `metadata`: a dict containing the file's headers (see also `metadata_as_dict`).
        * `header`: a dict containing the raw header information in the file.
        * `data`: a :class:`pandas.dataframe` containing the spectral data.

    :param filename: An Ocean Insight uv-vis spectrum file in 'ASCII (with header data)' text format.
    :type filename: str, optional

    """

    def __init__(self, filename: str = None):
        """
        Constructor method.

        :param filename: An Ocean Insight uv-vis spectrum file in 'ASCII (with header data)' text format.
        :type filename: str, optional
        """

        self._filename = filename
        self._metadata = dict()
        self._header = dict()
        self._data = pd.DataFrame()

        self.read(self._filename)

    def filename(self) -> Optional[str]:
        """
        Retrieve the name of the current spectrum file, or None if no filename is available.

        :return: The name of the currently active file
        :rtype: Optional[str]
        """
        return self._filename

    def metadata(self) -> dict:
        """
        Retrieve metadata relating to the spectrum file as a dict.

        :return: A dict of the file's metadata.
        :rtype: dict
        """
        return self._metadata

    def header(self) -> dict:
        """
        A dict containing the spectrum file's headers.

        :return: A dict containing the spectrum file's headers.
        :rtype: dict
        """
        return self._header

    def data(self) -> pd.DataFrame:
        """
        The spectral x- and y-values as a pandas.DataFrame.

        :return: The XY pairs representing the UVVIS spectrum
        :rtype: pandas.DataFrame
        """
        return self._data

    def read(self, filename: str = None) -> None:
        """
        Reads an Ocean Insight uv-vis spectrum file in 'ASCII (with header data)' text format.

        If a _filename is present in the object, perhaps passed to the constructor, and no _filename is passed in here,
        the object's _filename will be read.

        If this function is passed a _filename, and one is already present, the _filename here will overwrite the
        object's _filename and be read by this function.

        If no _filename is already present, and one is not passed in here, a `FileNotFoundError` exception is raised.

        :param filename: An Ocean Insight uv-vis spectrum file in 'ASCII (with header data)' text format.
        :type filename: str, optional
        :raises FileNotFoundError: Raised if no _filename is available, or the _filename is invalid.
        :return: This function returns no variable.
        :rtype: NoReturn
        """

        try:
            if filename:
                self._filename = filename

            filename = Path(self._filename)

            # Reset the contents in the case where we are reading a different file from that originally loaded.
            self._metadata = dict()
            self._header = dict()
            self._data = pd.DataFrame()

            x_values = list()
            y_values = list()

            first_line = True
            data_block = False
            with filename.open() as f:
                for line in f:
                    line = line.rstrip()
                    if first_line:
                        self._header['Description'] = line
                        first_line = False
                    else:
                        if line == '':
                            # Typically the second line in the file is blank
                            pass
                        else:
                            if line == '>>>>>Begin Spectral Data<<<<<':
                                # Starting the x-y pairs
                                data_block = True
                            else:
                                if data_block:
                                    x, y = line.split(sep='\t')
                                    x_values.append(float(x))
                                    y_values.append(float(y))
                                else:
                                    parts = line.split(sep=': ')
                                    if len(parts) != 2:
                                        raise Exception('Something wrong here')
                                    self._header[parts[0]] = parts[1]

            self._extract_metadata()

            x_label = self._metadata['abscissa']['label']
            y_label = self._metadata['ordinate']['label']

            self._data = pd.DataFrame(list(zip(x_values, y_values)),
                                      columns=[x_label, y_label])

            self._metadata['lowest-observed-wavelength'] = x_values[0]
            self._metadata['highest-observed-wavelength'] = x_values[-1]

        except FileNotFoundError as err:
            print(err)

    def _date_to_isoformat(self) -> str:
        """
        Convert the file's acquisition date to ISO 8601 format.

        If `Date` is in the file header, this function generates a version of it as a string in
        ISO 8601 format (YYYY-MM-DDThh:mm:ss+hh:mm).

        :return: A string containing the ISO 8601 format of the `self.date`.
        :rtype: str
        """
        if 'Date' in self._header:
            # Date: Thu Feb 27 15:05:24 GMT 2020
            date_parts = self._header['Date'].split()
            year = int(date_parts[5])
            dtmonth = datetime.strptime(date_parts[1], "%b")
            month = dtmonth.month
            day = int(date_parts[2])

            thedate = date(year, month, day)
            thetime = time.fromisoformat(date_parts[3])
            thetimezone = pytz.timezone(date_parts[4])

            thedatetime = datetime.combine(thedate, thetime, thetimezone)
            return thedatetime.isoformat()

    def _extract_metadata(self):
        """
        Convert the file header to a `dict`.

        Extracts the headers in the file and places then into the `self.metadata` dict.

        :return: This function returns no variable.
        :rtype: NoReturn
        """
        ureg = UnitRegistry()

        # Record the vendor's file format header
        self._metadata['vendor_header'] = self._header

        # Information about the technique
        self._metadata['technique'] = 'UV-vis spectroscopy'
        self._metadata['technique-iri'] = 'http://purl.obolibrary.org/obo/CHMO_0000292'

        # Information about the instrument
        self._metadata['instrument'] = dict()
        self._metadata['instrument']['vendor'] = 'Ocean Insight'
        if 'Spectrometer' in self._header:
            self._metadata['instrument']['spectrometer'] = self._header['Spectrometer']

        # Information about the experiment
        if 'Trigger mode' in self._header:
            # Making an assumption this is an integer
            self._metadata['Trigger mode'] = int(self._header['Trigger mode'])

        if 'Scans to average' in self._header:
            self._metadata['scans'] = int(self._header['Scans to average'])

        if 'Integration Time (sec)' in self._header:
            # Making an assumption this is a float
            dwell = ureg.Quantity(float(self._header['Integration Time (sec)']), ureg.sec)
            self._metadata['dwell-time'] = dwell

        if 'Nonlinearity correction enabled' in self._header:
            if self._header['Nonlinearity correction enabled'].lower() == 'false':
                self._metadata['Nonlinearity correction enabled'] = False
            else:
                self._metadata['Nonlinearity correction enabled'] = True

        if 'Boxcar width' in self._header:
            self._metadata['Boxcar width'] = int(self._header['Boxcar width'])

        if 'Storing dark spectrum' in self._header:
            if self._header['Storing dark spectrum'].lower() == 'false':
                self._metadata['Storing dark spectrum'] = False
            else:
                self._metadata['Storing dark spectrum'] = True

        # Generate information about the axes
        # If a x-axis label is provided, use that, but we have no information about the units
        # If the label happens to be 'Wavelengths', convert to wavelength in nm
        # Otherwise return a default label of 'x'
        if 'XAxis mode' in self._header:
            if self._header['XAxis mode'].lower() == 'wavelengths':
                x_label = unitmanager('wavelength', ureg.nm)
            else:
                x_label = unitmanager(self._header['XAxis mode'], ureg.dimensionless)
        else:
            # Default x label
            x_label = unitmanager('x', ureg.dimensionless)
        self._metadata['abscissa'] = x_label

        # Make up the y-axis label since we don't know if it is stored
        # Here we assume intensities are always stored in absorbance units (dimensionless)
        y_label = unitmanager('absorbance', ureg.dimensionless)
        self._metadata['ordinate'] = y_label

        if 'Number of Pixels in Spectrum' in self._header:
            self._metadata['number-of-data-points'] = int(self._header['Number of Pixels in Spectrum'])

        if 'Date' in self._header:
            self._metadata['acquisition-date'] = self._date_to_isoformat()

    def metadata_as_json(self, indent=4) -> str:
        """
        Convert the metadata to a JSON string.

        :param indent: Number of spaces to indent the JSON entries
        :type indent: int, optional
        :return: A string containing the JSON text
        :rtype: str
        """

        encoder = MultipleJsonEncoders(JsonPintEncoder, JsonDatetimeEncoder)

        json_metadata = json.dumps(self._metadata, indent=indent, cls=encoder)
        return json_metadata
