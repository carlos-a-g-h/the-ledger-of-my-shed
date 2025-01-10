#!/usr/bin/python3.9

from typing import Optional

from dbi_accounts import (
	_KEY_EMAIL,_KEY_TELEGRAM,
	_KEY_VM,_KEY_OTP,_KEY_USERNAME
)

from symbols_Any import _LANG_EN,_LANG_ES

from frontend_Any import (
	_CSS_CLASS_COMMON,_CSS_CLASS_HORIZONTAL,
	write_button_anchor
)

_ID_FORM_LOGIN="form-login"
_ID_USER_SECTION="section-user"

def write_link_account(lang:str,return_there:bool=False)->str:

	return write_button_anchor(
		{
			_LANG_EN:{
				True:"Return to account page",
				False:"Account"
			}[return_there],
			_LANG_ES:{
				True:"Volver a la página de la cuenta",
				False:"Cuenta"
			}[return_there],
		}[lang],
		"/page/accounts"
	)

def write_form_login(lang:str,full:bool=True)->str:

	# Sends: POST /api/accounts/login {username:String,vmethod:String}

	html_text=(
		"""<form """
			"""hx-post="/api/accounts/login" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">"
	)

	tl={
		_LANG_EN:"Username",
		_LANG_ES:"Nombre de usuario"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"<div>{tl}</div>\n"
		"<div>"
			f"""<input name="username" type=text class={_CSS_CLASS_COMMON} required>"""
		"</div>"
	)

	tl={
		_LANG_EN:"Verification method",
		_LANG_ES:"Método de verificación"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"<div>{tl}</div>\n"

		"<div>\n"
			"<div>\n"
				f"""<input id=vm-email name="{_KEY_VM}" type=radio value="{_KEY_EMAIL}" checked>""" "\n"
				"""<label for="vm-email">E-Mail</label>""" "\n"
			"</div>"
			"<div>\n"
				f"""<input id=vm-telegram name="{_KEY_VM}" type=radio value="{_KEY_TELEGRAM}">""" "\n"
				"""<label for="vm-telegram">Telegram</label>""" "\n"
			"</div>\n"
			"<div>\n"
				f"""<input id=vm-none name="{_KEY_VM}" type=radio value="">""" "\n"
				"""<label for="vm-none">Backend/Local</label>""" "\n"
			"</div>"
		"</div>"
	)

	tl={
		_LANG_EN:"Next",
		_LANG_ES:"Siguiente"
	}[lang]
	html_text=(
			f"{html_text}\n"
			f"""<button class="{_CSS_CLASS_COMMON}" type=submit>{tl}</button>""" "\n"
		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"Session login",
			_LANG_ES:"Inicio de sesión"
		}[lang]
		html_text=(
			f"<h3>{tl}</h3>\n"
			f"""<div id="{_ID_FORM_LOGIN}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_form_otp(
		lang:str,
		username:str,
		vmethod:Optional[str]=None,
		full:bool=True,
	)->str:

	# Sends: POST /api/accounts/login-otp {username:String,otp:String}

	# NOTE: The form leads to a full page or a redirect, so I can't use HTMX here
	# html_text=(
	# 	"""<form """
	# 		"""hx-post="/api/accounts/login-otp" """
	# 		"""hx-target="#messages" """
	# 		"""hx-swap="innerHTML" """
	# 		">"
	# )

	html_text=(
		"""<form method="POST" """
			"""action="/api/accounts/login-otp" """
			">"
	)

	tl={
		_LANG_EN:"Enter the generated password",
		_LANG_ES:"Introduzca la contraseña generada"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"<div>{tl}</div>\n"
		"<div>\n"
			f"""<input name="{_KEY_USERNAME}" type=hidden value="{username}">""" "\n"
			f"""<input name="{_KEY_OTP}" type=text class={_CSS_CLASS_COMMON} required>"""
		"</div>"
	)

	tl={
		_LANG_EN:"Confirm",
		_LANG_ES:"Confirmar"
	}[lang]
	html_text=(
			f"{html_text}\n"
			f"""<button class="{_CSS_CLASS_COMMON}" type=submit>{tl}</button>"""
		"</form>"
	)

	if vmethod is not None:

		known=False

		tl=""

		if vmethod==_KEY_EMAIL:
			known=True
			tl={
				_LANG_EN:"The generated password has been sent to your e-mail",
				_LANG_ES:"La contraseña generada fue enviada a su correo electrónico"
			}[lang]

		if vmethod==_KEY_TELEGRAM:
			known=True
			tl={
				_LANG_EN:"The generated password has been sent to you through the Telegram bot",
				_LANG_ES:"La contraseña generada ha sido enviada a través del bot de Telegram"
			}[lang]

		if not known:

			known=True
			tl={
				_LANG_EN:"The generated password has been sent through other means",
				_LANG_ES:"La contraseña generada ha sido enviada por otros medios"
			}[lang]

		html_text=(
			f"{html_text}\n"
			f"<div>{tl}</div>"
		)

	if full:
		tl={
			_LANG_EN:"Session login (OTP)",
			_LANG_ES:"Inicio de sesión (OTP)"
		}[lang]
		html_text=(
			f"<h3>{tl}</h3>\n"
			f"""<div id="session-login">""" "\n"
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
			f"""<button class="{_CSS_CLASS_COMMON}" type=submit>{tl}</button>""" "\n"
		"</form>"
	)

def write_button_logout(lang:str)->str:

	# Sends: DELETE /api/accounts/logout {username:String}

	tl={
		_LANG_EN:"Are you sure you want to logout?",
		_LANG_ES:"¿Seguro que quieres cerrar sesión?"
	}[lang]
	html_text=(
		"""<form """
			"""hx-delete="/api/accounts/logout" """
			"""hx-target="#messages" """
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
			# f"""<input name="username" type=hidden value={username}>""" "\n"
			f"""<button class="{_CSS_CLASS_COMMON}" type=submit>{tl}</button>""" "\n"
		"</form>"
	)

	return html_text

def write_html_user_section(
		lang:str,
		username:Optional[str]=None,
		full:bool=True
	)->str:

	html_text=""

	user_ok=(isinstance(username,str))

	if not user_ok:
		html_text=(
			f"{html_text}\n"
			"<!-- THERE IS NO USER -->"
		)

	if user_ok:

		tl={
			_LANG_EN:"User",
			_LANG_ES:"Usuario"
		}[lang]

		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"<h3>{tl}: {username}</h3>\n"
			"""</div>""" "\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"{write_button_logout(lang)}\n"
			"""</div>"""
		)

	if full:
		html_text=(
			f"""<section id="{_ID_USER_SECTION}">""" "\n"
				f"{html_text}\n"
			"""</section>"""
		)

	return html_text
