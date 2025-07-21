#!/usr/bin/python3.9

from typing import Mapping,Optional,Union

from frontend_Any import (

	_ID_MSGZONE,
	_ID_REQ_RES,

	_CSS_CLASS_DANGER,
	_CSS_CLASS_FOCUSED,
	# _CSS_CLASS_VER,
	_CSS_CLASS_COMMON,
	_CSS_CLASS_NAV,
	_CSS_CLASS_CONTROLS,
	# _CSS_CLASS_HORIZONTAL,

	# _CSS_CLASS_ANCHOR_AS_BUTTON,

	# _CSS_CLASS_ASSET_HISTORY,

	# _CSS_CLASS_IG_CHECKBOXES,
	_CSS_CLASS_IG_FIELDS,

	_CSS_CLASS_INPUT_GUARDED,

	# write_button_reset,
	# write_popupmsg,
	write_button_submit,
	write_div_display_error,
	write_html_input_checkbox,
	write_html_input_number,
	write_html_input_string,
	write_html_input_textbox,
	write_html_input_radio,
	write_html_input_date
)

from internals import (
	util_valid_int,
	util_valid_str,
	util_valid_date,
	# util_rnow
)

from symbols_assets import (

	_KEY_ASSET,
	_KEY_NAME,
	_KEY_VALUE,
	_KEY_SUPPLY,

	# _KEY_HISTORY,
	_KEY_RECORD_UID,
	_KEY_RECORD_MOD,

	_ID_ASSETS_TO_SPREADSHEET,

	_ID_NEW_ASSET,
		_ID_NEW_ASSET_FORM,

	_ID_ASSET_EDITOR,
		_ID_ASSET_EDITOR_FORM,

	_ID_ASSET_HISTORY,
		_ID_ASSET_HISTORY_FORM,
		_ID_ASSET_HISTORY_RECORDS,

	_ID_ASSET_INFO,
	_ID_ASSET_SUPPLY,

	_CSS_CLASS_ITEM_ASSET,

	_KEY_INC_HISTORY,
	# _KEY_INC_SUPPLY,
	# _KEY_INC_VALUE,

	html_id_asset
)

from symbols_Any import (
	_LANG_EN,_LANG_ES,

	_KEY_TAG,
	_KEY_SIGN,_KEY_SIGN_UNAME,
	_KEY_COMMENT,

	#_KEY_DELETE_AS_ITEM,
	_KEY_DATE,
	#_KEY_DATE_UTC,
	_KEY_DATE_MAX,
	_KEY_DATE_MIN
)

from exex_assets import (
	_KEY_ATYPE,
	_KEY_FTREND,
)

def write_button_nav_new_asset(lang:str)->str:

	tl={
		_LANG_EN:"Create new asset",
		_LANG_ES:"Crear activo nuevo"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_NAV}" """
			"""hx-get="/fgmt/assets/new" """
			"""hx-swap="innerHTML" """
			f"""hx-target="#{_ID_MSGZONE}" """
			">"
			f"{tl}"
		"</button>"
	)

def write_button_nav_search_assets(lang:str)->str:

	tl={
		_LANG_EN:"Search asset(s)",
		_LANG_ES:"Buscar activo(s)"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_NAV}" """
			"""hx-get="/fgmt/assets/search-assets" """
			"""hx-swap="innerHTML" """
			f"""hx-target="#{_ID_MSGZONE}" """
			">"
			f"{tl}"
		"</button>"
	)

def write_button_nav_export_options(lang:str)->str:

	tl={
		_LANG_EN:"Export options",
		_LANG_ES:"Opciones de exportación"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_NAV}" """
			"""hx-get="/fgmt/assets/export-options" """
			"""hx-swap="innerHTML" """
			f"""hx-target="#{_ID_MSGZONE}" """
			">"
			f"{tl}"
		"</button>"
	)

def write_form_new_asset(lang:str,full:bool=True)->str:

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=(
		f"{write_html_input_string(_KEY_NAME,label=tl,required=True)}"
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_TAG,label=tl,maxlen=32)}"
	)

	tl={
		_LANG_EN:"Value",
		_LANG_ES:"Valor"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_number(_KEY_VALUE,label=tl,value=0,minimum=0)}"
	)

	tl={
		_LANG_EN:"Initial ammount",
		_LANG_ES:"Cantidad inicial"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_number(_KEY_SUPPLY,label=tl,value=0,minimum=0)}"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	html_text=(
		f"""<div class="{_CSS_CLASS_IG_FIELDS}">""" "\n"
			f"{html_text}\n"
		"</div>\n"
		f"{write_html_input_textbox(_KEY_COMMENT,label=tl)}"
	)

	tl={
		_LANG_EN:"Create asset",
		_LANG_ES:"Crear activo"
	}[lang]
	html_text=(
		"""<form hx-post="/api/assets/new" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-trigger="submit" """
			"""hx-swap="innerHTML">""" "\n"

			f"{html_text}\n"

			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_submit(tl)}\n"
			"</div>\n"

		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"Creation of a new asset",
			_LANG_ES:"Creación de un nuevo activo"
		}[lang]
		html_text=(
			f"""<div id="{_ID_NEW_ASSET}">""" "\n"
				f"<h3>{tl}</h3>\n"
				f"""<div id="{_ID_NEW_ASSET_FORM}">""" "\n"
					f"{html_text}\n"
				"</div>\n"
			"</div>\n"
			f"""<div id="{_ID_REQ_RES}">""" "\n"
				"<!-- NEW ASSETS GO HERE -->\n"
			"</div>"
		)

	return html_text

def write_form_edit_asset_definition(
		lang:str,asset_id:str,
		full:bool=True,
	)->str:

	# OK

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	tl_change=f"change-{_KEY_NAME}"
	html_text=(

		f"""<div class="{_CSS_CLASS_INPUT_GUARDED}">""" "\n"
			f"{write_html_input_checkbox(tl_change,tl)}\n"
			f"{write_html_input_string(_KEY_NAME)}"
		"</div>"
	)

	tl={
		_LANG_EN:"Value",
		_LANG_ES:"Valor"
	}[lang]
	tl_change=f"change-{_KEY_VALUE}"
	html_text=(
		f"{html_text}\n"

		f"""<div class="{_CSS_CLASS_INPUT_GUARDED}">""" "\n"
			f"{write_html_input_checkbox(tl_change,tl)}\n"
			f"{write_html_input_number(_KEY_VALUE,minimum=0)}"
		"</div>"
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]
	tl_change=f"change-{_KEY_TAG}"
	html_text=(
		f"{html_text}\n"

		f"""<div class="{_CSS_CLASS_INPUT_GUARDED}">""" "\n"
			f"{write_html_input_checkbox(tl_change,tl)}\n"
			f"{write_html_input_string(_KEY_TAG)}"
		"</div>"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	tl_change=f"change-{_KEY_COMMENT}"
	html_text=(
		f"""<div class="{_CSS_CLASS_IG_FIELDS}">""" "\n"
			f"{html_text}\n"
		"</div>\n"
		f"""<div class="{_CSS_CLASS_INPUT_GUARDED}">""" "\n"
			f"{write_html_input_checkbox(tl_change,tl)}\n"
			f"{write_html_input_textbox(_KEY_COMMENT)}"
		"</div>"
	)


	tl={
		_LANG_EN:"Apply changes",
		_LANG_ES:"Aplicar cambios"
	}[lang]
	html_text=(

		# f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"

			f"{html_text}\n"

			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_submit(tl)}\n"
			"</div>\n"

		# "</div>"

	)


	html_text=(
		f"""<form hx-post="/api/assets/pool/{asset_id}/edit" """ "\n"
			f"""hx-target="#{_ID_MSGZONE}" """ "\n"
			"""hx-swap="innerHTML">""" "\n"

			f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
				f"{html_text}\n"
			"</div>\n"

		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"Edit definition",
			_LANG_ES:"Editar definición"
		}[lang]
		html_text=(
			f"""<details id="{_ID_ASSET_EDITOR}">""" "\n"
				f"<summary>{tl}</summary>\n"
				f"""<div id={_ID_ASSET_EDITOR_FORM}>""" "\n"
					f"{html_text}\n"
				"</div>"
			"</details>"
		)

	return html_text

def write_button_asset_fullview_or_update(
		lang:str,
		asset_id:str,
		umode:int=0
	)->str:

	tl={
		True:{
			_LANG_EN:"Manage",
			_LANG_ES:"Administrar"
		}[lang],
		False:{
			_LANG_EN:"Refresh now",
			_LANG_ES:"Actualizar ahora"
		}[lang]
	}[umode==0]

	url=f"/fgmt/assets/pool/{asset_id}"
	if umode==1:
		url=f"{url}?spec={_ID_ASSET_INFO}"
	if umode==2:
		url=f"{url}?spec={_ID_ASSET_HISTORY}"

	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			f"""hx-get="{url}" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-swap="innerHTML" """
			">"
			f"{tl}"
		"</button>"
	)

def write_form_drop_asset(
		lang:str,
		asset_id:str,
		delete_entry:bool=True,
	)->str:

	req_url=f"/api/assets/pool/{asset_id}/drop"
	if delete_entry:
		req_url=f"{req_url}-as-item"


	html_text={
		_LANG_EN:"Delete",
		_LANG_ES:"Eliminar"
	}[lang]

	tl={
		_LANG_EN:"Are you sure you want to delete this asset?",
		_LANG_ES:"¿Está seguro de que quiere eliminar este activo?"
	}[lang]
	html_text=(
		f"""<button hx-delete="{req_url}" """
			f"""class="{_CSS_CLASS_COMMON} {_CSS_CLASS_DANGER}" """
			f"""hx-target="#{_ID_MSGZONE}" """
			f"""hx-confirm="{tl}" """
			# """hx-trigger="submit" """
			"""hx-swap="innerHTML">"""
			f"{html_text}"
		"</button>"
	)

	return html_text

def write_form_add_record(
		lang:str,asset_id:str,
		full:bool=True
	)->str:

	tl={
		_LANG_EN:"Add or remove",
		_LANG_ES:"Agregar o sustraer"
	}[lang]
	html_text=(
		f"{write_html_input_number(_KEY_RECORD_MOD,label=tl,value=0,required=True)}"
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]

	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_TAG,label=tl)}"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	html_text=(
		f"""<div class={_CSS_CLASS_IG_FIELDS}>""" "\n"
			f"{html_text}\n"
		"</div>\n"
		f"{write_html_input_textbox(_KEY_COMMENT,label=tl)}"
	)

	tl={
		_LANG_EN:"Add to history",
		_LANG_ES:"Agregar al historial"
	}[lang]
	html_text=(
		f"""<form hx-post="/api/assets/pool/{asset_id}/history/add" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-swap="innerHTML">""" "\n"

			f"{html_text}\n"

			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_submit(tl)}\n"
			"</div>\n"

		"</form>"
	)

	if full:

		html_text=(

			f"""<div id={_ID_ASSET_HISTORY_FORM}>""" "\n"
				f"{html_text}\n"
			"</div>\n"
		)

	return html_text

def write_button_record_details(
		lang:str,
		asset_id:str,
		record_uid:str
	)->str:

	tl={
		_LANG_EN:"Details",
		_LANG_ES:"Detalles"
	}[lang]

	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			f"""hx-get="/fgmt/assets/pool/{asset_id}/history/records/{record_uid}" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-swap="innerHTML" """
			">"
			f"{tl}"
		"</button>"
	)

def write_html_record(
		lang:str,
		asset_id:str,
		data:Mapping,
		record_uid:Optional[str]=None,
		authorized:bool=False,
		focused:bool=False,
	)->str:

	record_uid_ok:Optional[str]=record_uid

	# print(type(record_uid_ok),record_uid_ok)

	if record_uid_ok is None:

		record_uid_ok=util_valid_str(
			data.get(_KEY_RECORD_UID),
			True
		)

	if record_uid_ok is None:
		print(1)
		return write_div_display_error(lang)

	record_date=util_valid_date(data.get(_KEY_DATE))
	if not isinstance(record_date,str):
		print(2)
		return write_div_display_error(lang)

	record_mod=util_valid_int(data.get(_KEY_RECORD_MOD))
	if not isinstance(record_mod,int):
		print(3)
		return write_div_display_error(lang)

	record_sign=util_valid_str(data.get(_KEY_SIGN),True)
	if not isinstance(record_sign,str):
		print(4)
		return write_div_display_error(lang)

	record_tag=util_valid_str(data.get(_KEY_TAG),True)

	html_text=f"\n<!-- HISTORY RECORD {record_uid_ok} -->"

	tl={
		_LANG_EN:"Adjustment",
		_LANG_ES:"Ajuste",
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"<div><strong>{record_date}</strong></div>\n"
		"<div>\n"
			# f"""<div class="{_CSS_CLASS_HORIZONTAL}">"""
			f"{tl}: {record_mod}"
		"</div>\n"
	)

	if isinstance(record_tag,str):
		tl={
			_LANG_EN:"Tag",
			_LANG_ES:"Etiqueta"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: {record_tag}</div>"
		)

	if authorized:

		html_text=(
			f"{html_text}\n"
			f"{write_button_record_details(lang,asset_id,record_uid_ok)}"
		)

	classes=f"{_CSS_CLASS_COMMON}"
	if focused:
		classes=f"{classes} {_CSS_CLASS_FOCUSED}"

	html_text=(
		f"""<div class="{classes}">""" "\n"
			f"{html_text}\n"
		"</div>"
	)

	return html_text

def write_html_record_detailed(
		lang:str,
		asset_id:str,
		data:Mapping,
		record_uid:Optional[str]=None,
	)->str:

	# TODO: fix must change this to a grid layout

	record_uid_ok=record_uid
	if record_uid_ok is None:
		record_uid_ok=util_valid_str(
			data.get(_KEY_RECORD_UID),
			True
		)
	if record_uid_ok is None:
		return write_div_display_error(lang,data)

	record_date=util_valid_date(data.get(_KEY_DATE))
	record_mod=util_valid_int(data.get(_KEY_RECORD_MOD))

	record_tag=util_valid_str(data.get(_KEY_TAG),True)
	record_comment=util_valid_str(data.get(_KEY_COMMENT))

	record_sign=util_valid_str(
		data.get(_KEY_SIGN),
		True
	)
	record_sign_uname=util_valid_str(
		data.get(_KEY_SIGN_UNAME),
		True
	)

	if (
		(record_date is None) or
		(record_mod is None) or
		(record_sign is None)
	):
		return write_div_display_error(lang,data)

	# tl={
	# 	_LANG_EN:"Record details",
	# 	_LANG_ES:"Detalles del registro"
	# }[lang]

	html_text=(
		# f"{html_text}\n"
		# """<div style="padding-bottom:8px;">""" "\n"
		# 	f"<strong>{tl}</strong>\n"
		# "</div>\n"
		"""<table style="width:100%;text-align:left;">""" "\n"
			"<tbody>\n"
				"<tr>\n"
					"<td>UID</td>\n"
					f"<td>{record_uid_ok}</td>\n"
				"</tr>\n"
	)

	tl={
		_LANG_EN:"Date",
		_LANG_ES:"Fecha"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"<tr>\n"
			f"<td>{tl}</td>\n"
			f"<td>{record_date}</td>\n"
		"</tr>\n"
	)

	tl={
		_LANG_EN:"Asset ID",
		_LANG_ES:"ID del activo"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"<tr>\n"
			f"<td>{tl}</td>\n"
			f"<td>{asset_id}</td>\n"
		"</tr>\n"
	)

	tl={
		_LANG_EN:"Adjustment",
		_LANG_ES:"Ajuste",
	}[lang]
	html_text=(
		f"{html_text}\n"
		"<tr>\n"
			f"<td>{tl}</td>\n"
			f"<td>{record_mod}</td>\n"
		"</tr>\n"
	)

	tl={
		_LANG_EN:"Signed by",
		_LANG_ES:"Firmado por"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"<tr>\n"
			f"<td>{tl}</td>"
	)

	tl=record_sign
	if record_sign_uname is None:
		tl=f"{record_sign_uname} ({tl})"

	html_text=(
			f"{html_text}\n"
			f"<td>{tl}</td>\n"
		"</tr>\n"
	)

	if record_tag is not None:

		tl={
			_LANG_EN:"Tag",
			_LANG_ES:"Etiqueta"
		}[lang]
		html_text=(
			f"{html_text}\n"
			"<tr>\n"
				f"<td>{tl}</td>\n"
				f"<td>{record_tag}</td>\n"
			"</tr>\n"
		)

	if record_comment is not None:

		html_text=(
			f"{html_text}\n"
			"""<tr>""" "\n"
				"<td colspan=2>\n"
					"""<div style="padding-top:8px;">""" "\n"
						f"{record_comment}\n"
					"</div>\n"
				"</td>\n"
			"</tr>\n"
		)

	return (
				f"{html_text}\n"
			"</tbody>\n"
		"</table>"
	)

def write_html_asset_info(
		lang:str,
		asset:Union[tuple,Mapping],
		full:bool=True
	)->str:

	print(
		f"{write_html_asset_info.__name__}()",
		"rendering:",asset
	)

	asset_id:Optional[str]=None
	asset_name:Optional[str]=None

	as_tup=isinstance(asset,tuple)
	as_map=isinstance(asset,Mapping)

	if not (as_tup or as_map):
		return write_div_display_error(lang)

	if as_tup:
		if len(asset)==2:
			asset_id,asset_name=asset

	if as_map:
		asset_id=util_valid_str(asset.get(_KEY_ASSET))
		asset_name=util_valid_str(asset.get(_KEY_NAME))

	if not isinstance(asset_id,str):
		return write_div_display_error(lang)

	if not isinstance(asset_name,str):
		return write_div_display_error(lang)

	html_text=(
		f"<div>"
			f"<strong>{asset_name}</strong>"
		"</div>"
		f"<div>"
			f"ID: <code>{asset_id}</code>"
		"</div>"
	)

	if as_map:

		asset_tag=util_valid_str(asset.get(_KEY_TAG),True)
		if isinstance(asset_tag,str):
			tl={
				_LANG_EN:"Tag",
				_LANG_ES:"Etiqueta"
			}[lang]
			html_text=(
				f"{html_text}\n"
				f"<div>"
					f"{tl}: <code>{asset_tag}</code>"
				"</div>"
			)

		asset_sign=util_valid_str(asset.get(_KEY_SIGN))
		asset_sign_uname=util_valid_str(asset.get(_KEY_SIGN_UNAME))
		signed_raw=(isinstance(asset_sign,str))
		signed_neat=(isinstance(asset_sign_uname,str))
		if signed_raw or signed_neat:
			tl={
				_LANG_EN:"Signed by",
				_LANG_ES:"Firmado por"
			}[lang]
			tl=f"{tl}: "
			if signed_neat:
				tl=f"{tl} [ <code>{asset_sign_uname}</code> ]"
			if signed_raw:
				tl=f"{tl} [ <code>{asset_sign}</code> ]"

			html_text=(
				f"{html_text}\n"
				f"<div>{tl}</div>"
			)

		asset_value=util_valid_int(asset.get(_KEY_VALUE))
		if isinstance(asset_value,int):
			tl={
				_LANG_EN:"Value",
				_LANG_ES:"Valor"
			}[lang]
			html_text=(
				f"{html_text}\n"
				f"<div>{tl}: <code>{asset_value}</code></div>"
			)

		asset_supply=util_valid_int(asset.get(_KEY_SUPPLY))
		print("SUPPLY:",asset_supply)
		if isinstance(asset_supply,int):
			tl={
				_LANG_EN:"Current amount",
				_LANG_ES:"Cantidad actual"
			}[lang]
			html_text=(
				f"{html_text}\n"
				f"""<div>{tl}: <code id="{_ID_ASSET_SUPPLY}-{asset_id}">{asset_supply}</code></div>"""
			)

		asset_comment=util_valid_str(asset.get(_KEY_COMMENT))
		if isinstance(asset_comment,str):
			html_text=(
				f"{html_text}\n"
				f"<div><code>{asset_comment}</code></div>"
			)

	if full:
		html_text=(
			f"""<div id="{_ID_ASSET_INFO}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_button_asset_msgbox(lang,asset_id)->str:

	tl={
		_LANG_EN:"See details",
		_LANG_ES:"Ver detalles"
	}[lang]

	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			f"""hx-get="/fgmt/assets/pool/{asset_id}/details" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-swap="innerHTML" """
			">"
			f"{tl}"
		"</button>"
	)

def write_html_asset_as_item(
		lang:str,
		# the_asset:Mapping,
		asset:Union[tuple,Mapping],
		full:bool=True,
		authorized:bool=True,
		focused:bool=False,
		is_search_result:bool=True
	)->str:

	asset_id:Optional[str]=None

	as_tup=(isinstance(asset,tuple))
	as_map=(isinstance(asset,Mapping))

	if as_tup:
		if len(asset)==2:
			asset_id=asset[0]

	if as_map:
		asset_id=asset.get(_KEY_ASSET)

	html_text=(
		f"""<div id="{_ID_ASSET_INFO}">""" "\n"
			f"{write_html_asset_info(lang,asset,full=False)}\n"
		"</div>\n"
		f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
	)


	if is_search_result:
		html_text=(
			f"{html_text}\n"
			f"{write_button_asset_msgbox(lang,asset_id)}\n"
		)

	html_text=(
		f"{html_text}\n"
		f"{write_button_asset_fullview_or_update(lang,asset_id)}\n"
	)

	if authorized:
		html_text=(
			f"{html_text}\n"
			f"{write_form_drop_asset(lang,asset_id)}\n"
		)

	html_text=(
			f"{html_text}\n"
		"</div>"
	)

	if full:

		classes=f"{_CSS_CLASS_COMMON} {_CSS_CLASS_ITEM_ASSET}"
		if focused:
			classes=f"{classes} {_CSS_CLASS_FOCUSED}"

		html_text=(
			f"""<div id="{html_id_asset(asset_id)}" """
				f"""class="{classes}">""" "\n"

				f"{html_text}\n"

			"</div>"
		)

	return html_text

def write_html_asset_details(
		lang:str,
		the_asset:Mapping,
		authorized:bool=True,
	)->str:

	asset_id=the_asset.get(_KEY_ASSET)
	if asset_id is None:
		return write_div_display_error(lang)

	tl={
		_LANG_EN:"Asset details",
		_LANG_ES:"Detalles del activo"
	}[lang]

	html_text=(
		f"<h3>{tl}</h3>\n"
		f"{write_html_asset_info(lang,the_asset)}"
	)

	if authorized:
		html_text=(
			f"{html_text}\n"
			f"{write_form_edit_asset_definition(lang,asset_id)}"
		)

	html_text=(
		f"{html_text}\n"
		f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
			f"{write_button_asset_fullview_or_update(lang,asset_id,umode=1)}\n"
	)
	if authorized:
		html_text=(
			f"{html_text}\n"
			f"{write_form_drop_asset(lang,asset_id,False)}"
		)

	html_text=(
			f"{html_text}\n"
		"</div>"
	)

	return html_text

def write_html_asset_history_records(
		lang:str,asset_id:str,
		history:Optional[Mapping],
		authorized:bool=True,
	)->str:

	if not isinstance(history,Mapping):
		return "<!-- NO HISTORY YET...? -->"

	if len(history)==0:
		return "<!-- HISTORY IS EMPTY -->"

	html_text=""

	for record_uid in history:

		if not isinstance(
			history.get(record_uid),
			Mapping
		):
			continue

		if len(history[record_uid])==0:
			continue

		html_text=write_html_record(
			lang,asset_id,
			history[record_uid],
			record_uid=record_uid,
			authorized=authorized,
		)+f"\n{html_text}"

	return html_text


def write_html_asset_history(
		lang:str,asset_id:str,
		history:Optional[Mapping],
		authorized:bool,
	)->str:

	tl={
		_LANG_EN:"History",
		_LANG_ES:"Historial"
	}[lang]
	html_text=(
		f"<!-- HISTORY FOR {asset_id} -->\n"
		f"<h3>{tl}</h3>"
	)


	if authorized:
		html_text=(
			f"{html_text}\n"
			f"{write_form_add_record(lang,asset_id)}\n"
		)


	html_text=(
		f"{html_text}\n"
		f"""<div id="{_ID_ASSET_HISTORY_RECORDS}">""" "\n"
			f"{write_html_asset_history_records(lang,asset_id,history,authorized)}\n"
		"</div>"
	)

	return html_text

def write_form_export_assets_as_excel(lang:str):

	html_text=(
		"""<form method="POST" """
			"""action="/api/assets/export-as-spreadsheet" """
			">"
	)

	tl={
		_LANG_EN:"Include full history",
		_LANG_ES:"Incluir historial completo"
	}[lang]
	html_text=(
		f"{html_text}\n"
			"<div>\n"
				f"{write_html_input_checkbox(_KEY_INC_HISTORY,tl)}\n"
			"</div>"
	)

	tl={
		_LANG_EN:"Date",
		_LANG_ES:"Fecha"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"<div>\n"
			f"{write_html_input_date(_KEY_DATE,tl)}"
	)

	tl={
		_LANG_EN:"Initial date",
		_LANG_ES:"Fecha inicial"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_date(_KEY_DATE_MIN,tl)}"
	)

	tl={
		_LANG_EN:"Final date",
		_LANG_ES:"Fecha final"
	}[lang]
	html_text=(
			f"{html_text}\n"
			f"{write_html_input_date(_KEY_DATE_MAX,tl)}\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Performance analysis",
		_LANG_ES:"Análisis de rendimiento"
	}[lang]
	radio_opts=[
		(0,{_LANG_EN:"None",_LANG_ES:"Ninguno"}[lang]),
		(1,{_LANG_EN:"Uphill",_LANG_ES:"Al alza"}[lang]),
		(-1,{_LANG_EN:"Downhill",_LANG_ES:"A la baja"}[lang]),
	]
	html_text=(
		f"{html_text}\n"
		# f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
		"<div>\n"
			"<div>\n"
				f"""<label for="{_KEY_ATYPE}">{tl}</label>""" "\n"
				f"{write_html_input_radio(_KEY_ATYPE,radio_opts)}\n"
			"</div>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Ignore all opposing trends (requires performance analysis)",
		_LANG_ES:"No seguir tendencias opuestas (requiere análisis de rendimiento)"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"<div>\n"
			f"{write_html_input_checkbox(_KEY_FTREND,tl)}\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Export",
		_LANG_ES:"Exportar"
	}[lang]
	html_text=(
				f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_submit(tl)}\n"
				# f"{write_button_reset(lang)}\n"
			"</div>\n"
		"</form>"
	)

	tl={
		_LANG_EN:"Asset report",
		_LANG_ES:"Informe de activos"
	}[lang]

	html_text=(
		# "<div>\n"
		f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
			f"<h3>{tl}</h3>\n"
			f"""<div id="{_ID_ASSETS_TO_SPREADSHEET}">""" "\n"
				f"{html_text}\n"
			"</div>\n"
		"</div>"
	)

	return html_text

