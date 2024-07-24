# My Shed's Ledger

## What is this now?

This is a very simple inventory manager, it only supports fungible assets at the moment

### DISCLAIMER

I do not know anything about accounting, or have any background on warehousing or inventory management solutions, this is my first project of that nature, and I'm relying on my common-sense on how fungible assets with physical presence in an inventory should be handled, so if you check out the code or use the program, expect some non-standard terminology in the naming of things

## Features

More will be added but this is what you can do right now:

- CRUD operations for assets definitions
- Add modification records within each asset
- CRUD operations with orders (The order book)

### Pending

- User authentication and authorization
- Propper API for external clients and frontends
- Safer order handling
- Modification records query by date

## This is built on what?

### Backend

- AioHTTP (Python)
- MongoDB (using the motor driver)

### Frontend

- Vainilla HTML/CSS
- HTMX (It is bundled along with this project but you can provide your own if you want to)

## How Do I run this ?

First of all, Make sure you have a MongoDB server instance available to use, wether you have it locally or remotely, it doesn't matter

First of all, open up the "config.yaml" file and adjust it to your needs

After setting it up, you can run the server like this

```
$ chmod +x shled; ./shled
```
or like this if you're not running directly from the source code

```
$ python3 main.py
```

### How to customize the CSS

You can customize the looks of this thing by editing the "custom.css" file, feel free to adjust it to your needs

NOTE: If you're going to edit anything related to the popup messages, check the "popup.css" file using your browser's CSS Editor while the server is running
