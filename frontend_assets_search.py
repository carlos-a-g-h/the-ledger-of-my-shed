#!/usr/bin/python3.9

# from typing import Mapping
from typing import Optional

from frontend_Any import (

	_ID_MSGZONE,

	# _CSS_CLASS_HX_SWAPPABLE,

	_CSS_CLASS_COMMON,
	_CSS_CLASS_CONTROLS,
	_CSS_CLASS_IG_FIELDS,
	_CSS_CLASS_IG_CHECKBOXES,
	write_html_input_checkbox,
	write_html_input_string,
	write_button_submit
)

# from frontend_orders import write_form_add_asset_to_order_lucky

from symbols_Any import (
	_LANG_EN,_LANG_ES,
	_KEY_TAG,
	_KEY_SIGN,
	_KEY_NAME_QUERY,
	# _KEY_DATE,
	# _KEY_GO_STRAIGHT
)

from symbols_assets import(
	# _KEY_NAME,
	_ID_FORM_ASSET_EMATCH,
	_ID_FORM_SEARCH_ASSETS,
	_ID_RESULT_SEARCH_ASSETS,
	_KEY_INC_SUPPLY as _KEY_GET_SUPPLY,
	_KEY_INC_VALUE as _KEY_GET_VALUE,
)

def write_form_asset_ematch(lang:str,full:bool=True)->str:

	blank=""

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=f"{write_html_input_string(_KEY_NAME_QUERY,tl,value=blank)}"

	tl={
		_LANG_EN:"Go",
		_LANG_ES:"Ir"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_button_submit(tl)}"
	)

	html_text=(
		"""<form hx-post="/api/assets/exact-match" """
			"""hx-trigger="submit" """
			f"""hx-target=#{_ID_MSGZONE} """
			"""hx-swap=innerHTML"""
			">\n"
			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{html_text}\n"
			"</div>\n"
		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"Exact search",
			_LANG_ES:"Búsqueda precisa"
		}[lang]
		html_text=(
			# f"""<div id="{_ID_FORM_ASSET_EMATCH}" """
			# "<div>\n"
			f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"

				f"<h3>{tl}</h3>\n"

				# f"""<div class="{_CSS_CLASS_HX_SWAPPABLE}">""" "\n"
				f"""<div id="{_ID_FORM_ASSET_EMATCH}">""" "\n"
					f"{html_text}\n"
				"</div>\n"

			"</div>"
		)

	return html_text

def write_button_cleanup(lang:str)->str:

	onclick=(
		f""" document.getElementById('{_ID_RESULT_SEARCH_ASSETS}').innerHTML='<!-- ALL CLEAN -->' """
	)

	tl={
		_LANG_EN:"Clean",
		_LANG_ES:"Limpiar"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			f"""onclick="{onclick.strip()}" """
			">"
			f"{tl}"
		"</button>"
	)

def write_form_search_assets(
		lang:str,
		order_id:Optional[str]=None,
		authorized:bool=True,
		full:bool=True,
		decorate:bool=False,
	)->str:

	order_specific=isinstance(order_id,str)

	the_route={
		True:f"/api/orders/pool/{order_id}/search-assets",
		False:"/api/assets/search-assets"
	}[order_specific]

	html_text=(
		f"""<form hx-post="{the_route}" """
			"""hx-trigger="submit" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-swap="innerHTML" """
			">\n"

			# NOTE: fields start
			f"""<div class="{_CSS_CLASS_IG_FIELDS}">"""
	)

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_NAME_QUERY,label=tl)}"
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_TAG,label=tl,maxlen=32)}"
	)

	if authorized:
		tl={
			_LANG_EN:"Sign (by ID)",
			_LANG_ES:"Firma (por ID)"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"{write_html_input_string(_KEY_SIGN,label=tl,maxlen=32)}"
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

			f"""<div class="{_CSS_CLASS_IG_CHECKBOXES}">"""
				# checkboxes start {
		)

		tl={
			_LANG_EN:"Include value",
			_LANG_ES:"Incluir valor"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"{write_html_input_checkbox(_KEY_GET_VALUE,label=tl)}"
		)

		tl={
			_LANG_EN:"Include supply",
			_LANG_ES:"Incluir cantidad actual"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"{write_html_input_checkbox(_KEY_GET_SUPPLY,label=tl)}"
		)

		html_text=(
				f"{html_text}\n"

				# } checkboxes end
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
				"</button>"
			"</div>\n"
		"</form>"
	)

	if full:

		tl={
			_LANG_EN:"Asset searcher",
			_LANG_ES:"Buscador de activos"
		}[lang]

		attr_class=""
		if decorate:
			attr_class=f""" class="{_CSS_CLASS_COMMON}" """

		html_text=(
			f"<div {attr_class}>\n"
				f"<h3>{tl}</h3>\n"
				f"""<div id={_ID_FORM_SEARCH_ASSETS}>""" "\n"
					f"{html_text}\n"
				"</div>\n"
			"</div>"
		)

		html_text=(
			f"{html_text}\n"
			f"""<div id={_ID_RESULT_SEARCH_ASSETS}>""" "\n"
				"<!-- SEARCH RESULTS GO HERE -->\n"
			"</div>"
		)

		# if order_specific:
		# 	html_text=(
		# 		f"{html_text}\n"
		# 		f"{write_form_add_asset_to_order_lucky(lang,order_id)}"
		# 	)

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
