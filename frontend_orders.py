#!/usr/bin/python3.9

from typing import (
		Mapping,
		# Union,
		Optional
	)

from symbols_Any import (

	_LANG_EN,_LANG_ES,
	_SECTION,

	_KEY_SIGN,_KEY_SIGN_UNAME,
	_KEY_TAG,_KEY_COMMENT,
	_KEY_DATE,
	_KEY_DELETE_AS_ITEM,
)

from symbols_assets import (
	_COL_ASSETS,
	_KEY_ASSET,
	_KEY_NAME,
	_KEY_RECORD_MOD,
	_KEY_VALUE
)

from symbols_orders import (

	_KEY_ORDER,
	_KEY_ORDER_VALUE,
	_KEY_ORDER_IS_FLIPPED,
	_KEY_LOCKED_BY,

	_KEY_ORDER_KEEP,
	_KEY_ORDER_DROP,
	_KEY_ALGSUM,
	_KEY_COPY_VALUE,

	_ID_FORM_NEW_ORDER,
	_ID_RESULT_NEW_ORDER,

	# _ID_FORM_RUN_ORDER,
	_ID_FORM_RUN_OR_REVERT_ORDER,

	_CSS_CLASS_ITEM_ORDER,
	_CSS_CLASS_ORDER_INFO,

	html_id_order,
	html_id_order_asset
)

from frontend_Any import (

	_ID_MESSAGES,
	_ID_MAIN_TWO,

	_CSS_CLASS_NAV,
	_CSS_CLASS_COMMON,
	# _CSS_CLASS_HORIZONTAL,
	_CSS_CLASS_FOCUSED,
	_CSS_CLASS_DANGER,
	_CSS_CLASS_CONTROLS,

	_CSS_CLASS_ASSET_IN_ORDER,

	# _STYLE_TALIGN_R,

	write_button_submit,
	write_div_display_error,
	write_html_input_number,
	write_html_input_string,
	write_html_input_checkbox,
	write_html_input_textbox
)

from internals import (
	util_valid_bool,
	util_valid_int,
	util_valid_str,
	util_valid_date,
	util_rnow,
)

def write_button_nav_new_order(lang:str)->str:

	tl={
		_LANG_EN:"Create a new order",
		_LANG_ES:"Crear una nueva orden"
	}[lang]

	return (
		f"""<button class="{_CSS_CLASS_NAV}" """
			"""hx-get="/fgmt/orders/new" """
			"""hx-swap="innerHTML" """
			f"""hx-target="#{_ID_MESSAGES}" """
			">"
			f"{tl}"
		"</button>"
	)

def write_button_nav_list_orders(lang:str)->str:

	tl={
		_LANG_EN:"All orders",
		_LANG_ES:"Todas las órdenes"
	}[lang]

	return (
		f"""<button class="{_CSS_CLASS_NAV}" """
			"""hx-get="/fgmt/orders/all-orders" """
			"""hx-swap="innerHTML" """
			f"""hx-target="#{_ID_MESSAGES}" """
			">"
			f"{tl}"
		"</button>"
	)

def write_form_new_order(lang:str,full:bool=True)->str:

	html_text=(
		"""<form hx-post="/api/orders/new" """
			"""hx-trigger=submit """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML" """
			">\n"
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]
	html_text=f"{html_text}\n"+write_html_input_string(
		_KEY_TAG,label=tl,
		value=f"ord-{util_rnow()}",
		maxlen=32,required=True
	)

	tl={
		_LANG_EN:"Flipped order",
		_LANG_ES:"Orden invertida"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_checkbox(_KEY_ORDER_IS_FLIPPED,tl)}\n"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_textbox(_KEY_COMMENT,label=tl)}"
	)

	tl={
		_LANG_EN:"Create order",
		_LANG_ES:"Crear orden"
	}[lang]
	html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_submit(tl)}\n"
			"</div>\n"
		"</form>"
	)

	if full:
		html_text=(
			f"""<div id="{_ID_FORM_NEW_ORDER}">""" "\n"
				f"{html_text}\n"
			"</div>\n"
			f"""<div id="{_ID_RESULT_NEW_ORDER}">""" "\n"
				f"<!-- NEW ORDER(s) GO HERE -->\n"
			"</div>\n"
		)

	return html_text

def write_button_order_details(
		lang:str,order_id:str,
		refresh:bool=False
	)->str:

	tl={
		True:{
			_LANG_EN:"Refresh",
			_LANG_ES:"Actualizar"
		},
		False:{
			_LANG_EN:"View or edit",
			_LANG_ES:"Ver o editar"
		}
	}[refresh][lang]

	url_path=f"/fgmt/orders/pool/{order_id}/details"

	if refresh:
		url_path=f"{url_path}?{_SECTION}={_ID_MAIN_TWO}"

	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			f"""hx-get="{url_path}" """
			"""hx-swap="innerHTML" """
			f"""hx-target="#{_ID_MESSAGES}" """
			">"
			f"{tl}"
		"</button>"
	)

def write_button_add_asset_to_order(
		lang:str,
		order_id:str,
		asset_id:str
	)->str:

	tl={
		_LANG_EN:"Copy the value",
		_LANG_ES:"Copiar el valor"
	}[lang]
	html_text=(
		f"""<div>""" "\n"
			f"""<form hx-post="/api/orders/pool/{order_id}/add-asset" """
				f"""hx-target="#{_ID_MESSAGES}" """
				"""hx-swap="innerHTML" """
				">\n"

				f"""<input type="hidden" name="{_KEY_ASSET}" value="{asset_id}">""" "\n"

				f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"

					f"{write_html_input_number(_KEY_RECORD_MOD,value=0,required=True)}\n"
					f"{write_html_input_checkbox(_KEY_COPY_VALUE,tl,checked=True)}"
	)

	tl={
		_LANG_EN:"Add to order",
		_LANG_ES:"Agregar a la orden"
	}[lang]
	html_text=(
					f"{html_text}\n"
					f"{write_button_submit(tl)}\n"
				"</div>\n"
			"</form>\n"
		"</div>"
	)

	return html_text

def write_button_remove_asset_from_order(
		lang:str,order_id:str,asset_id:str
	)->str:

	tl={
		_LANG_EN:"Remove from order",
		_LANG_ES:"Quitar de la orden"
	}[lang]
	return (
		f"""<form hx-delete="/api/orders/pool/{order_id}/remove-asset" """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML">"""

			f"""<input type=hidden name="{_KEY_ASSET}" value="{asset_id}">""" "\n"

			f"{write_button_submit(tl,[_CSS_CLASS_COMMON,_CSS_CLASS_DANGER])}\n"

		"</form>"
	)

def write_form_update_asset_in_order(
		lang:str,
		order_id:str,asset_id:str,
		full:bool=True
	)->str:

	html_text=(
		f"""<form hx-post="/api/orders/pool/{order_id}/update-asset" """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML" """
			">\n"

			f"""<input type="hidden" name="{_KEY_ASSET}" value="{asset_id}">""" "\n"
	)

	tl={
		_LANG_EN:"Algebraic sum",
		_LANG_ES:"Suma algebraica"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
			f"{write_html_input_number(_KEY_RECORD_MOD,value=0,required=True)}\n"
			f"{write_html_input_checkbox(_KEY_ALGSUM,tl)}\n"
	)

	tl={
		_LANG_EN:"Update",
		_LANG_ES:"Actualizar"
	}[lang]

	html_text=(
				f"{html_text}\n"
				f"{write_button_submit(tl)}\n"
			"</div>\n"
		"</form>\n"
		# f"{write_button_remove_asset_from_order(lang,order_id,asset_id)}"
	)

	if full:
		tl={
			_LANG_EN:"Edit",
			_LANG_ES:"Editar"
		}[lang]
		html_text=(
			"<details>\n"
				f"<summary>{tl}</summary>\n"
				f"{html_text}\n"
			"</details>"
		)

	return html_text

def write_html_asset_in_order(
		lang,order_id:str,
		data:Mapping,
		asset_id:Optional[str]=None,
		full:bool=True,
		authorized=True,
		focus:bool=False
	)->str:

	asset_id_ok=asset_id
	if asset_id_ok is None:
		asset_id_ok=data.get(_KEY_ASSET)

	if asset_id_ok is None:
		return write_div_display_error(lang,data)

	asset_name=data.get(_KEY_NAME)
	if asset_name is None:
		return write_div_display_error(lang,data)

	# The info: name, value

	html_text=(
		"<div>"
			f"""<strong>{asset_name}</strong> """
			f"( <code>{asset_id_ok}</code> )"
		"</div>"
	)

	asset_value=data.get(_KEY_VALUE)
	has_value=isinstance(asset_value,int)
	if has_value:
		tl={
			_LANG_EN:"Value",
			_LANG_ES:"Valor"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{asset_value}</code></div>"
		)

	asset_mod=data.get(_KEY_RECORD_MOD)
	has_mod=isinstance(asset_mod,int)
	if has_mod:

		tl=asset_mod
		if has_value and (not asset_value==0):
			tl=f"{tl} ( {asset_mod*asset_value} )"

		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
					f"<strong>{tl}</strong>\n"
				"</div>\n"
		)
		if authorized:
			html_text=(
				f"{html_text}\n"
				f"{write_button_remove_asset_from_order(lang,order_id,asset_id)}"
			)

		html_text=(
				f"{html_text}\n"
			"</div>"
		)


	# Wrapping around all the info

	html_text=(
		f"""<div id="{html_id_order_asset(asset_id,True)}">""" "\n"
			f"{html_text}\n"
		"</div>\n"
	)

	# Delete button and editor form

	if authorized:

		html_text=(
			f"{html_text}\n"
			f"{write_form_update_asset_in_order(lang,order_id,asset_id)}"
		)

	if full:

		classes=f"{_CSS_CLASS_ASSET_IN_ORDER} {_CSS_CLASS_COMMON}"
		if focus:
			classes=f"{classes} {_CSS_CLASS_FOCUSED}"

		html_text=(
			f"""<div id="{html_id_order_asset(asset_id)}" class="{classes}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_html_order_assets(
		lang:str,
		order_id:str,
		obj_order:Mapping,
		focus:Optional[str]=None,
		authorized:bool=True,
	)->str:

	html_text=f"""<div id="{html_id_order(order_id,assets=True)}">"""

	focus_asset=isinstance(focus,str)

	if isinstance(obj_order.get(_COL_ASSETS),Mapping):

		for asset_id in obj_order[_COL_ASSETS]:

			focus_on_this=False
			if focus_asset:
				focus_on_this=(focus==asset_id)

			html_text=write_html_asset_in_order(
				lang,order_id,obj_order[_COL_ASSETS][asset_id],
				asset_id=asset_id,authorized=authorized,
				focus=focus_on_this
			)+f"\n{html_text}"

	html_text=(
			f"{html_text}\n"
		"</div>\n"
	)

	# order_value=util_valid_int(
	# 	obj_order.get(_KEY_ORDER_VALUE)
	# )
	# if (order_value is not None):
	# 	if not order_value==0:
	# 		tl={
	# 			_LANG_EN:"TOTAL VALUE",
	# 			_LANG_ES:"VALOR TOTAL"
	# 		}[lang]
	# 		html_text=(
	# 			f"{html_text}\n"
	# 			f"""<div class="{_CSS_CLASS_COMMON}">"""
	# 				f"{tl}: <strong>{order_value}</strong>"
	# 			"</div>"
	# 		)

	# html_text=(
	# 		f"{html_text}\n"
	# 	"</div>"
	# )

	return html_text

# NOTE:
# There is a weird HTMX bug in the functions write_form_run_order() and write_form_revert_order()
# For some reason I haven't figured out yet, the nested inputs (form>div>input nesting) do not get included in the POST request
# I double checked, even tripple checked the surrounding code to see if there was a missing parent/surrounding tag and I found nothing, the form even works OK if it is used as a traditional HTML Form
# The solution (for now) in these functions is to write the checkbox and the label without their divs wrapping them up, so that the form is the direct parent

def write_form_run_order(
		lang:str,order_id:str,
		full:bool=True
	)->str:

	tl={
		_LANG_EN:"Are you sure?",
		_LANG_ES:"¿Está seguro?"
	}[lang]
	html_text=(
		f"""<form hx-post="/api/orders/pool/{order_id}/run" """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML" """
			f"""hx-confirm="{tl}" """
			f"""hx-trigger="submit" """
			# f"""hx-include="[name='{_KEY_ORDER_KEEP}']" """
			">\n"
	)

	tl={
		_LANG_EN:"Keep after running",
		_LANG_ES:"Conservar tras ejecutar"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_checkbox(_KEY_ORDER_KEEP,tl,checked=True,full=False)}"
	)

	tl={
		_LANG_EN:"Run order",
		_LANG_ES:"Ejecutar orden"
	}[lang]
	html_text=(
			f"{html_text}\n"
			f"{write_button_submit(tl)}\n"
		"</form>"
	)

	if full:
		html_text=(
			f"""<div id="{_ID_FORM_RUN_OR_REVERT_ORDER}" """
				f"""class="{_CSS_CLASS_COMMON} {_CSS_CLASS_CONTROLS}" """
				">\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_form_revert_order(
		lang:str,order_id:str,
		full:bool=True,
	)->str:

	tl={
		_LANG_EN:"Changes that came from this order will be reverted. Are you sure?",
		_LANG_ES:"Los cambios causados por esta orden serán revertidos ¿Está seguro?"
	}[lang]
	html_text=(
		"<form "
			f"""hx-post="/api/orders/pool/{order_id}/revert" """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML" """
			f"""hx-confirm="{tl}" """
			f"""hx-trigger="submit" """
			">\n"
	)


	tl={
		_LANG_EN:"Delete the order",
		_LANG_ES:"Eliminar la órden"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_checkbox(_KEY_ORDER_DROP,tl,full=False)}\n"
	)

	tl={
		_LANG_EN:"Revert",
		_LANG_ES:"Revertir"
	}[lang]

	html_text=(
		f"{html_text}\n"
			f"{write_button_submit(tl)}\n"
		"</form>"
	)

	if full:
		html_text=(
			f"""<div id="{_ID_FORM_RUN_OR_REVERT_ORDER}" """
				f"""class="{_CSS_CLASS_COMMON} {_CSS_CLASS_CONTROLS}" """
					">\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text


def write_button_delete_order(
		lang:str,
		order_id:str,
		delete_as_item:bool=False
	)->str:

	the_route={
		True:"/api/orders/drop-order",
		False:f"/api/orders/pool/{order_id}/drop"
	}[delete_as_item]

	tl={
		_LANG_EN:"Are you sure you want to delete this order?",
		_LANG_ES:"¿Está seguro que quiere eliminar la orden?"
	}[lang]
	html_text=(
		f"""<form hx-delete="{the_route}" """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML" """
			f"""hx-confirm="{tl}" """
			">\n"
	)

	if delete_as_item:
		html_text=(
			f"{html_text}\n"
			f"""<input type="hidden" name="{_KEY_DELETE_AS_ITEM}" value=true>""" "\n"
			f"""<input type="hidden" name="{_KEY_ORDER}" value="{order_id}">""" "\n"
		)

	tl={
		_LANG_EN:"Delete",
		_LANG_ES:"Eliminar"
	}[lang]
	html_text=(
			f"{html_text}\n"
			f"{write_button_submit(tl,[_CSS_CLASS_COMMON,_CSS_CLASS_DANGER])}\n"
		"</form>"
	)

	return html_text

def write_html_order_info(
		lang:str,
		data:Mapping,
		authorized:bool,
		full:bool=True,
	)->str:

	order_id:Optional[str]=util_valid_str(
		data.get(_KEY_ORDER),True
	)
	order_tag:Optional[str]=util_valid_str(
		data.get(_KEY_TAG),True
	)
	order_date:Optional[str]=util_valid_date(
		data.get(_KEY_DATE)
	)
	if (
		(order_id is None) or
		(order_tag is None) or
		(order_date) is None
	):
		return write_div_display_error(lang,data)

	html_text=(
		f"<div><strong>{order_id}</strong></div>\n"
		f"<div>{order_date} / {order_tag}</div>"
	)

	if authorized:

		order_sign:Optional[str]=util_valid_str(
			data.get(_KEY_SIGN),True
		)
		order_sign_uname:Optional[str]=util_valid_str(
			data.get(_KEY_SIGN_UNAME),True
		)

		signed=isinstance(order_sign,str)
		signed_uname=isinstance(order_sign_uname,str)
		if signed or signed_uname:

			tl={
				_LANG_EN:"Signed by:",
				_LANG_ES:"Firmado por:"
			}[lang]
			if signed_uname:
				tl=f"{tl} [ <code>{order_sign_uname}</code> ]"
			if signed:
				tl=f"{tl} [ <code>{order_sign}</code> ]"

			html_text=(
				f"{html_text}\n"
				f"<div>{tl}</div>"
			)

		locked_by=data.get(_KEY_LOCKED_BY)
		if isinstance(locked_by,str):

			tl={
				_LANG_EN:"Locked by:",
				_LANG_ES:"Bloqueada por:"
			}[lang]
			html_text=(
				f"{html_text}\n"
				f"<div>{tl} <code>{locked_by}</code></div>"
			)

	order_is_fliped=util_valid_bool(
		data.get(_KEY_ORDER_IS_FLIPPED),False
	)
	if order_is_fliped:
		tl={
			_LANG_EN:"This order is flipped",
			_LANG_ES:"Esta orden es invertida"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>"
				f"<code>[ {tl} ]</code>"
			"</div>"
		)

	order_comment:Optional[str]=util_valid_str(
		data.get(_KEY_COMMENT)
	)
	if order_comment is not None:
		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
				f"{order_comment}\n"
			"</div>"
		)

	if full:
		html_text=(
			f"""<div id="{html_id_order(order_id,info=True)}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_html_order_as_item(
		lang:str,
		data:Mapping,
		authorized:bool,
		full:bool=True,
		focus:bool=False
	)->str:

	print("Data to render:",data)

	order_id:Optional[str]=util_valid_str(
		data.get(_KEY_ORDER),True
	)
	if order_id is None:
		return write_div_display_error(lang,data)

	# html_text=write_html_order_as_item(lang,data,False)

	html_text=(
		f"{write_html_order_info(lang,data,authorized)}\n"

		f"""<div class={_CSS_CLASS_CONTROLS}>""" "\n"
			f"{write_button_order_details(lang,order_id)}\n"
			f"{write_button_delete_order(lang,order_id,True)}\n"
		"</div>"
	)

	if full:

		classes=f"{_CSS_CLASS_ITEM_ORDER} {_CSS_CLASS_COMMON}"
		if focus:
			classes=f"{classes} {_CSS_CLASS_FOCUSED}"

		html_text=(
			f"""<div id="{html_id_order(order_id)}" """
				f"""class="{classes}" """
				">\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text


def write_html_order_details(
		lang:str,data:Mapping,
		authorized:bool,
		focus:Optional[str]=None,
	)->str:

	order_id:Optional[str]=util_valid_str(
		data.get(_KEY_ORDER),True
	)
	if not isinstance(order_id,str):
		return write_div_display_error(lang,data)

	# Info + delete button

	tl={
		_LANG_EN:"Order assets",
		_LANG_ES:"Activos de la orden"
	}[lang]
	html_text=(
		f"""<div id="{html_id_order(order_id)}" class="{_CSS_CLASS_ORDER_INFO}">""" "\n"
			f"<h3>{tl}</h3>\n"
			f"{write_html_order_info(lang,data,authorized)}\n"
			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_order_details(lang,order_id,True)}\n"
	)
	if authorized:
		html_text=(
			f"{html_text}\n"
			f"{write_button_delete_order(lang,order_id)}\n"
		)

	html_text=(
				f"{html_text}\n"
			"</div>\n"
		"</div>"
	)

	# Run/revert order form

	if authorized:

		locked=isinstance(
			data.get(_KEY_LOCKED_BY),str
		)

		if locked:
			html_text=(
				f"{html_text}\n"
				# f"""<div class="{_CSS_CLASS_COMMON} {_CSS_CLASS_CONTROLS}">"""
				f"{write_form_revert_order(lang,order_id)}\n"
				# "</div>"
			)

		if not locked:
			html_text=(
				f"{html_text}\n"
				f"{write_form_run_order(lang,order_id)}"
			)

	# Order value

	html_text=(
		f"{html_text}\n"
		f"""<div id="{html_id_order(order_id,value=True)}">""" "\n"
			"<!-- ORDER VALUE GOES HERE -->"
	)

	order_value=util_valid_int(
		data.get(_KEY_ORDER_VALUE)
	)
	if (order_value is not None):
		if not order_value==0:
			tl={
				_LANG_EN:"TOTAL VALUE",
				_LANG_ES:"VALOR TOTAL"
			}[lang]
			html_text=(
				f"{html_text}\n"
				f"""<div class="{_CSS_CLASS_COMMON}">"""
					f"{tl}: <strong>{order_value}</strong>"
				"</div>"
			)

	html_text=(
			f"{html_text}\n"
		"</div>"
	)

	# Assets inside the order

	html_text=(
		f"{html_text}\n"
		f"{write_html_order_assets(lang,order_id,data,focus)}\n"
	)

	return html_text
