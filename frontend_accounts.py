#!/usr/bin/python3.9

from typing import Mapping,Optional

from aiohttp.web import Request

from control_Any import (
	is_root_local_autologin_allowed,
	# get_username
)

from frontend_Any import (

	_ID_MSGZONE,

	_CSS_CLASS_COMMON,
	_CSS_CLASS_CONTROLS,
	_CSS_CLASS_NAV,
	_CSS_CLASS_IG_FIELDS,
	_CSS_CLASS_INPUT_GUARDED,

	# write_popupmsg,
	write_button_submit,
	write_html_input_string,
	write_html_input_checkbox,
	write_html_input_radio,
	# write_button_anchor,
)

from symbols_Any import (
	_LANG_EN,_LANG_ES,
	_CFG_FLAGS,
		_CFG_FLAG_D_SECURITY,
		# _CFG_FLAG_E_LOGIN_ROOT_LOCAL_AUTOLOGIN,
	_REQ_USERID,
	_REQ_USERNAME,
	_REQ_HAS_SESSION,
	_CFG_ACC_TIMEOUT_SESSION,
	# _ROOT_USER_ID,
)

from symbols_accounts import (
	_ID_FORM_LOGIN,
	_ID_USER_ACCOUNT,
	_ROUTE_API_CHECKIN,
	_KEY_USERID,
	_KEY_ACC_EMAIL,_KEY_ACC_TELEGRAM,
	_KEY_SIM,_KEY_OTP,_KEY_USERNAME,
	# id_user,
	_ID_UACC_EDITOR,
	_ID_UACC_EDITOR_FORM,
)

# from symbols_admin import _ROUTE_API_USERS_DELETE

_TITLE_USER_DETAILS={
	_LANG_EN:"User details",
	_LANG_ES:"Detalles del usuario"
}

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

def write_html_user_detailed(
		lang:str,
		data:Mapping,
		full:bool=False,
	)->str:

	userid=data.get(_KEY_USERID)
	username=data.get(_KEY_USERNAME)

	# html_text=(
	# 	f"<h2>{tl}</h2>"
	# )

	tl={
		_LANG_EN:"User ID",
		_LANG_ES:"ID de usuario"
	}[lang]
	html_text=(
		f"<div>{tl}: {userid}</div>"
	)

	tl={
		_LANG_EN:"Username",
		_LANG_ES:"Nombre de usuario"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"<div>{tl}: {username}</div>"
	)

	acc_email=data.get(_KEY_ACC_EMAIL)

	if acc_email is not None:
		tl={
			_LANG_EN:"Correo electrónico",
			_LANG_ES:"E-Mail account"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: {acc_email}</div>"
		)

	acc_telegram=data.get(_KEY_ACC_TELEGRAM)

	if acc_telegram is not None:
		tl={
			_LANG_EN:"ID de Telegram",
			_LANG_ES:"Telegram user ID"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: {acc_telegram}</div>"
		)

	if full:
		html_text=(
			"<div>\n"
				f"<h3>{_TITLE_USER_DETAILS[lang]}</h3>\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

# def write_button_delete_user(
# 		lang:str,
# 		userid:str,
# 		as_item:bool=True
# 	)->str:

# 	tl={
# 		_LANG_EN:"Are you sure you want to delete this user?",
# 		_LANG_ES:"¿Está seguro de que quiere eliminar este usuario?"
# 	}[lang]
# 	html_text=(
# 		f"""<button class="{_CSS_CLASS_COMMON}" """
# 			f"""hx-delete="{_ROUTE_API_USERS_DELETE}" """
# 			f"""hx-target="{_ID_MSGZONE}" """
# 			f"""hx-confirm="{tl}" """
# 			"""hx-swap="innerHTML">"""
# 	)

# 	tl={
# 		_LANG_EN:"Delete",
# 		_LANG_ES:"Eliminar"
# 	}[lang]
# 	html_text=(
# 			f"{html_text}\n"
# 			f"{tl}\n"
# 		"</button>"
# 	)

# 	return html_text

# def write_button_delete_user(
# 		lang:str,userid:str,
# 		as_item:bool=True
# 	)->str:

# 	html_text=(
# 		f"""<input type="hidden" name="{_KEY_USERID}" value="{userid}" >"""
# 	)

# 	if as_item:
# 		html_text=(
# 			f"{html_text}\n"
# 			f"""<input type="hidden" name="{_KEY_DELETE_AS_ITEM}" value="true" >"""
# 		)

# 	tl={
# 		_LANG_EN:"Delete user",
# 		_LANG_ES:"Eliminar usuario"
# 	}[lang]
# 	html_text=(
# 		f"{html_text}\n"
# 		"""<button type="submit" """
# 			f"""class="{_CSS_CLASS_COMMON} {_CSS_CLASS_DANGER}">"""
# 			f"{tl}"
# 		"</button>"
# 	)

# 	tl={
# 		_LANG_EN:"The user will be permanently deleted. Are you sure?",
# 		_LANG_ES:"El usuario será eliminado de forma permanente. ¿Está seguro?"
# 	}[lang]
# 	html_text=(
# 		f"""<form hx-delete="{_ROUTE_API_USERS_DELETE}" """
# 			f"""hx-confirm="{tl}" """
# 			f"""hx-target="#{_ID_MSGZONE}" """
# 			"""hx-trigger="submit" """
# 			"""hx-swap="innerHTML">""" "\n"

# 			f"{html_text}\n"

# 		"</form>"
# 	)

# 	return html_text

# def write_html_user_as_item(lang:str,user:Mapping)->str:

# 	userid=user.get(_KEY_USERID)

# 	html_text=(
# 		f"""<div id="{id_user(userid)}" class="{_CSS_CLASS_COMMON}">""" "\n"
# 			f"{write_html_user_asitem(lang,user,full=False)}\n"
# 			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
# 				f"{write_button_delete_user(lang,userid)}\n"
# 			"</div>\n"
# 		"</div>"
# 	)

# 	return html_text

def write_button_user_details(
		lang:str,
		userid:str
	)->str:

	tl={
		_LANG_EN:"See details",
		_LANG_ES:"Ver detalles"
	}[lang]

	html_text=(
		f"""<button class="{_CSS_CLASS_COMMON}" """
			f"""hx-get="/fgmt/accounts/details/{userid}" """
			f"""hx-target=#{_ID_MSGZONE} """
			"""hx-swap="innerHTML">"""
			f"{tl}"
		"</button>"
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
			_KEY_ACC_EMAIL,
			{
				_LANG_EN:"E-Mail",
				_LANG_ES:"Correo electrónico"
			}[lang]
		),
		(
			_KEY_ACC_TELEGRAM,
			"Telegram"
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

# def write_form_otp(
# 		lang:str,
# 		otp_id:str,
# 	)->str:

# 	# Result of /api/accounts/otp-new

# 	# Sends /api/accounts/otp-con

def write_form_login_otp(
		lang:str,
		userid:str,
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
		f"""<input name="{_KEY_USERID}" type=hidden value="{userid}">""" "\n"

		f"{write_html_input_string(_KEY_OTP,tl,maxlen=32)}"
	)

	sim_ok=False
	if sim==_KEY_ACC_EMAIL:
		sim_ok=True
		tl={
			_LANG_EN:"The generated password has been sent to your e-mail",
			_LANG_ES:"La contraseña generada ha sido enviada a su correo electrónico"
		}[lang]

	if sim==_KEY_ACC_TELEGRAM:
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
		f"""<div hx-post={_ROUTE_API_CHECKIN} hx-trigger="every {interval}s">""" "\n"
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

def write_html_user_section(
		request:Request,
		lang:str,
		full:bool=True,
	)->str:

	html_text=""

	userid:Optional[str]=request[_REQ_USERID]
	username:Optional[str]=None
	has_session=request[_REQ_HAS_SESSION]
	flag_sec_disabled=(
		_CFG_FLAG_D_SECURITY in
		request.app[_CFG_FLAGS]
	)
	logged_in=(userid is not None)

	if logged_in:
		username=request[_REQ_USERNAME]

	print(
		"uid =",userid,
		"; uname =",username,
		"; has_session =",has_session,
		"; sd =",flag_sec_disabled
	)

	if logged_in:
		html_text=(
			f"{html_text}\n"
			f"<div>{username}</div>\n"
		)
		if not flag_sec_disabled:
			if has_session:
				keep_alive_time=int(
					0.5*request.app[_CFG_ACC_TIMEOUT_SESSION]
				)
				html_text=(
					f"{html_text}\n"
					f"{write_button_logout(lang)}\n"
					f"{write_html_keepalive(keep_alive_time)}"
				)

	if not logged_in:

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

def write_form_edit_user(
		lang:str,
		userid:str,
		as_admin:bool=False,
		full:bool=True
	)->str:

	tl={
		_LANG_EN:"Username",
		_LANG_ES:"Nombre de usuario"
	}[lang]
	tl_change=f"change-{_KEY_USERNAME}"
	html_text=(

		f"""<div class="{_CSS_CLASS_INPUT_GUARDED}">""" "\n"
			f"{write_html_input_checkbox(tl_change,tl)}\n"
			f"{write_html_input_string(_KEY_USERNAME)}"
		"</div>"
	)

	tl={
		_LANG_EN:"E-Mail",
		_LANG_ES:"Correo electrónico"
	}[lang]
	tl_change=f"change-{_KEY_ACC_EMAIL}"
	html_text=(
		f"{html_text}\n"

		f"""<div class="{_CSS_CLASS_INPUT_GUARDED}">""" "\n"
			f"{write_html_input_checkbox(tl_change,tl)}\n"
			f"{write_html_input_string(_KEY_ACC_EMAIL)}"
		"</div>"
	)

	tl={
		_LANG_EN:"Telegram user",
		_LANG_ES:"Usuario de Telegram"
	}[lang]
	tl_change=f"change-{_KEY_ACC_TELEGRAM}"
	html_text=(
		f"{html_text}\n"

		f"""<div class="{_CSS_CLASS_INPUT_GUARDED}">""" "\n"
			f"{write_html_input_checkbox(tl_change,tl)}\n"
			f"{write_html_input_string(_KEY_ACC_TELEGRAM)}"
		"</div>"
	)

	tl={
		_LANG_EN:"Apply changes",
		_LANG_ES:"Aplicar cambios"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
			f"{write_button_submit(tl)}\n"
		"</div>\n"
	)


	req_url={
		True:f"/api/admin/users/{userid}/edit",
		False:"/api/accounts/apply-changes"
	}[as_admin]

	html_text=(
		f"""<form hx-post="{req_url}" """ "\n"
			f"""hx-target="#{_ID_MSGZONE}" """ "\n"
			"""hx-swap="innerHTML">""" "\n"

			f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
				f"{html_text}\n"
			"</div>\n"
		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"Edit user account",
			_LANG_ES:"Editar cuenta de usuario"
		}[lang]
		html_text=(
			f"""<details id="{_ID_UACC_EDITOR}">""" "\n"
				f"<summary>{tl}</summary>\n"
				f"""<div id={_ID_UACC_EDITOR_FORM}>""" "\n"
					f"{html_text}\n"
				"</div>"
			"</details>"
		)

	return html_text

