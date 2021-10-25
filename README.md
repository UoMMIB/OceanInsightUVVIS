# OceanInsightUVVIS
_Release v2.0.0_   

Python package to read the Ocean Insight ultraviolet-visible spectroscopy (uv-vis) file format.

[Ocean Insight](https://www.oceaninsight.com/) (formerly Ocean Optics) produce instrumentation for spectroscopy. 
Their data acquisition package &ndash; [OceanView](https://www.oceaninsight.com/products/software/) &ndash; can export 
spectra in a number of file formats. Here we read the `ASCII (with header data)` text format.

## Usage
### Construction
To read a spectrum file, first create an instance of an OceanInsightUVVIS class, then pass the spectrum filename to 
the `read`function. As a shortcut, pass the spectrum filename directly to the constructor.

```python

from uvvis.uvvis_spectrum import UVVisSpectrum

obj = UVVisSpectrum()
spectrum = obj.read("myfile.txt")
```
or

```python

from uvvis.uvvis_spectrum import UVVisSpectrum

spectrum = UVVisSpectrum("myfile.txt")
```

### Functionality
Retrieve the filename of the currently active spectrum  
    `filename = spectrum.filename()`

Retrieve the spectral data as a pandas.DataFrame  
`data = spectrum.data()`

Retrieve the raw file header information as a dictionary  
`header = spectrum.header()`  

Retrieve the file metadata as a dictionary  
`metadata = spectrum.metadata()`  

Retrieve the file metadata as a JSON string    
`jsonmetadata = spectrum.metadata_as_json()`  

## Copyright and Licence for use
Copyright (C) 2021 Alex Henderson [alex.henderson@manchester.ac.uk](mailto:alex.henderson@manchester.ac.uk)  
Release v2.0.0

This work is licensed under a [MIT](https://opensource.org/licenses/MIT) license.  
SPDX-License-Identifier: MIT  

The most recent version of this software library can be found here: [https://github.com/UoMMIB/OceanInsightUVVIS/](https://github.com/UoMMIB/OceanInsightUVVIS/)

## Contributors
Alex Henderson, University of Manchester. [alex.henderson@manchester.ac.uk](mailto:alex.henderson@manchester.ac.uk)