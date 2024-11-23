#!/usr/bin/python3.9

_LANG_EN="en"
_LANG_ES="es"

_CSS_CLASS_TITLE_UNIQUE="title-uniq"
_CSS_CLASS_TITLE="title"

_CSS_CLASS_COMMON="common"
_CSS_CLASS_HORIZONTAL="horizontal"

_CSS_CLASS_DANGER="danger"

_SCRIPT_HTMX="""<script src="/src/local/htmx.min.js"></script>"""
_SCRIPT_HYPERSCRIPT="""<script src="/src/local/hyperscript.js"></script>"""

_STYLE_CUSTOM="""<link rel="stylesheet" href="/src/local/custom.css">"""
_STYLE_POPUP="""<link rel="stylesheet" href="/src/baked/popup.css">"""

_STYLE_POPUP_CONTENTS="""
div.popup-background {

	/*
		PLEASE DON'T TOUCH ANY OF THIS
		UNLESS YOU KNOW WHAT YOU'RE DOING
	*/

	z-index:999;
	position:fixed;
	top:0;
	left:0;
	width:100vw;
	height:100vh;

	display:grid;
	grid-template-columns:1fr 0.75fr 1fr;
	grid-template-rows:1fr 1fr 1fr;

	background-color:rgba(0, 0, 0, 0.5);
}

div.popup-area {

	/*
		PLEASE DON'T TOUCH ANY OF THIS
		UNLESS YOU KNOW WHAT YOU'RE DOING
	*/

	grid-column:2/3;
	grid-row:2/3;
}

/* EVERYTHING BELOW THIS LINE IS SAFE TO OVERRIDE ON THE 'CUSTOM.CSS' FILE */

div.popup-body {

	color:black;
	border:1px solid black;
	background-color:white;
}

div.popup-button-area {text-align: center;}
.popup-centered {text-align: center;}
"""

def write_button_anchor(label:str,link:str)->str:

	return (
		"<div>\n"
			f"""<button class="{_CSS_CLASS_COMMON}" """
				f"""onclick="location.href='{link}'" """
				">"
				f"{label}"
			"</button>" "\n"

			# f"""<form action="{link}">""" "\n"
			# 	f"""<button class="{_CSS_CLASS_COMMON}">"""
			# 		f"{label}"
			# 	"</button>" "\n"
			# "</form>\n"

		"</div>"
	)

def write_link_homepage(lang:str)->str:

	return write_button_anchor(
		{
			_LANG_EN:"Back to homepage",
			_LANG_ES:"Volver a la página principal"
		}[lang],
		"/"
	)

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

def write_fullpage(
		lang:str,
		html_title:str,
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
				f"<title>{html_title}</title>\n"
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
		"</div>"
	)

