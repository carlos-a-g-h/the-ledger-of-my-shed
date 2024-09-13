#!/usr/bin/python3.9

from typing import Mapping,Union

from frontend_Any import _LANG_EN,_LANG_ES
from frontend_Any import _CSS_CLASS_COMMON
from frontend_Any import _CSS_CLASS_HORIZONTAL
from frontend_Any import _CSS_CLASS_DANGER
from frontend_Any import write_div_display_error

from internals import util_valid_str
# from internals import util_valid_int

def write_button_nav_new_order(lang:str)->str:

	tl={
		_LANG_EN:"Create a new order",
		_LANG_ES:"Crear una nueva orden"
	}[lang]

	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			"""hx-get="/fgmt/orders/new" """
			"""hx-swap="innerHTML" """
			"""hx-target="#messages" """
			">"
			f"{tl}"
		"</button>"
	)

def write_button_nav_list_orders(lang:str)->str:

	tl={
		_LANG_EN:"Select an existing order",
		_LANG_ES:"Seleccionar una orden existente"
	}[lang]

	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			"""hx-get="/fgmt/orders/current" """
			"""hx-swap="innerHTML" """
			"""hx-target="#messages" """
			">"
			f"{tl}"
		"</button>"
	)

# Display in search results
def write_button_add_asset_to_order(
		lang:str,order_id:str,asset_id:str
	)->str:

	tl={
		_LANG_EN:"Add to order",
		_LANG_ES:"Agregar a la orden"
	}[lang]
	return (
		f"""<form hx-post="/api/orders/current/{order_id}/update" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"

			# f"""<input type="hidden" name="id" value="{order_id}">"""
			f"""<input type="hidden" name="asset" value="{asset_id}">"""
			"""<input type="hidden" name="justbool" value="true">"""

			f"""<button class="{_CSS_CLASS_COMMON}" type="submit">""" "\n"
				f"{tl}\n"
			"</button>\n"

		"</form>"
	)

def write_button_run_order(
		lang:str,order_id:str
	)->str:

	tl={
		_LANG_EN:"Are you sure?",
		_LANG_ES:"¿Está seguro?"
	}[lang]
	html_text=(
		"<button "
			f"""class="{_CSS_CLASS_COMMON}" """
			f"""hx-post="/api/orders/current/{order_id}/run" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			f"""hx-confirm="{tl}" """
			">"
	)

	tl={
		_LANG_EN:"Run order",
		_LANG_ES:"Ejecutar orden"
	}[lang]
	return (
			f"{html_text}\n"
			f"{tl}\n"
		"</button>"
	)

def write_form_remove_asset_from_order(
		lang:str,
		order_id:str,asset_id:str
	)->str:

	tl={
		_LANG_EN:"Remove",
		_LANG_ES:"Quitar"
	}[lang]

	return (
		"<form "
			"""style="text-align:right" """
			f"""hx-delete="/api/orders/current/{order_id}/update" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML">"""
			"\n"

			f"""<input type="hidden" name="asset" value="{asset_id}">"""

			"""<button type="submit" """
				f"""class="{_CSS_CLASS_COMMON} {_CSS_CLASS_DANGER}">"""
				f"{tl}"
			"</button>\n"

		"</form>"
	)

def write_form_update_asset_in_order(
		lang:str,
		order_id:str,asset_id:str,
		currmod:Union[int,str]="???",
		inner:bool=False
	)->str:

	tl={
		_LANG_EN:"Algebraic sum",
		_LANG_ES:"Suma algebraica"
	}[lang]

	html_text=(
		f"""<form hx-post="/api/orders/current/{order_id}/update" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"

			"<div>\n\n"

				f"""<div class="{_CSS_CLASS_HORIZONTAL}">"""
					f"""<div class="{_CSS_CLASS_COMMON}">"""
						f"<strong>{currmod}</strong>"
					"</div>\n"
				"</div>\n"

				"\n"

				f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
					f"""<input type="hidden" name="asset" value="{asset_id}">""" "\n"
					f"""<input type="number" name="imod" value=0 class="{_CSS_CLASS_COMMON}">""" "\n"
				"</div>\n"

				"\n"

				f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
					"""<input type=checkbox name="algsum">""" "\n"
					f"""<label for="algsum">{tl}</label>"""
				"</div>"

				"\n"
	)


	tl={
		_LANG_EN:"Update",
		_LANG_ES:"Actualizar"
	}[lang]

	html_text=(
		f"{html_text}\n"

				f"""<div class="{_CSS_CLASS_HORIZONTAL}">"""
				"\n"
					f"""<button type="submit" class="{_CSS_CLASS_COMMON}">"""
					"\n"
						f"{tl}\n"
					"</button>\n"
				"</div>\n"

			"</div>\n"

		"</form>\n"
	)

	if not inner:
		html_text=(
			f"""<div id="asset-{asset_id}-in-{order_id}-updater">"""
			"\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text


def write_button_goto_order_editor(lang:str,order_id:str)->str:
	tl={
		_LANG_EN:"View or edit",
		_LANG_ES:"Ver o editar"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			f"""hx-get="/fgmt/orders/current/{order_id}/editor" """
			"""hx-swap="innerHTML" """
			"""hx-target="#messages" """
			">"
			f"{tl}"
		"</button>"
	)

def write_button_goto_order_asset_search(lang:str,order_id:str)->str:
	tl={
		_LANG_EN:"Search for assets",
		_LANG_ES:"Búsqueda de activos"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			f"""hx-get="/fgmt/orders/current/{order_id}/search-assets" """
			"""hx-swap="innerHTML" """
			"""hx-target="#messages" """
			">"
			f"{tl}"
		"</button>"
	)

def write_button_delete_order(
		lang:str,
		order_id:str,
		fol:bool=False
	)->str:

	route=f"/api/orders/current/{order_id}/drop"
	if fol:
		route=f"{route}-fol"

	tl={
		_LANG_EN:"Are you sure you want to delete this order?",
		_LANG_ES:"¿Está seguro que quiere eliminar la orden?"
	}[lang]
	html_text=(
		"<button "
			# """style="float:right;" """
			f"""class="{_CSS_CLASS_COMMON} {_CSS_CLASS_DANGER}" """
			f"""hx-delete="{route}" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			f"""hx-confirm="{tl}" """
			">"
	)

	tl={
		_LANG_EN:"Delete",
		_LANG_ES:"Eliminar"
	}[lang]
	html_text=(
			f"{html_text}\n"
			f"{tl}"
		"</button>"
	)

	return html_text

def write_form_new_order(lang:str)->str:

	html_text=(
		f"""<div class="{_CSS_CLASS_COMMON}">"""
			"<form "
				"""hx-post="/api/orders/new" """
				"""hx-trigger=submit """
				"""hx-target=#messages """
				"""hx-swap="innerHTML" """
				">\n"

				"<div>\n"
	)

	tl={
		_LANG_EN:"Sign",
		_LANG_ES:"Firma"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"""<label class="{_CSS_CLASS_COMMON}" for="sign">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					""" name="sign" """
					"""type="text" """
					"""max-length=32 """
					"required>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"""<label class="{_CSS_CLASS_COMMON}" for="tag">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					""" name="tag" """
					"""type="text" """
					"""max-length=32 """
					"required>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	html_text=(
			f"{html_text}\n"
		"</div>\n"
		"<div>\n"
			f"""<label class="{_CSS_CLASS_COMMON}" for="comment">{tl}</label>""" "\n"
			f"""<textarea class="{_CSS_CLASS_COMMON}" """
				"""name="comment" """
				"max-length=256 "
				">"
			"""</textarea>""" "\n"
		"<div>"
	)

	tl={
		_LANG_EN:"Create order",
		_LANG_ES:"Crear orden"
	}[lang]
	return (
				f"{html_text}"

				"""<button """
					f"""class="{_CSS_CLASS_COMMON}" """
					"""type="submit" """
					">"
					f"{tl}"
				"</button>"

			"</form>"
		"</div>"
	)

def write_html_order_assets(
		lang:str,
		order_id:str,
		assets:Mapping,
		assets_names:Mapping,
	)->str:

	html_text=""

	for asset_id in assets:
		html_text=(
			f"{html_text}\n"
			f"""<div id="asset-{asset_id}-in-{order_id}">"""
			"\n"
				f"""<div class="{_CSS_CLASS_COMMON}">"""
				"\n"
					f"<div>{asset_id} - {assets_names[asset_id]}</div>\n"
					f"{write_form_update_asset_in_order(lang,order_id,asset_id,assets[asset_id])}\n"
					f"{write_form_remove_asset_from_order(lang,order_id,asset_id)}\n"
				"</div>\n"
			"</div>"
		)

	return html_text

def write_html_order(
		lang:str,data:Mapping,
		edit_mode:bool=False
	)->str:

	order_id=util_valid_str(
		data.get("id")
	)
	if not isinstance(order_id,str):
		return write_div_display_error(lang)

	order_sign=util_valid_str(
		data.get("sign")
	)
	if not isinstance(order_sign,str):
		return write_div_display_error(lang)

	order_date=util_valid_str(
		data.get("date")
	)
	if not isinstance(order_date,str):
		return write_div_display_error(lang)

	order_tag=util_valid_str(
		data.get("tag")
	)
	if not isinstance(order_tag,str):
		return write_div_display_error(lang)

	html_text=(

		f"""<div id="order-{order_id}">"""

			f"""<div class="{_CSS_CLASS_COMMON}">"""

				"\n<div>\n"

					"""<!-- ID, SIGN, AND TAG, (NO COMMENT, AND NO ASSETS) -->"""
					"\n"

					f"<div><strong>ID: {order_id}</strong></div>"
	)

	tl={
		_LANG_EN:"Sign",
		_LANG_ES:"Firma"
	}[lang]
	html_text=(
		f"{html_text}\n"
		# f"""<div class="{_CSS_CLASS_HORIZONTAL}">{tl}: {order_sign}</div>"""
		f"""<div>{tl}: {order_sign}</div>"""
	)

	tl={
		_LANG_EN:"Date",
		_LANG_ES:"Fecha"
	}[lang]
	html_text=(
		f"{html_text}\n"
		# f"""<div class="{_CSS_CLASS_HORIZONTAL}">{tl}: {order_date}</div>"""
		f"""<div>{tl}: {order_date}</div>"""
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]
	html_text=(
			f"{html_text}\n"
			# f"""<div class="{_CSS_CLASS_HORIZONTAL}">{tl}: {order_tag}</div>""" "\n"
			f"""<div>{tl}: {order_tag}</div>""" "\n"
		"</div>"
	)

	# End of all 'horizontal' content, and goto buttons

	if not edit_mode:
		html_text=(
			f"{html_text}\n"
			f"{write_button_goto_order_editor(lang,order_id)}\n"
			"""<div style="float:right;">"""
				f"{write_button_delete_order(lang,order_id,True)}\n"
			"</div>"
		)

	if edit_mode:
		html_text=(
			f"{html_text}\n"
			f"{write_button_goto_order_asset_search(lang,order_id)}\n"
			f"{write_button_run_order(lang,order_id)}\n"
			"""<div style="float:right;">"""
				f"{write_button_delete_order(lang,order_id)}\n"
			"</div>"
		)

	# end of both divs

	return (
				f"{html_text}\n"
			"</div>"
		"</div>"
	)
