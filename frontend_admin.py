#!/usr/bin/python3.9

from symbols_Any import _LANG_EN,_LANG_ES
from symbols_Any import _PORT_MIN,_PORT_MAX
from symbols_Any import _CFG_LANG,_CFG_PORT

from frontend_Any import _CSS_CLASS_COMMON
from frontend_Any import _CSS_CLASS_HORIZONTAL
from frontend_Any import _CSS_CLASS_VUP

def write_button_nav_users(lang:str)->str:
	tl={
		_LANG_EN:"Users",
		_LANG_ES:"Usuarios"
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
					f"""min={_PORT_MIN} """
					f"""max={_PORT_MAX} """
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

