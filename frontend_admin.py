#!/usr/bin/python3.9

from frontend_Any import _LANG_EN,_LANG_ES

_LABEL_APPLY={
	_LANG_EN:"Apply",
	_LANG_ES:"Aplicar"
}

def write_form_update_config(lang:str)->str:

	html_text=(
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
	chk=""
	if lang==_LANG_EN:
		chk=" checked"
	html_text=(
		f"{html_text}\n"
		# """<div class="common">"""
		"<div>"
			f"<h3>{tl}</h3>\n"
			"""<div class="hcontainer">""" "\n"
				f"""<input id="lang-{_LANG_EN}" """
					"""name="lang" """
					f"""value="{_LANG_EN}" """
					f"""type="radio"{chk} """
					">\n"
				f"""<label for="lang-{_LANG_EN}">English</label>""" "\n"
			"</div>"
	)

	chk=""
	if lang==_LANG_ES:
		chk=" checked"
	html_text=(
		f"{html_text}\n"
			"""<div class="hcontainer">""" "\n"
				f"""<input id="lang-{_LANG_ES}" """
					"""name="lang" """
					f"""value="{_LANG_ES}" """
					f"""type="radio"{chk} """
					">\n"
				f"""<label for="lang-{_LANG_ES}">Español</label>""" "\n"
			"</div>\n"
		"</div>\n"
	)

	# NOTE: <input> min and max are not a good idea
	tl={
		_LANG_EN:"Port number",
		_LANG_ES:"Puerto"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"<div>\n"
			f"<h3>{tl}</h3>\n"
			# """<label style="display:block;" """
			# 	f"""for="port-number">{tl}</label>""" "\n"
			"""<input class="common" """
				"""id="port-number" """
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
				"""class="common" """
				">"
				f"{tl}"
			"</button>"
		"</form>"
	)

def write_button_update_known_item_names(lang:str)->str:

	tl={
		_LANG_EN:"Update",
		_LANG_ES:"Actualizar"
	}[lang]

	return (
		"""<button class="common" """
			"""hx-post="/api/admin/update-known-items" """
			"""hx-swap="innerHTML" """
			"""hx-target="#messages" """
			">\n"
			f"{tl}"
		"</button>"
	)

