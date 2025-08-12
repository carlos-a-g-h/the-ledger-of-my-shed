#!/usr/bin/python3.9

# Languages

_LANG_EN="en"
_LANG_ES="es"

# One Megabyte

_ONE_MB=1048576

# Local directories
_DIR_TEMP="temp"
_DIR_SOURCES="sources"

_MONGO_URL_DEFAULT="mongodb://127.0.0.1:27017"

_LOCALHOST_IPV4="127.0.0.1"
_LOCALHOST_IPV6="::1"

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
_APP_TGHC="Telegram-Client"

# Date conversion formats

_FMT_DATE_YMDHMS="%Y-%m-%d-%H-%M-%S"
_FMT_DATE_YMDHM="%Y-%m-%d-%H-%M"
_FMT_DATE_YMDH="%Y-%m-%d-%H"
_FMT_DATE_YMD="%Y-%m-%d"
_FMT_DATE_YM="%Y-%m"

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
_MIMETYPE_SQLITE3="application/vnd.sqlite3"

# HTTP Headers

_HEADER_ACCEPT="Accept"
_HEADER_CONTENT_TYPE="Content-Type"
_HEADER_CONTENT_DISPOSITION="Content-Disposition"
_HEADER_REFERER="Referer"
_HEADER_USER_AGENT="User-Agent"

# Excel related

# _excel_columns=[
# 	"",
# 	"A","B","C",
# 	"D","E","F",
# 	"G","H","I",
# 	"J","K","L",
# 	"M","N","O",
# 	"P","Q","R",
# 	"S","T","U",
# 	"V","W","X",
# 	"Y",
# 	"Z",
# ]

# The f***ing Cookies!
_CRED_TYPE="CRED_TYPE"
_CRED_VISITOR="CRED_VISITOR"
_CRED_EMPLOYEE="CRED_EMPLOYEE"
_COOKIE_CLIENT="CLIENT-ID"
_COOKIE_AKEY="ACCESS-KEY"
_COOKIE_USER="USER-ID"

# Root User
_ROOT_USER="root"
_ROOT_USER_ID="000000000000000000000001"

# Request extra data
_REQ_USERNAME="Username"
_REQ_USERID="User_ID"
_REQ_CID="Client_ID"
_REQ_SID="Session_ID"
_REQ_ACCESS_KEY="Access_Key"
_REQ_CLIENT_TYPE="Client_Type"
_REQ_IS_HTMX="RequestFromHTMX"
_REQ_HAS_SESSION="Has_Session?"
_REQ_LANGUAGE="Language"
_REQ_PATH="Path_In_Pathlib"

# Config file

_CFG_LANG="lang"
_CFG_DB_NAME="db-name"
_CFG_DB_URL="db-url"

_CFG_ACC="accounts"
_CFG_ACC_TIMEOUT_OTP="timeout-otp"
_CFG_ACC_TIMEOUT_SESSION="timeout-session"

_CFG_FLAGS="flags"
_CFG_FLAG_D_SECURITY="d-security"
_CFG_FLAG_E_STARTUP_RUN_MONGOD="e-startup-run-mongod"
_CFG_FLAG_E_STARTUP_PRINT_ASSETS="e-startup-print-assets"
_CFG_FLAG_E_STARTUP_PRINT_NW_INTERFACES="e-startup-print-nw-interfaces"
_CFG_FLAG_D_STARTUP_CSS_BAKING="d-startup-css-baking"
_CFG_FLAG_E_LOGIN_ROOT_LOCAL_AUTOLOGIN="e-login-root-local-autologin"
_CFG_FLAG_E_LOGIN_BACKEND_OTP_ALL="e-login-backend-otp-for-all"
# _CFG_FLAG_PUB_READ_ACCESS_TO_ORDERS="pub-read-orders"
# _CFG_FLAG_PUB_READ_ACCESS_TO_HISTORY="pub-read-history"
# _CFG_FLAG_PVT_READ_ACCESS_TO_ASSETS="pvt-read-assets"

_CFG_PORT="port"
_CFG_PORT_MIN=1024
_CFG_PORT_MAX=65535

_CFG_TELEGRAM="telegram"
_CFG_TELEGRAM_API_ID="api-id"
_CFG_TELEGRAM_API_HASH="api-hash"
_CFG_TELEGRAM_BOT_TOKEN="bot-token"
_CFG_TELEGRAM_API_LVL="tg-api-lvl"

# Keys/Fields for anything

_KEY_ID="_id"
_KEY_STATUS="status"
# _KEY_MQUALITY="mquality"
_KEY_SIGN="sign"
_KEY_SIGN_UNAME="sign_uname"
_KEY_TAG="tag"
_KEY_COMMENT="comment"
_KEY_DATE="date"

_KEY_FOCUS="focus"

_KEY_GETRES="get-result"

_KEY_DATE_UTC="date-utc"
_KEY_DATE_MIN="date-min"
_KEY_DATE_MAX="date-max"

# _KEY_GO_STRAIGHT="go_straight"
_KEY_DELETE_AS_ITEM="delete-as-item"
_KEY_VERBOSE="verbose"
_KEY_VLEVEL="vlevel"

_KEY_NAME_QUERY="name-query"
_KEY_INC_TAG="include-tag"
_KEY_INC_COMMENT="include-comment"

_KEY_JOB="job"
_KEY_JOB_RUN="run"
_KEY_JOB_REVERT="revert"
