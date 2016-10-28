# Overview

This is a python script for transforming SSI billing SQL table definitions
to the DA schema for the EDW.

# Usage

First, install the required support library, `sed`:
```
$ pip install sed
```

Then, go to the directory that has all the table definitions.
It is assumed that they have textfile extensions and will be converted to
SQL file extensions. This way, the source files are not overwritten.
```
$ ./transform.py --ext=.txt --new-ext=.sql
```

In addition, I found this useful for renaming th efiles and moving them over to
the SSI Windows environment en masse. The idea is to make a single zip file and
to spin up an HTTP server that a web browser can download the file from on the
VPN/RDP machine:
```
$ for a in *.sql mv $a billing_$a;
$ zip -m SQL *.sql
$ python -m SimpleHTTPServer
```

On the VPN/RDP machine, go to 
    http://<your local machine address>:8000/SQL.zip
and that should begin to download the file for use.

