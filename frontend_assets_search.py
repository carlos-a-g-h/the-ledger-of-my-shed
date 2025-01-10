#!/usr/bin/python3.9

# from typing import Mapping
from typing import Optional

from symbols_Any import (
	_LANG_EN,_LANG_ES,
	_KEY_TAG,
	_KEY_SIGN,
	# _KEY_DATE,
)

from frontend_Any import (

	_ID_MESSAGES,

	_CSS_CLASS_COMMON,
	_CSS_CLASS_CONTROLS,
	_CSS_CLASS_HORIZONTAL,
)

from symbols_assets import(
	_KEY_NAME,
	_ID_FORM_SEARCH_ASSETS,
	_ID_RESULT_SEARCH_ASSETS,
)

_KEY_GET_VALUE="get_value"
_KEY_GET_TOTAL="get_total"

def write_form_search_assets(
		lang:str,
		order_id:Optional[str]=None,
		authorized:bool=True,
		full:bool=True,
	)->str:

	order_specific=isinstance(order_id,str)

	the_route={
		True:f"/api/orders/current/{order_id}/search-assets",
		False:"/api/assets/search-assets"
	}[order_specific]

	html_text=(
		f"""<form hx-post="{the_route}" """
			"""hx-trigger="submit" """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML" """
			">\n"

			# NOTE: fields start
			"""<div class="hc">"""
	)

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=(
		f"{html_text}"
		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
			f"""<label class="{_CSS_CLASS_COMMON}" for="{_KEY_NAME}">{tl}</label>"""
			"\n"
			f"""<input class="{_CSS_CLASS_COMMON}" """
				f"""name="{_KEY_NAME}" """
				"""type="text" """
				"""max-length=32 """
				">\n"
		"</div>"
	)

	if authorized:
		tl={
			_LANG_EN:"Sign (User ID)",
			_LANG_ES:"Firma (ID de Usuario)"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"""<label class="{_CSS_CLASS_COMMON}" for="{_KEY_SIGN}">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					f"""name="{_KEY_SIGN}" """
					"""type="text" """
					"""max-length=32 """
					">\n"
			"</div>"
		)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
			f"""<label class="{_CSS_CLASS_COMMON}" for="{_KEY_TAG}">{tl}</label>"""
			"\n"
			f"""<input class="{_CSS_CLASS_COMMON}" """
				f"""name="{_KEY_TAG}" """
				"""type="text" """
				"""max-length=32 """
				">\n"
		"</div>"
	)

	html_text=(
			f"{html_text}\n"
		"</div>"
		# NOTE: fields end
	)

	if authorized:

		print("AUTHORIZED!")

		html_text=(
			f"{html_text}\n"

			# NOTE: fields start
			"<div>"
		)

		tl={
			_LANG_EN:"Include value",
			_LANG_ES:"Incluir valor"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					f"""name="{_KEY_GET_VALUE}" """
					"""type="checkbox" """
					# """checked"""
					">\n"
				f"""<label for="{_KEY_GET_VALUE}">{tl}</label>""" "\n"
			"</div>"
		)

		tl={
			_LANG_EN:"Include total",
			_LANG_ES:"Incluir total"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					f"""name="{_KEY_GET_TOTAL}" """
					"""type="checkbox" """
					# """checked"""
					">\n"
				f"""<label for="{_KEY_GET_TOTAL}">{tl}</label>""" "\n"
			"</div>"
		)

		html_text=(
			f"{html_text}\n"

			# NOTE: fields end
			"</div>"
		)

	tl={
		_LANG_EN:"Perform search",
		_LANG_ES:"Realizar búsqueda"
	}[lang]
	html_text=(
			f"{html_text}\n"

			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				"""<button type="submit" """
					f"""class="{_CSS_CLASS_COMMON}" """
					">"
					f"{tl}"
				"</button>\n"
			"</div>\n"
		"</form>"
	)

	if full:

		tl={
			_LANG_EN:"Asset searcher",
			_LANG_ES:"Buscador de activos"
		}[lang]

		html_text=(
			f"<h3>{tl}</h3>\n"
			f"""<div id={_ID_FORM_SEARCH_ASSETS}>""" "\n"
				f"{html_text}\n"
			"</div>\n"
			f"""<div id={_ID_RESULT_SEARCH_ASSETS}>""" "\n"
				"<!-- SEARCH RESULTS GO HERE -->\n"
			"</div>"
		)

	if order_specific:
		html_text=(
			f"<!-- ASSET SEARCH FOR ORDER {order_id} -->\n"
			f"{html_text}"
		)

	if not order_specific:
		html_text=(
			f"<!-- GENERIC ASSET SEARCH -->\n"
			f"{html_text}"
		)

	return html_text

# def write_html_list_of_assets(
# 		lang:str,assets_list:list,
# 		order_id:Optional[str]=None
# 	)->str:

# 	html_text="""<div id="list-of-assets">"""

# 	empty=(len(assets_list)==0)

# 	if empty:
# 		tl={
# 			_LANG_EN:"There are no assets",
# 			_LANG_ES:"No hay activos"
# 		}[lang]
# 		html_text=(
# 			f"{html_text}\n"
# 			f"<div>{tl}</div>"
# 		)

# 	if not empty:

# 		x=len(assets_list)
# 		while True:
# 			x=x-1
# 			if x<0:
# 				break
# 			html_text=(
# 				f"{html_text}\n"
# 				f"{write_html_asset(lang,assets_list[x])}"
# 			)

# 	return (
# 			f"{html_text}\n"
# 		"</div>"
# 	)
