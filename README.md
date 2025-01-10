# My Shed's Ledger

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

### Pending

- Exporting/Importing asset definitions, orders, etc...
- Propper API (route naming, authorization, etc... ) for custom clients

## This is built on what?

### Backend

- AioHTTP (A web server framework for Python)
- MongoDB (Using the motor library)
- SQLite (Available on the Python standard library)

### Frontend

- Vainilla HTML/CSS
- HTMX (It is bundled along with this project but you can provide your own if you want to)

## How to run this ?

First of all, Make sure you have a MongoDB server instance available to use, wether you have it locally or remotely, it doesn't matter

You might want to check out the "config.yaml" file and adjust it to your needs, specially if you are using MongoDB remotely and not locally

After setting it up, you can run the server like this

```
$ chmod +x shled; ./shled
```

or like this if you're not running directly from the source code

```
$ python3 main.py
```

or you can just double-click the "shled.exe" executable it if you're on Windows

### How to customize

You can customize the looks of this thing by editing the "custom.css" file, feel free to adjust it to your needs

NOTE: If you're going to edit anything related to the popup messages, check the "popup.css" file using your browser's CSS Editor while the server is running
