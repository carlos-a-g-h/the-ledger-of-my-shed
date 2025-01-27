#!/usr/bin/python3.9

from symbols_Any import (
	_LANG_EN,_LANG_ES,
	_CFG_PORT_MIN,_CFG_PORT_MAX,
	_CFG_LANG,_CFG_PORT
)

from symbols_admin import (
	_ID_MISC_SETTINGS,
	_ID_UPDATE_ASSET_NAMES,
	_ID_CREATE_USER,
	_ID_SEARCH_USER,
)

from symbols_accounts import (
	# _KEY_USERID,
	_KEY_USERNAME,

	_KEY_EMAIL,
	_KEY_TELEGRAM
)

from frontend_Any import (

	_CSS_CLASS_COMMON,
	_CSS_CLASS_CONTROLS,

	_CSS_CLASS_IG_FIELDS,

	write_button_submit,

	write_html_input_radio,
	write_html_input_string,
	write_html_input_checkbox,
	write_html_input_number
)

def write_button_nav_users(lang:str)->str:
	tl={
		_LANG_EN:"Users control panel",
		_LANG_ES:"Panel de control de usuarios"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			"""hx-get="/fgmt/admin/users" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML">"""
			f"{tl}"
		"</button>"
	)

def write_button_nav_misc_settings(lang:str)->str:
	tl={
		_LANG_EN:"Misc settings",
		_LANG_ES:"Ajustes varios"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			"""hx-get="/fgmt/admin/misc" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML">"""
			f"{tl}"
		"</button>"
	)

def write_form_create_user(
		lang:str,full:bool=True
	)->str:

	# POST: /api/admin/users/new-user

	html_text=(
		"<form "
			"""hx-post="/api/admin/users/new-user" """
			"""hx-trigger="submit" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"

			f"""<div class="{_CSS_CLASS_IG_FIELDS}">"""
	)

	tl={
		_LANG_EN:"Username",
		_LANG_ES:"Nombre de usuario"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_USERNAME,label=tl,maxlen=24,input_type=1)}"
	)

	tl={
		_LANG_EN:"E-Mail",
		_LANG_ES:"Correo electrónico"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_EMAIL,label=tl,maxlen=24,input_type=1)}"
	)

	tl={
		_LANG_EN:"Telegram User ID",
		_LANG_ES:"ID de usuario de Telegram"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_TELEGRAM,label=tl,maxlen=24)}"
	)

	tl={
		_LANG_EN:"Create",
		_LANG_ES:"Crear"
	}[lang]
	html_text=(
				f"{html_text}\n"
			"</div>\n"

			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_submit(tl)}\n"
			"</div>\n"
		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"User creation",
			_LANG_ES:"Creación de usuario"
		}[lang]
		html_text=(
			"<div>\n"
				f"<h3>{tl}</h3>\n"

				"""<p style="color:red;">THIS FEATURE IS NOT READY YET</p>""" "\n"

				f"""<div id="{_ID_CREATE_USER}">""" "\n"
					f"{html_text}\n"
				"</div>\n"
			"</div>\n"
			f"""<div id="{_ID_CREATE_USER}-results">""" "\n"
				"<!-- CREATED USERS GO HERE -->\n"
			"</div>"
		)

	return html_text

def write_form_search_users(
		lang:str,
		full:bool=True
	)->str:

	# POST: /api/admin/users/search

	html_text=(
		"<form "
			"""hx-post="/api/admin/users/search" """
			"""hx-trigger="submit" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"
			f"""<div class="{_CSS_CLASS_IG_FIELDS}">"""
	)

	tl={
		_LANG_EN:"Username",
		_LANG_ES:"Nombre de usuario"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_USERNAME,label=tl,maxlen=24,input_type=1)}"
	)

	tl={
		_LANG_EN:"E-Mail",
		_LANG_ES:"Correo electrónico"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_EMAIL,label=tl,maxlen=24,input_type=1)}"
	)

	tl={
		_LANG_EN:"Telegram User ID",
		_LANG_ES:"ID de usuario de Telegram"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_TELEGRAM,label=tl,maxlen=24)}"
	)

	tl={
		_LANG_EN:"Search",
		_LANG_ES:"Buscar"
	}[lang]
	html_text=(
				f"{html_text}\n"
			"</div>\n"

			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_submit(tl)}\n"
			"</div>\n"
		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"User search",
			_LANG_ES:"Buscador de usuario(s)"
		}[lang]
		html_text=(
			"<div>\n"
				f"<h3>{tl}</h3>\n"

				"""<p style="color:red;">THIS FEATURE IS NOT READY YET</p>""" "\n"

				f"""<div id="{_ID_SEARCH_USER}">""" "\n"
					f"{html_text}\n"
				"</div>\n"
			"</div>\n"
			f"""<div id="{_ID_SEARCH_USER}-result">""" "\n"
				"<!-- USERS FOUND GO HERE -->\n"
			"</div>"
		)

	return html_text

def write_form_update_config(
		lang:str,
		full:bool=True
	)->str:

	# POST: /api/admin/misc/change-config
	# {
	# 	change-lang:bool,
	# 	lang:str,
	# 	change-port:bool,
	# 	port:int
	# }

	html_text=(
		"<form "
			"""hx-post="/api/admin/misc/change-config" """
			"""hx-trigger="submit" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"
	)

	lang_radio_opts=[
		(_LANG_EN,"English"),
		(_LANG_ES,"Español")
	]
	tl={
		_LANG_EN:"Language",
		_LANG_ES:"Idioma"
	}[lang]
	tl_ch=f"change-{_CFG_LANG}"
	html_text=(
		f"{html_text}\n"

		"<!-- LANG CONFIG -->\n"

		# f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
		"<div>\n"
			f"{write_html_input_checkbox(tl_ch,tl)}\n"
			f"{write_html_input_radio(_CFG_LANG,lang_radio_opts)}"
		"</div>"
	)

	tl={
		_LANG_EN:"Port number",
		_LANG_ES:"Puerto"
	}[lang]
	tl_ch=f"change-{_CFG_PORT}"
	html_text=(
		f"{html_text}\n"

		"<!-- PORT CONFIG -->\n"

		# f"""<div class="{_CSS_CLASS_COMMON}">"""
		"<div>\n"
			f"{write_html_input_checkbox(tl_ch,tl)}\n"
			"<div>\n"
				f"{write_html_input_number(_CFG_PORT,value=_CFG_PORT_MIN,minimum=_CFG_PORT_MIN,maximum=_CFG_PORT_MAX)}\n"
			"</div>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Apply changes",
		_LANG_ES:"Aplicar cambios"
	}[lang]

	html_text=(
			f"{html_text}\n"

			"<!-- APPLY CHANGES -->\n"

			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_submit(tl)}\n"
			"</div>\n"

		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"Server configuration",
			_LANG_ES:"Configuración del servidor"
		}[lang]
		html_text=(
			f"""<div id="{_ID_MISC_SETTINGS}" class="{_CSS_CLASS_COMMON}">""" "\n"
				f"<h3>{tl}</h3>\n"
				f"""<div id="admin-config">""" "\n"
					f"{html_text}\n"
				"</div>"
			"</div>"
		)

	return html_text

def write_button_update_known_asset_names(lang:str)->str:

	tl={
		_LANG_EN:"Update known asset names",
		_LANG_ES:"Actualizar nombres de activos conocidos"
	}[lang]
	html_text=(
		f"""<div id="{_ID_UPDATE_ASSET_NAMES}" """
			f"""class="{_CSS_CLASS_COMMON}" """
			">\n"
			f"<h3>{tl}</h3>"
	)

	tl={
		_LANG_EN:"Do this only if the asset definitions were modified recently by external means",
		_LANG_ES:"Haga esto solamente si las definiciones de los activos han sido modificadas recientemente usando aplicaciones externas"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"<p>{tl}</p>"
	)

	tl={
		_LANG_EN:"Update",
		_LANG_ES:"Actualizar"
	}[lang]
	return (
			f"{html_text}\n"
			"""<button class="common" """
				"""hx-post="/api/admin/misc/update-known-assets" """
				"""hx-swap="innerHTML" """
				"""hx-target="#messages" """
				">\n"
				f"{tl}"
			"</button>\n"
		"</div>"
	)

