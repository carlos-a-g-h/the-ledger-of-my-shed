#!/usr/bin/python3.9

# Languages

_LANG_EN="en"
_LANG_ES="es"

# One Megabyte

_ONE_MB=1048576

# Errors

_ERR="error"
_WARN="warning"

# _ERROR_SIGN_UNAUTHORIZED={
# 	_LANG_EN:"",
# 	_LANG_ES:""
# }

_SECTION="section"

# Internal app sotrage in memory (the state)

_APP_LANG="lang"
_APP_PROGRAMDIR="programdir"
_APP_ROOT_USERID="Root-UserID"
_APP_CACHE_ASSETS="AssetsCache"
_APP_BAKED_CSS="Baked_CSS"
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
_MIMETYPE_EXCEL="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# HTTP Headers

_HEADER_ACCEPT="Accept"
_HEADER_CONTENT_TYPE="Content-Type"
_HEADER_CONTENT_DISPOSITION="Content-Disposition"
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
_COOKIE_USER="USER-ID"

# Root User

_ROOT_USER="root"
_ROOT_USER_ID="000000000000000000000001"

# Request extra data
_REQ_USERNAME="Username"
_REQ_USERID="User_ID"
_REQ_ACCESS_KEY="Access_Key"
_REQ_CLIENT_TYPE="Client_Type"
_REQ_IS_HTMX="RequestFromHTMX"
_REQ_HAS_SESSION="Has_Session?"
_REQ_LANGUAGE="Language"

# Config file

_CFG_LANG="lang"
_CFG_DB_NAME="db-name"
_CFG_DB_URL="db-url"

_CFG_FLAGS="flags"
# _CFG_FLAG_ON_LAUNCH_CSS_NOT_BAKED="on-launch-css-not-baked"
_CFG_FLAG_ROOT_LOCAL_AUTOLOGIN="root-local-autologin"
_CFG_FLAG_PUB_READ_ACCESS_TO_ORDERS="pub-read-orders"
_CFG_FLAG_PUB_READ_ACCESS_TO_HISTORY="pub-read-history"
_CFG_FLAG_PVT_READ_ACCESS_TO_ASSETS="pvt-read-assets"

_CFG_PORT="port"
_CFG_PORT_MIN=1024
_CFG_PORT_MAX=65535

# Keys/Fields agnostic for ANYTHING

_KEY_SIGN="sign"
_KEY_SIGN_UNAME="sign_uname"
_KEY_TAG="tag"
_KEY_COMMENT="comment"
_KEY_DATE="date"

_KEY_DELETE_AS_ITEM="delete_as_item"
_KEY_VERBOSE="verbose"
_KEY_VLEVEL="vlevel"
