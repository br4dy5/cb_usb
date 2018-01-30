# cb_usb
Identify USB activity on host(s) and outputs time, host, user, usb brand, model and serial using Carbon Black.

## Install Dependencies
It's expected that you're an authorized user of Carbon Black Response, but if you have not yet configured your API, instructions can be found here: https://cbapi.readthedocs.io/en/latest/#api-credentials
    
    pip install -r requirements.txt

## Usage
usage: cb_usb.py [-h] [-m HOST] [-l LIST] [-e EXCLUDE] [-i INCLUDE]

optional arguments:

-h,    --help   show this help message and exit

-m HOST,    --host    HOST    hostname to query for USB activity

-l LIST,    --list    LIST    file of list of hostnames, one per line, e.g. hosts.txt

-e EXCLUDE,    --exclude    EXCLUDE    USB brand or serial to exclude, e.g. "samsung"

-i INCLUDE,    --include    INCLUDE    USB brand or serial to query

-r RESULTS,    --results RESULTS    number of results returned per host. default=1

### Example
This example will search for the most recent USB activity on host 'Host123' which does not include 'sandisk' in the registry modification.

    cb_usb.py -m host123 -e sandisk

### Example Output
    Checking 1 host(s)
    Processing host123
    ('2018-01-29T08:28:31', u'host123', u'US\\johnsmith', 'lexar usb_flash_drive', u'aarur46ajdg15me6a&0', u'https://123.45.6.789:1234/#analyze/000012345-0000-0001-0123-987654321/123456789')
    All hosts have been processed.

