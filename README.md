# My Shed's Ledger (SHLED)

## What is this now?

This is a very simple inventory manager, it only supports fungible assets at the moment

### DISCLAIMER

I do not know anything about accounting, or have any background on warehousing or inventory management solutions, this is my first project of that nature, and I'm relying on my common sense on how fungible assets with physical presence in an inventory should be handled, so if you check out the code or use the program, expect some non-standard terminology in the naming of things

## Features

More will be added but this is what you can do right now:

- CRUD operations for assets definitions
- Accumulative history for each asset
- Large scale record modifications using orders
- User accounts system with dynamic passwords
- Export assets and orders as excel files

### Pending

- User creation functionality (the only user right now is root)
- Propper API (route naming, authorization, etc... ) for custom clients
- Better CSS consistency

## This is built on what?

### Backend

- AioHTTP (A web server framework for Python)
- MongoDB (Using the motor library)
- SQLite (Available on the Python standard library)

### Frontend

- Vainilla HTML/CSS
- HTMX (It is bundled along with this project but you can provide your own if you want to)

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
