# TOTP code extractor / rebuilder

This program is designed for those, for some reason, unable to scan the QR Code from the MFA provider.

## Requirements

* Python 3 (Tested with 3.9)
* Python packages in [requirements.txt](requirements.txt) `pip3 install -r requirements.txt` or `pip install -r requirements.txt`
* libzbar (for non Windows platform only)
    * Debian / Ubuntu: `apt install libzbar0`
    * RedHat / CentOS Stream / Rocky Linux / AlmaLinux: `dnf install zbar`
    * MacOS: `brew install zbar`
* (Windows user only) Visual C++ Redistributable Packages for Visual Studio 2013
    * Download from [Official Site](https://www.microsoft.com/en-us/download/details.aspx?id=40784)

## Usage

```bash
python3 main.py path/to/image-1 path/to/image-2
```

Output the TOTP secret:
```bash
python3 main.py --show-secret path/to/image-1 path/to/image-2
```

Show help message:
```bash
python3 main.py --help
```

## Limitations

* Tilted QR Code maybe unable to read
* Some QR Code image may require some enhancement before reading
