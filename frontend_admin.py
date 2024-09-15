#!/usr/bin/python3.9

from frontend_Any import _LANG_EN,_LANG_ES

from frontend_Any import _CSS_CLASS_COMMON
from frontend_Any import _CSS_CLASS_HORIZONTAL

def write_form_update_config(lang:str)->str:

	tl={
		_LANG_EN:"Change configuration",
		_LANG_ES:"Cambiar configuración"
	}[lang]
	html_text=(
		f"<h2>{tl}</h2>"
		"<form "
			"""hx-post="/api/admin/update-config" """
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
		f"<h3>{tl}</h3>\n"
		"<div>"
	)

	lang_table=[
		(_LANG_EN,"English"),
		(_LANG_ES,"Español")
	]

	for row in lang_table:
		chk=""
		if lang==row[0]:
			chk=" checked"
		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"""<input id="lang-{row[0]}" """
					"""name="lang" """
					f"""value="{row[0]}" """
					f"""type="radio"{chk} """
					">\n"
				f"""<label for="lang-{row[0]}">{row[1]}</label>""" "\n"
			"</div>"
		)

	html_text=(
			f"{html_text}\n"
		"</div>"
	)

	# NOTE: <input> min and max attrs are not good for this form
	tl={
		_LANG_EN:"Port number",
		_LANG_ES:"Puerto"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"<h3>{tl}</h3>\n"
		"<div>\n"
			f"""<input class="{_CSS_CLASS_COMMON}" """
				""" name="port" """
				"""type="number" """
				"""value=0 """
				">\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Apply changes",
		_LANG_ES:"Aplicar cambios"
	}[lang]

	return (
			f"{html_text}\n"

			"""<button """
				"""type="submit" """
				f"""class="{_CSS_CLASS_COMMON}" """
				">"
				f"{tl}"
			"</button>" "\n"

		"</form>"
	)

def write_button_update_known_asset_names(lang:str)->str:

	tl={
		_LANG_EN:"Update known asset names",
		_LANG_ES:"Actualizar nombres de activos conocidos"
	}[lang]
	html_text=f"<h2>{tl}</h2>"

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
			"""hx-post="/api/admin/update-known-assets" """
			"""hx-swap="innerHTML" """
			"""hx-target="#messages" """
			">\n"
			f"{tl}"
		"</button>"
	)

