#!/usr/bin/python3.9

from typing import Mapping,Optional

from aiohttp.web import Request

from symbols_accounts import (
	_ROUTE_CHECKIN,
	_KEY_USERID,
	_KEY_CON_EMAIL,_KEY_CON_TELEGRAM,
	_KEY_SIM,_KEY_OTP,_KEY_USERNAME,
	id_user,
)

from control_Any import (
	is_root_local_autologin_allowed,
	get_username
)

from symbols_Any import (
	_LANG_EN,_LANG_ES,
	_REQ_USERID,
	_CFG_ACC_TIMEOUT_SESSION,

)

from symbols_accounts import (
	_ID_FORM_LOGIN,
	_ID_USER_ACCOUNT

)

from frontend_Any import (

	_ID_MSGZONE,

	_CSS_CLASS_COMMON,
	_CSS_CLASS_CONTROLS,
	_CSS_CLASS_NAV,
	_CSS_CLASS_IG_FIELDS,

	write_html_input_string,
	write_html_input_radio,
	# write_button_anchor,
)

# def write_link_account(lang:str,return_there:bool=False)->str:

# 	return write_button_anchor(
# 		{
# 			_LANG_EN:{
# 				True:"Return to account page",
# 				False:"Account"
# 			}[return_there],
# 			_LANG_ES:{
# 				True:"Volver a la página de la cuenta",
# 				False:"Cuenta"
# 			}[return_there],
# 		}[lang],
# 		"/page/accountss"
# 	)

def write_html_user(
		lang:str,
		data:Mapping,
		full:bool=True
	)->str:

	userid=data.get(_KEY_USERID)

	username=data.get(_KEY_USERNAME)

	con_telegram=data.get(_KEY_CON_TELEGRAM)

	con_email=data.get(_KEY_CON_EMAIL)

	html_text=(
		f"<div>{username} | {userid}</div>\n"
	)

	if con_telegram is not None:
		tl={
			_LANG_EN:"Telegram user",
			_LANG_ES:"Usuario de Telegram"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{con_telegram}</code></div>"
		)

	if con_email is not None:
		tl={
			_LANG_EN:"E-Mail",
			_LANG_ES:"Correo electrónico"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{con_email}</code></div>"
		)

	if full:
		html_text=(
			f"""<div id={id_user(userid)} class="{_CSS_CLASS_COMMON}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_button_login(lang:str)->str:

	# Sends:
	# GET: /fgmt/accounts/login
	# hx-target: #messages

	tl={
		_LANG_EN:"Log in",
		_LANG_ES:"iniciar sesión"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_NAV}" """
			"""hx-get="/fgmt/accounts/login" """
			f"""hx-target=#{_ID_MSGZONE} """
			"""hx-swap="innerHTML" """
			">"
			f"{tl}"
		"</button>"
	)


def write_form_login(lang:str,depth:int=0)->str:

	# Sends: POST /api/accounts/login {username:String,vmethod:String}

	tl={
		_LANG_EN:"Username",
		_LANG_ES:"Nombre de usuario",
	}[lang]
	html_text=(
		f"""<div class="{_CSS_CLASS_IG_FIELDS}">""" "\n"
			f"{write_html_input_string(_KEY_USERNAME,tl,required=True)}\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Sign in method",
		_LANG_ES:"Método de inicio de sesión"
	}[lang]
	sim_opts=[
		(
			_KEY_CON_EMAIL,
			{
				_LANG_EN:"E-Mail",
				_LANG_ES:"Correo electrónico"
			}[lang]
		),
		(
			_KEY_CON_TELEGRAM,
			{
				_LANG_EN:"E-Mail",
				_LANG_ES:"Correo electrónico"
			}[lang]
		),
		(
			"",
			{
				_LANG_EN:"None/hidden",
				_LANG_ES:"Ninguno/oculto"
			}[lang]
		),
	]
	html_text=(
		f"{html_text}\n"
		"<div>\n"
			f"""<label for="{_KEY_SIM}">{tl}</label>""" "\n"
			f"{write_html_input_radio(_KEY_SIM,options=sim_opts)}\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Next",
		_LANG_ES:"Siguiente"
	}[lang]
	html_text=(
		"""<form hx-post="/api/accounts/login" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-swap="innerHTML">""" "\n"

			f"{html_text}\n"

			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"""<button class="{_CSS_CLASS_COMMON}" type=submit>{tl}</button>""" "\n"
			"</div>\n"

		"</form>"
	)

	if depth<2:
		tl={
			_LANG_EN:"Session login",
			_LANG_ES:"Inicio de sesión"
		}[lang]
		html_text=(
			f"<h3>{tl}</h3>\n"
			f"""<div id="{_ID_FORM_LOGIN}-inner">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	if depth<1:
		html_text=(
			f"""<div id="{_ID_FORM_LOGIN}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_form_otp(
		lang:str,
		username:str,
		sim:Optional[str]=None,
		depth:int=0,
	)->str:

	# Sends: POST /api/accounts/login-otp {username:String,otp:String}

	# NOTE: The form needs to lead to a full page load to make those cookies, so I can't use HTMX here

	tl={
		_LANG_EN:"Enter the generated password",
		_LANG_ES:"Introduzca la contraseña generada"
	}[lang]
	html_text=(
		f"""<input name="{_KEY_USERNAME}" type=hidden value="{username}">""" "\n"

		f"{write_html_input_string(_KEY_OTP,tl,maxlen=32)}"
	)

	sim_ok=False
	if sim==_KEY_CON_EMAIL:
		sim_ok=True
		tl={
			_LANG_EN:"The generated password has been sent to your e-mail",
			_LANG_ES:"La contraseña generada ha sido enviada a su correo electrónico"
		}[lang]

	if sim==_KEY_CON_TELEGRAM:
		sim_ok=True
		tl={
			_LANG_EN:"The generated password has been sent to you through the Telegram bot",
			_LANG_ES:"La contraseña generada ha sido enviada a través del bot de Telegram"
		}[lang]

	if sim_ok:
		html_text=(
			f"{html_text}\n"
			f"<div>[ {tl} ]</div>"
		)

	tl={
		_LANG_EN:"Confirm",
		_LANG_ES:"Confirmar"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
			f"""<button class="{_CSS_CLASS_COMMON}" type=submit>{tl}</button>""" "\n"
		"<div>"
	)

	html_text=(
		"""<form method="POST" """
			"""action="/api/accounts/login-otp" """
			">\n"

			f"{html_text}\n"

		"</form>"
	)

	if depth<2:
		tl={
			_LANG_EN:"Session login (OTP)",
			_LANG_ES:"Inicio de sesión (OTP)"
		}[lang]
		html_text=(
			f"<h3>{tl}</h3>\n"
			f"""<div id="{_ID_FORM_LOGIN}-inner">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	if depth<1:
		html_text=(
			f"""<div id="{_ID_FORM_LOGIN}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_button_login_magical(lang:str)->str:

	# WARNING: This is dangerous
	# NOTE: Available only at the server machine and by enabling the local root autologin flag

	tl={
		_LANG_EN:"Start local session",
		_LANG_ES:"Iniciar sesión local"
	}[lang]

	return (
		"""<form method="POST" """
			"""action="/api/accounts/login-magical" """
			">\n"
			f"""<button class="{_CSS_CLASS_NAV}" type=submit>{tl}</button>""" "\n"
		"</form>"
	)

def write_html_keepalive(interval:int)->str:
	return (
		f"""<div hx-post={_ROUTE_CHECKIN} hx-trigger="every {interval}s">""" "\n"
			"<!-- KEEPING THE SESSION ALIVE -->"
		"</div>"
	)

def write_button_logout(lang:str)->str:

	# Sends: DELETE /api/accounts/logout

	tl={
		_LANG_EN:"Are you sure you want to logout?",
		_LANG_ES:"¿Seguro que quieres cerrar sesión?"
	}[lang]
	html_text=(
		f"""<button class="{_CSS_CLASS_NAV}" """
			"""hx-delete="/api/accounts/logout" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-swap="innerHTML" """
			f"""hx-confirm="{tl}" """
			">\n"
	)

	tl={
		_LANG_EN:"Logout",
		_LANG_ES:"Cerrar sesión"
	}[lang]
	html_text=(
		f"{html_text}\n"
			f"{tl}\n"
		"</button>"
	)

	return html_text

async def render_html_user_section(
		request:Request,
		lang:str,full:bool=True,
	)->str:

	html_text=""

	userid:Optional[str]=request[_REQ_USERID]
	username:Optional[str]=None

	anonymous=(userid is None)
	if not anonymous:
		username=await get_username(
			request,explode=False,
			userid=userid
		)
		anonymous=(username is None)

	if not anonymous:

		keep_alive_time=int(
			0.5*request.app[_CFG_ACC_TIMEOUT_SESSION]
		)

		html_text=(
			f"{html_text}\n"
			f"<div>{username}</div>\n"
			f"{write_button_logout(lang)}\n"
			f"{write_html_keepalive(keep_alive_time)}"
		)

	if anonymous:
		super_login=is_root_local_autologin_allowed(request)
		if super_login:
			html_text=(
				f"{html_text}\n"
				f"{write_button_login_magical(lang)}"
			)
		if not super_login:
			html_text=(
				f"{html_text}\n"
				f"{write_button_login(lang)}"
			)

	if full:
		html_text=(
			f"""<div id="{_ID_USER_ACCOUNT}">""" "\n"
				f"{html_text}\n"
			"""</div>"""
		)

	return html_text

