# My Shed's Ledger (SHLED)

## What is this now?

This is a very simple inventory manager, it only supports fungible assets at the moment

### DISCLAIMER

I do not know anything about accounting, or have any background on warehousing or inventory management solutions, this is my first project of that nature, and I'm relying on my common sense on how fungible assets with physical presence in an inventory should be handled, so if you check out the code or use the program, expect some non-standard terminology in the naming of things

## Features

More will be added but this is what you can do right now:

- CRUD operations for assets definitions
- Accumulative history for each asset
- Large scale record modifications using orders. Orders are by default locked down uopon executing and can be used for auditing or accurate book keeping
- User accounts system with dynamic passwords. Users can be created or deleted by the root account
- Export assets and orders as excel files. The resulting excel files can be edited for any specific purposes

### Pending

- Propper API (route naming, authorization, etc... ) for custom clients
- Better CSS consistency

## This is built on what?

### Backend

- AioHTTP.server (Asynchronous web server for python)
- MongoDB (Remote/main database, motor and pymongo libraries)
- SQLite (Local/caching database, python's SQLite3 library)

### Frontend

- Vainilla HTML/CSS
- HTMX
- AlpineJS

## How to run this ?

First of all, Make sure you have a MongoDB server instance available to use, wether you have it locally or remotely

You might want to check out the "config.yaml" file and adjust it to your needs, specially if you are using MongoDB remotely

After ensuring that there is a MongoDB instance available, you can run the server like this

```
$ chmod +x shled.bin; ./shled.bin
```

or like this if you're running directly from the source code

```
$ python3 main.py
```

or you can just double-click the "shled.exe" executable it if you're on Windows

Shled can also accept a custom config file as a command line argument instead of the default "config.yaml" file

```
$ ./shled.bin "/your/custom/configuration/file.yaml"
```

NOTE: Relative paths are relative not to your working directory, but to the program's directory

### How to customize the CSS

Add/modify CSS files to the sources directory. At the startup phase, the files will be concatenated into a single 'custom.css' file and this is the CSS file that will be loaded on each page request

There is a flag called 'd-startup-css-baking', this flag disables the default CSS "baking phase" and allows you to modify the CSS in a way more comfortable way while the server is running

### Bring your own files

The HTMX and AlpineJS files that come with SHLED can be updated with newer versions or replaced with your own copies

```
$ wget https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js -O sources/alpine.js
```

```
$ wget https://unpkg.com/htmx.org@2.x.x -O sources/htmx.min.js
```