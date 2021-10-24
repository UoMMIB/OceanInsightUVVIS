# This file is part of the OceanInsightUVVIS library https://github.com/UoMMIB/OceanInsightUVVIS/
# Copyright (C) 2021 Alex Henderson (alex.henderson@manchester.ac.uk)
# SPDX-License-Identifier: MIT

from datetime import datetime, date, time
import json
from pathlib import Path

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
        * `filename`: a string containing the file's location.
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

        self.filename = filename
        self.metadata = dict()
        self.header = dict()
        self.data = pd.DataFrame()

        self.read(self.filename)

    def read(self, filename: str = None) -> None:
        """
        Reads an Ocean Insight uv-vis spectrum file in 'ASCII (with header data)' text format.

        If a filename is present in the object, perhaps passed to the constructor, and no filename is passed in here,
        the object's filename will be read.

        If this function is passed a filename, and one is already present, the filename here will overwrite the
        object's filename and be read by this function.

        If no filename is already present, and one is not passed in here, a `FileNotFoundError` exception is raised.

        :param filename: An Ocean Insight uv-vis spectrum file in 'ASCII (with header data)' text format.
        :type filename: str, optional
        :raises FileNotFoundError: Raised if no filename is available, or the filename is invalid.
        :return: This function returns no variable.
        :rtype: NoReturn
        """

        try:
            if filename:
                self.filename = filename

            filename = Path(self.filename)

            # Reset the contents in the case where we are reading a different file from that originally loaded.
            self.metadata = dict()
            self.header = dict()
            self.data = pd.DataFrame()

            x_values = list()
            y_values = list()

            first_line = True
            data_block = False
            with filename.open() as f:
                for line in f:
                    line = line.rstrip()
                    if first_line:
                        self.header['Description'] = line
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
                                    self.header[parts[0]] = parts[1]

            self._extract_metadata()

            x_label = self.metadata['abscissa']['label']
            y_label = self.metadata['ordinate']['label']

            self.data = pd.DataFrame(list(zip(x_values, y_values)),
                                     columns=[x_label, y_label])

            self.metadata['lowest-observed-wavelength'] = x_values[0]
            self.metadata['highest-observed-wavelength'] = x_values[-1]

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
        if 'Date' in self.header:
            # Date: Thu Feb 27 15:05:24 GMT 2020
            date_parts = self.header['Date'].split()
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
        self.metadata['vendor_header'] = self.header

        # Information about the technique
        self.metadata['technique'] = 'UV-vis spectroscopy'
        self.metadata['technique-iri'] = 'http://purl.obolibrary.org/obo/CHMO_0000292'

        # Information about the instrument
        self.metadata['instrument'] = dict()
        self.metadata['instrument']['vendor'] = 'Ocean Insight'
        if 'Spectrometer' in self.header:
            self.metadata['instrument']['spectrometer'] = self.header['Spectrometer']

        # Information about the experiment
        if 'Trigger mode' in self.header:
            # Making an assumption this is an integer
            self.metadata['Trigger mode'] = int(self.header['Trigger mode'])

        if 'Scans to average' in self.header:
            self.metadata['scans'] = int(self.header['Scans to average'])

        if 'Integration Time (sec)' in self.header:
            # Making an assumption this is a float
            dwell = ureg.Quantity(float(self.header['Integration Time (sec)']), ureg.sec)
            self.metadata['dwell-time'] = dwell

        if 'Nonlinearity correction enabled' in self.header:
            if self.header['Nonlinearity correction enabled'].lower() == 'false':
                self.metadata['Nonlinearity correction enabled'] = False
            else:
                self.metadata['Nonlinearity correction enabled'] = True

        if 'Boxcar width' in self.header:
            self.metadata['Boxcar width'] = int(self.header['Boxcar width'])

        if 'Storing dark spectrum' in self.header:
            if self.header['Storing dark spectrum'].lower() == 'false':
                self.metadata['Storing dark spectrum'] = False
            else:
                self.metadata['Storing dark spectrum'] = True

        # Generate information about the axes
        # If a x-axis label is provided, use that, but we have no information about the units
        # If the label happens to be 'Wavelengths', convert to wavelength in nm
        # Otherwise return a default label of 'x'
        if 'XAxis mode' in self.header:
            if self.header['XAxis mode'].lower() == 'wavelengths':
                x_label = unitmanager('wavelength', ureg.nm)
            else:
                x_label = unitmanager(self.header['XAxis mode'], ureg.dimensionless)
        else:
            # Default x label
            x_label = unitmanager('x', ureg.dimensionless)
        self.metadata['abscissa'] = x_label

        # Make up the y-axis label since we don't know if it is stored
        # Here we assume intensities are always stored in absorbance units (dimensionless)
        y_label = unitmanager('absorbance', ureg.dimensionless)
        self.metadata['ordinate'] = y_label

        if 'Number of Pixels in Spectrum' in self.header:
            self.metadata['number-of-data-points'] = int(self.header['Number of Pixels in Spectrum'])

        if 'Date' in self.header:
            self.metadata['acquisition-date'] = self._date_to_isoformat()

    def metadata_as_dict(self) -> dict:
        """
        Convert the metadata to a dict.

        :return: A dict of the file's metadata headers.
        :rtype: dict
        """

        return self.metadata

    def metadata_as_json(self, indent=4) -> str:
        """
        Convert the metadata to a JSON string.

        :param indent: Number of spaces to indent the JSON entries
        :type indent: int, optional
        :return: A string containing the JSON text
        :rtype: str
        """

        encoder = MultipleJsonEncoders(JsonPintEncoder, JsonDatetimeEncoder)

        json_metadata = json.dumps(self.metadata, indent=indent, cls=encoder)
        return json_metadata
