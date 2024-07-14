#!/usr/bin/python3.9

_LANG_EN="en"
_LANG_ES="es"

_CSS_CLASS_COMMON="common"
_CSS_CLASS_HORIZONTAL="horizontal"

# _CSS_CLASS_BUTTON="button"
_CSS_CLASS_DANGER="danger"
# _CSS_CLASS_INPUT_TEXT="input-text"

def write_link_homepage(lang:str):
	text={
		_LANG_EN:"Back to homepage",
		_LANG_ES:"Volver a la página principal"
	}[lang]
	return f"""<a class="{_CSS_CLASS_COMMON}" href="/">- {text} -</a>"""

def write_popupmsg(html_content:str)->str:
	return (
		"""<div class="popup-background">""" "\n"
			"""<div class="popup-area">""" "\n"
				"""<div class="popup-body">""" "\n"
					"""<div class="popup-content">""" "\n"
						f"{html_content}\n"
					"</div>\n"
					"""<div class="popup-button-area">""" "\n"
						"""<button class="popup-button" onclick="this.parentElement.parentElement.parentElement.parentElement.style.display='none';">""" "\n"
							"<!-- × -->"
							"<strong>OK</strong>"
						"</button>\n"
					"</div>\n"
				"</div>\n"
			"</div>\n"
		"</div>"
	)

def write_popupmsg_oob(
		html_content:str,
		oob_target:str="messages"
	)->str:

	return (
		f"""<section hx-swap-oob="innerHTML:{oob_target}">""" "\n"
			f"{write_popupmsg(html_content)}\n"
		"</section>"
	)

def write_fullpage(
		lang:str,
		html_title_inner:str,
		html_body_inner:str,
		html_header_extra:list=[],
	)->str:

	html_page=(
		"<!DOCTYPE html>\n"
			f"""<html lang="{lang}">""" "\n"
				"<head>\n"
					"""<meta charset="UTF-8" />""" "\n"
						"""<meta name="viewport" content="width=device-width,initial-scale=1.0" />""" "\n"
	)

	for thing in html_header_extra:
		html_page=f"{html_page}\n{thing}"

	return (
					f"{html_page}\n"
				f"<title>{html_title_inner}</title>\n"
			"</head>\n"
			"<body>\n"
				f"{html_body_inner}\n"
			"</body>\n"
		"</html>"
	)

def write_ul(
		list_of_things:list
	)->str:

	if len(list_of_things)==0:
		return ""

	html_text="<ul>\n"

	for thing in list_of_things:
		html_text=(
			f"{html_text}"
			"<li>\n"
				f"{thing}\n"
			"</li>\n"
		)

	return (
			f"{html_text}"
		"</ul>"
	)

def write_div_display_error(lang:str)->str:
	html_text=(
		"""<div class="display-error">""" "\n"
	)

	html_text=f"{html_text}"+{
		_LANG_EN:"Display error",
		_LANG_ES:"Error al mostrar"
	}[lang]

	return (
			f"{html_text}\n"
		"<div>"
	)

