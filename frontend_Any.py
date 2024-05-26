#!/usr/bin/python3.9

_LANG_EN="en"
_LANG_ES="es"

_MBTN_BACK="""<a href="/">Back to homepage</a>"""

def write_popupmsg(html_content:str)->str:
	return (
		"""<div class="popup-background">""" "\n"
			"""<div class="popup-area">""" "\n"
				"""<div class="popup-body">""" "\n"
					"""<div class="popup-content">""" "\n"
						f"{html_content}"
					"</div>\n"
					"""<div class="popup-button-area">""" "\n"
						"""<button class="popup-button" onclick="this.parentElement.parentElement.parentElement.parentElement.style.display='none';">""" "\n"
							"<!-- × -->"
							"<strong>OK</strong>"
						"</button>\n"
					"</div>\n"
				"</div>\n"
			"</div>\n"
		"</div>\n"
	)

def write_popupmsg_oob(
		html_content:str,
		oob_target:str="messages"
	)->str:

	return (
		f"""<section hx-swap-oob="innerHTML:{oob_target}">"""
			f"{write_popupmsg(html_content)}"
		"</section>"
	)

def write_fullpage(
		lang:str,
		html_title_inner:str,
		html_body_inner:str,
		html_header_extra:list=[],
		# html_style_outer:str="",
		# html_script_outer:str="",
		# html_links:str=""
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

	# if not len(html_style_outer)==0:
	# 	html_page=f"{html_page}\n{html_style_outer}"

	# if not len(html_script_outer)==0:
	# 	html_page=f"{html_page}{html_script_outer}"

	# if not len(html_links)==0:
	# 	html_page=f"{html_page}\n{html_links}"

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
