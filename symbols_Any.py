#!/usr/bin/python3.9

# One Megabyte
_ONE_MB=1048576

# Languages
_LANG_EN="en"
_LANG_ES="es"

# Internal app sotrage in memory (the state)
_APP_LANG="lang"
_APP_PROGRAMDIR="programdir"
_APP_CACHE_ASSETS="AssetsCache"
_APP_RDBN="MongoDB-DB-Name"
_APP_RDBC="MongoDB-Client"

# Client Types
_TYPE_CUSTOM="CustomClient"
_TYPE_BROWSER="Browser"

# MIME Types
_MIMETYPE_CSS="text/css"
_MIMETYPE_HTML="text/html"
_MIMETYPE_JS="application/javascript"
_MIMETYPE_JSON="application/json"
_MIMETYPE_FORM="application/x-www-form-urlencoded"

# HTTP Headers
_HEADER_ACCEPT="Accept"
_HEADER_CONTENT_TYPE="Content-Type"
_HEADER_REFERER="Referer"
_HEADER_USER_AGENT="User-Agent"

# Excel related
_excel_columns=[
	"Z",
	"A","B","C",
	"D","E","F",
	"G","H","I",
	"J","K","L",
	"M","N","O",
	"P","Q","R",
	"S","T","U",
	"V","W","X",
	"Y",
]

# The f***ing Cookies!
_COOKIE_AKEY="ACCESS-KEY"
_COOKIE_USER="USER-NAME"

# Root User
_ROOT_USER="root"

# Request baggage
_REQ_USERNAME="Username"
_REQ_ACCESS_KEY="Access_Key"
_REQ_CLIENT_TYPE="Client_Type"
_REQ_HAS_SESSION="Has_Session?"
_REQ_LANGUAGE="Language"

# Config file
_CFG_PORT="port"
_CFG_LANG="lang"
_CFG_DB_NAME="db-name"
_CFG_DB_URL="db-url"

_PORT_MIN=1024
_PORT_MAX=65535