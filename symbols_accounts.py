#!/usr/bin/python3.9

_ROUTE_PAGE="/page/accounts"
_ROUTE_FGMT_LOGIN="/fgmt/accounts/login"
_ROUTE_API_CHECKIN="/api/accounts/check-in"
_ROUTE_API_LOGIN="/api/accounts/login"
_ROUTE_API_LOGIN_OTP="/api/accounts/login-otp"
_ROUTE_API_LOGIN_MAGIC="/api/accounts/login-magical"
_ROUTE_API_LOGOUT="/api/accounts/logout"
_ROUTE_API_OTP_NEW="/api/accounts/otp-new"
_ROUTE_API_OTP_CON="/api/accounts/otp-con"

_KEY_ACC_EMAIL="email"
_KEY_ACC_TELEGRAM="telegram"
_KEY_USERID="userid"
_KEY_USERNAME="username"
_KEY_SETTINGS="settings"

# NOTE: SIM = Sign In Method

_KEY_OTP="otp"
_KEY_DATE="date"
# _MS_UA="user_agent"
# _MS_IP="ip_address"
_KEY_AKEY="access_key"
_KEY_SIM="sim"

_MONGO_COL_USERS="users"

_SQL_FILE_SESSIONS="ldb_sessions.db"
_SQL_FILE_USERS="ldb_users.db"

_SQL_TABLE_USERS="TheUsers"
_SQL_TABLE_SESSION_CANDIDATES="SessionCandidates"
_SQL_TABLE_ACTIVE_SESSIONS="ActiveSessions"

_SQL_COL_DATE="TheDate"
_SQL_COL_USERID="UserID"
# _SQL_COL_USERNAME="UserName"
# _SQL_COL_TGUID="TelegramUserID"
# _SQL_COL_EMAIL="Email"
_SQL_COL_OTP="OneTimePassword"
_SQL_COL_AKEY="AccessKey"
_SQL_COL_SID="SessionID"

_ID_FORM_LOGIN="form-login"
_ID_USER_ACCOUNT="user-account"

def id_user(userid:str)->str:
	return f"user-{userid}"

