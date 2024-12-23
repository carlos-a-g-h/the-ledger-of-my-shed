#!/usr/bin/python3.9

from symbols_Any import (
	_LANG_EN,_LANG_ES,
	_CFG_PORT_MIN,_CFG_PORT_MAX,
	_CFG_LANG,_CFG_PORT
)

from frontend_Any import (
	_CSS_CLASS_COMMON,_CSS_CLASS_CONTROLS,
	_CSS_CLASS_HORIZONTAL,
	_CSS_CLASS_VUP,
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
		# f"""<div class="{_CSS_CLASS_VDOWN}"><strong>{tl}</strong></div>""" "\n"
		"<form "
			"""hx-post="/api/admin/users/new-user" """
			"""hx-trigger="submit" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"
			"<div>"
	)

	tl={
		_LANG_EN:"Username",
		_LANG_ES:"Nombre de usuario"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
			f"""<label class="{_CSS_CLASS_COMMON}" for="username">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					"""name="username" """
					"""type="text" """
					"""max-length=16 """
					"required>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"E-Mail",
		_LANG_ES:"Correo electrónico"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
			f"""<label class="{_CSS_CLASS_COMMON}" for="email">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					"""name="email" """
					"""type="email" """
					"""max-length=16 """
					"required>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Telegram User ID",
		_LANG_ES:"ID de usuario de Telegram"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
			f"""<label class="{_CSS_CLASS_COMMON}" for="telegram">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					"""name="telegram" """
					"""type="text" """
					"""max-length=32 """
					"required>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Create",
		_LANG_ES:"Crear"
	}[lang]
	html_text=(
				f"{html_text}\n"
			"</div>\n"
			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"""<button type="submit" """
					f"""class="{_CSS_CLASS_COMMON}">""" "\n"
						f"{tl}\n"
				"</button>" "\n"
			"</div>\n"
		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"User creation",
			_LANG_ES:"Creación de usuario"
		}[lang]
		html_text=(
			f"<h3>{tl}</h3>\n"
			"""<div id="user-creation">""" "\n"
				f"{html_text}\n"
			"</div>\n"
			"""<div id="user-creation-result">""" "\n"
				"<!-- CREATED USERS GO HERE -->\n"
			"</div>"
		)

	return html_text

def write_form_search_users(
		lang:str,full:bool=True
	)->str:

	# POST: /api/admin/users/search

	html_text=(
		"<form "
			"""hx-post="/api/admin/users/search" """
			"""hx-trigger="submit" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"
			"<div>"
	)

	tl={
		_LANG_EN:"Username",
		_LANG_ES:"Nombre de usuario"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
			f"""<label class="{_CSS_CLASS_COMMON}" for="username">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					"""name="username" """
					"""type="text" """
					"""max-length=16 """
					"required>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"E-Mail",
		_LANG_ES:"Correo electrónico"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
			f"""<label class="{_CSS_CLASS_COMMON}" for="email">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					"""name="email" """
					"""type="email" """
					"""max-length=16 """
					"required>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Telegram User ID",
		_LANG_ES:"ID de usuario de Telegram"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
			f"""<label class="{_CSS_CLASS_COMMON}" for="telegram">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					"""name="telegram" """
					"""type="text" """
					"""max-length=32 """
					"required>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Search",
		_LANG_ES:"Buscar"
	}[lang]
	html_text=(
				f"{html_text}\n"
			"</div>\n"
			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"""<button type="submit" """
					f"""class="{_CSS_CLASS_COMMON}">""" "\n"
						f"{tl}\n"
				"</button>\n"
			"</div>\n"
		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"User search",
			_LANG_ES:"Búsqueda de usuarios"
		}[lang]
		html_text=(
			f"<h3>{tl}</h3>\n"
			"""<div id="user-search">""" "\n"
				f"{html_text}\n"
			"</div>\n"
			"""<div id="user-search-result">""" "\n"
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

	tl={
		_LANG_EN:"Language",
		_LANG_ES:"Idioma"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"<!-- LANG CONFIG -->\n"
		f"""<div class={_CSS_CLASS_VUP}>""" "\n"
			"<div>\n"
				f"""<input name="change-lang" type=checkbox>""" "\n"
				f"""<label for=change-lang>{tl}</label>""" "\n"
			"</div>\n"
			"<div>"
	)

	for row in [
		(_LANG_EN,"English"),
		(_LANG_ES,"Español")
	]:
		chk=""
		if lang==row[0]:
			chk=" checked"

		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"""<input id="lang-{row[0]}" """
					f"""name="{_CFG_LANG}" """
					f"""value="{row[0]}" """
					f"""type="radio"{chk} """
					">\n"
				f"""<label for="lang-{row[0]}">{row[1]}</label>""" "\n"
			"</div>"
		)

	html_text=(
				f"{html_text}\n"
			"</div>"
		"</div>"
	)

	tl={
		_LANG_EN:"Port number",
		_LANG_ES:"Puerto"
	}[lang]
	html_text=(
		f"{html_text}\n"

		"<!-- PORT CONFIG -->\n"

		f"""<div class={_CSS_CLASS_VUP}>""" "\n"
			"<div>\n"
				f"""<input name="change-port" type=checkbox>""" "\n"
				f"""<label for=change-port>{tl}</label>""" "\n"
			"</div>\n"
			"<div>\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					f""" name="{_CFG_PORT}" """
					"""type="number" """
					"""value=1024 """
					f"""min={_CFG_PORT_MIN} """
					f"""max={_CFG_PORT_MAX} """
					">\n"
			"</div>"
		"</div>\n"
	)

	tl={
		_LANG_EN:"Apply changes",
		_LANG_ES:"Aplicar cambios"
	}[lang]

	html_text=(
			f"{html_text}\n"

			"<!-- APPLY CHANGES -->\n"

			"""<button """
				"""type="submit" """
				f"""class="{_CSS_CLASS_COMMON}" """
				">"
				f"{tl}"
			"</button>" "\n"

		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"Server configuration",
			_LANG_ES:"Configuración del servidor"
		}[lang]
		html_text=(
			f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
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
		f"""<div id="admin-asset-names" """
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

