#!/usr/bin/python3.9

from typing import Mapping
from typing import Optional

from frontend_Any import (

	_ID_MAIN,_ID_MESSAGES,

	_CSS_CLASS_DANGER,
	_CSS_CLASS_FOCUSED,
	_CSS_CLASS_VUP,
	_CSS_CLASS_VDOWN,
	_CSS_CLASS_COMMON,
	_CSS_CLASS_CONTROLS,
	_CSS_CLASS_HORIZONTAL,
	
	write_div_display_error
)

from internals import (
	util_valid_int,
	util_valid_str,
	util_valid_date
)

from symbols_assets import (

	_KEY_ASSET,
	_KEY_NAME,
	_KEY_VALUE,
	_KEY_TOTAL,

	_KEY_HISTORY,
	_KEY_RECORD_UID,
	_KEY_RECORD_MOD,

	_ID_FORM_NEW_ASSET,
	_ID_RESULT_NEW_ASSET,

	html_id_asset
)

from symbols_Any import (
	_LANG_EN,_LANG_ES,

	_KEY_TAG,
	_KEY_SIGN,_KEY_SIGN_UNAME,
	_KEY_COMMENT,

	_KEY_DELETE_ITEM,
	_KEY_DATE,
)

def write_button_nav_new_asset(lang:str)->str:

	tl={
		_LANG_EN:"Create new asset",
		_LANG_ES:"Crear activo nuevo"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			"""hx-get="/fgmt/assets/new" """
			"""hx-swap="innerHTML" """
			f"""hx-target="#{_ID_MAIN}" """
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
		f"""<button class="{_CSS_CLASS_COMMON}" """
			"""hx-get="/fgmt/assets/search-assets" """
			"""hx-swap="innerHTML" """
			f"""hx-target="#{_ID_MAIN}" """
			">"
			f"{tl}"
		"</button>"
	)

def write_form_new_asset(lang:str,full:bool=True)->str:

	# OK

	html_text=(
		"<form "
			"""hx-post="/api/assets/new" """
			"""hx-trigger="submit" """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML" """
			">\n"
	)

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"<div>\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"""<label class="{_CSS_CLASS_COMMON}" for="{_KEY_NAME}">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					f""" name="{_KEY_NAME}" """
					"""type="text" """
					"""max-length=64 """
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
			f"""<label class="{_CSS_CLASS_COMMON}" for="{_KEY_TAG}">{tl}</label>""" "\n"
			f"""<input class="{_CSS_CLASS_COMMON}" """
				f""" name="{_KEY_TAG}" """
				"""type="text" """
				"""max-length=32 """
				">\n"
		"</div>\n"
	)

	tl={
		_LANG_EN:"Value",
		_LANG_ES:"Valor"
	}[lang]
	html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"""<label class="{_CSS_CLASS_COMMON}" for="{_KEY_VALUE}">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					f""" name="{_KEY_VALUE}" """
					"""type="number" """
					"""value=0 """
					"required>\n"
			"</div>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<label class="{_CSS_CLASS_COMMON}" for="{_KEY_COMMENT}">{tl}</label>""" "\n"
		f"""<textarea class="{_CSS_CLASS_COMMON}" """
			f"""name="{_KEY_COMMENT}" """
			"max-length=256 "
			">"
		"""</textarea>"""
	)

	tl={
		_LANG_EN:"Create asset",
		_LANG_ES:"Crear activo"
	}[lang]
	html_text=(
			f"{html_text}"
			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				"""<button """
					f"""class="{_CSS_CLASS_COMMON}" """
					"""type="submit" """
					">"
					f"{tl}"
				"</button>\n"
			"</div>\n"
		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"Creation of a new asset",
			_LANG_ES:"Creación de un nuevo activo"
		}[lang]
		html_text=(
			f"<h3>{tl}</h3>\n"
			f"""<div id="{_ID_FORM_NEW_ASSET}">""" "\n"
				f"{html_text}\n"
			"</div>\n"
			f"""<div id="{_ID_RESULT_NEW_ASSET}">""" "\n"
				"<!-- NEW ASSET GOES HERE -->\n"
			"</div>"
		)

	return html_text

def write_form_edit_asset_metadata(
		lang:str,asset_id:str,
		full:bool=True,
	)->str:

	tl={
		_LANG_EN:"Edit",
		_LANG_ES:"Editar"
	}[lang]
	html_text=(
		"<!-- ASSET METADATA EDITOR -->\n"
		f"<summary>{tl}</summary>\n"
		f"""<div class="{_CSS_CLASS_VUP}">""" "\n"
			f"""<form hx-post="/api/assets/change-metadata" """ "\n"
				"""hx-swap="innerHTML" """ "\n"
				f"""hx-target="#{_ID_MESSAGES}" """ "\n"
				">\n"
				f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
					f"""<input name="{_KEY_ASSET}" type=hidden value="{asset_id}">"""
	)

	html_text=(
		f"{html_text}\n"
		f"""<div>"""
	)

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=(
		f"{html_text}\n"

		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
			"<div>\n"
				f"""<input name="change-{_KEY_NAME}" type=checkbox>""" "\n"
				f"""<label for=change-{_KEY_NAME}>{tl}</label>""" "\n"
			"</div>\n"
			f"""<input class="{_CSS_CLASS_COMMON}" name="{_KEY_NAME}" type=text max-length=32>""" "\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]
	html_text=(
		f"{html_text}\n"

		f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
			"<div>\n"
				f"""<input name="change-{_KEY_TAG}" type=checkbox>""" "\n"
				f"""<label for=change-{_KEY_TAG}>{tl}</label>""" "\n"
			"</div>\n"
			f"""<input class="{_CSS_CLASS_COMMON}" name="{_KEY_TAG}" type=text max-length=32>""" "\n"
		"</div>"
	)

	html_text=(
			f"{html_text}\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	html_text=(
		f"{html_text}\n"

		"<div>\n"
			f"""<input name="change-{_KEY_COMMENT}" type=checkbox>""" "\n"
			f"""<label for=change-{_KEY_COMMENT}>{tl}</label>""" "\n"
		"</div>\n"
		f"""<textarea class="{_CSS_CLASS_COMMON}" """
			f"""name="{_KEY_COMMENT}" """
			"max-length=256 "
			">"
		"</textarea>"
	)

	tl={
		_LANG_EN:"Apply changes",
		_LANG_ES:"Aplicar cambios"
	}[lang]
	html_text=(
					f"{html_text}\n"

					f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
						f"""<button type="submit" """
							f"""class="{_CSS_CLASS_COMMON}">""" "\n"
								f"{tl}\n"
						"</button>" "\n"
					"</div>\n"
				"</div>\n"
			"</form>\n"
		"</div>"
	)

	if full:
		html_text=(
			f"""<details id="{html_id_asset(asset_id,editor=True)}" """
				f"""class="{_CSS_CLASS_VUP} {_CSS_CLASS_VDOWN}" """
				">\n"
				f"{html_text}\n"
			"</details>"
		)

	return html_text

def write_button_asset_fullview_or_update(
		lang:str,
		asset_id:str,
		in_fullview:bool
	)->str:

	tl={
		True:{
			_LANG_EN:"Refresh now",
			_LANG_ES:"Actualizar ahora"
		}[lang],
		False:{
			_LANG_EN:"View/Manage",
			_LANG_ES:"Ver/Administrar"
		}[lang]
	}[in_fullview]

	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			f"""hx-get="/fgmt/assets/panel/{asset_id}" """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML" """
			">"
			f"{tl}"
		"</button>"
	)

def write_form_delete_asset(
		lang:str,
		asset_id:str,
		delete_entry:bool=True,
	)->str:

	tl={
		_LANG_EN:"Are you sure you want to delete this asset?",
		_LANG_ES:"¿Está seguro de que quiere eliminar este activo?"
	}[lang]
	html_text=(
		"""<form hx-delete="/api/assets/drop" """
			"""hx-trigger="submit" """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML" """
			f"""hx-confirm="{tl}" """
			">\n"

			f"""<input name="{_KEY_ASSET}" type="hidden" value="{asset_id}">"""
	)

	if delete_entry:
		html_text=(
			f"{html_text}\n"
			f"""<input name="{_KEY_DELETE_ITEM}" type="hidden" value="true">"""
		)

	tl={
		_LANG_EN:"Delete this asset",
		_LANG_ES:"Eliminar este activo"
	}[lang]
	html_text=(
		f"{html_text}\n"
			f"""<button class="{_CSS_CLASS_COMMON} {_CSS_CLASS_DANGER}" """
				"""type="submit">"""
				f"{tl}"
			"</button>\n"
		"</form>"
	)

	return html_text

def write_form_add_record(lang:str,asset_id:str)->str:

	html_text=(
		f"""<form hx-post="/api/assets/history/{asset_id}/add" """
			f"""hx-target="#{_ID_MESSAGES}" """
			"""hx-swap="innerHTML" """
			">\n"

			# WARN: HIDDEN INPUT
			f"""<input name="{_KEY_ASSET}" """
				"""type="hidden" """
				f"""value="{asset_id}" """
				"required>\n"
	)

	tl={
		_LANG_EN:"Add or remove",
		_LANG_ES:"Agregar o sustraer"
	}[lang]
	html_text=(
		f"{html_text}\n"

		# NOTE: horizontal content starts
		"<div>"

			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"""<label class="{_CSS_CLASS_COMMON}" for="{_KEY_RECORD_MOD}">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					f"""name="{_KEY_RECORD_MOD}" """
					"""type="number" """
					"""value=0 """
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
				f"""<label class="{_CSS_CLASS_COMMON}" for="{_KEY_TAG}">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					f""" name="{_KEY_TAG}" """
					""" type="text" """
					"""max-length=32 """
					">\n"
			"</div>"

		# NOTE: horizontal content ends
		"</div>\n"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	html_text=(
		f"{html_text}\n"

		f"""<label class="{_CSS_CLASS_COMMON}" for="{_KEY_COMMENT}">{tl}</label>""" "\n"
		f"""<textarea class="{_CSS_CLASS_COMMON}" """ 
			f"""name="{_KEY_COMMENT}" """
			"max-length=256 "
			">"
		"</textarea>"
	)

	tl={
		_LANG_EN:"Add to history",
		_LANG_ES:"Agregar al historial"
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

		# NOTE: end of the form
		"</form>\n"
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
			f"""hx-get="/api/assets/history/{asset_id}/records/{record_uid}" """
			f"""hx-target="#{_ID_MESSAGES}" """
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

	# tl={
	# 	_LANG_EN:"Signed by",
	# 	_LANG_ES:"Firmado por"
	# }[lang]
	# html_text=(
	# 	f"{html_text}\n"
	# 		f"""<div class="{_CSS_CLASS_HORIZONTAL}">"""
	# 			f"{tl}: {record_sign}"
	# 		"</div>\n"
	# 	"</div>"
	# )

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

	tl={
		_LANG_EN:"Record details",
		_LANG_ES:"Detalles del registro"
	}[lang]

	html_text=(
		# f"{html_text}\n"
		"""<div style="padding-bottom:8px;">""" "\n"
			f"<strong>{tl}</strong>\n"
		"</div>\n"
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
		the_asset:Mapping,
		full:bool=True
	)->str:

	print("rendering:",the_asset)

	asset_id=util_valid_str(the_asset.get(_KEY_ASSET))
	if not isinstance(asset_id,str):
		return write_div_display_error(lang)

	asset_name=util_valid_str(the_asset.get(_KEY_NAME))
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

	asset_tag=util_valid_str(the_asset.get(_KEY_TAG),True)
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

	asset_sign=util_valid_str(the_asset.get(_KEY_SIGN))
	asset_sign_uname=util_valid_str(the_asset.get(_KEY_SIGN_UNAME))
	signed_raw=(isinstance(asset_sign,str))
	signed_neat=(isinstance(asset_sign_uname,str))
	if signed_raw or signed_neat:
		tl={
			_LANG_EN:"Signed by",
			_LANG_ES:"Firmado por"
		}[lang]
		if signed_neat:
			tl=f"{tl}: [ <code>{asset_sign_uname}</code> ]"
		if signed_raw:
			tl=f"{tl}: [ <code>{asset_sign}</code> ]"

		html_text=(
			f"{html_text}\n"
			f"<div>{tl}</div>"
		)

	asset_value=util_valid_int(the_asset.get(_KEY_VALUE))
	if isinstance(asset_value,int):
		tl={
			_LANG_EN:"Value",
			_LANG_ES:"Valor"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{asset_value}</code></div>"
		)

	asset_total=util_valid_int(the_asset.get(_KEY_TOTAL))
	if isinstance(asset_total,int):
		tl={
			_LANG_EN:"Current amount",
			_LANG_ES:"Cantidad actual"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"""<div>{tl}: <code id="{html_id_asset(asset_id,total=True)}">{asset_total}</code></div>"""
		)

	asset_comment=util_valid_str(the_asset.get(_KEY_COMMENT))
	if isinstance(asset_comment,str):
		html_text=(
			f"{html_text}\n"
			f"<div><code>{asset_comment}</code></div>"
		)

	if full:
		html_text=(
			f"""<div id="{html_id_asset(asset_id,info=True)}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_html_asset_as_item(
		lang:str,
		the_asset:Mapping,
		full:bool=True,
		authorized:bool=True,
		focused:bool=False,
	)->str:

	asset_id=the_asset.get(_KEY_ASSET)

	html_text=(
		f"{write_html_asset_info(lang,the_asset,False)}\n"
		f"""<div id="{html_id_asset(asset_id,controls=True)}">""" "\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"{write_button_asset_fullview_or_update(lang,asset_id,False)}\n"
			"</div>"
	)
	if authorized:
		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
				f"{write_form_delete_asset(lang,asset_id)}\n"
			"</div>"
		)

	html_text=(
			f"{html_text}\n"
		"</div>"
	)

	if full:

		classes=f"{_CSS_CLASS_COMMON}"
		if focused:
			classes=f"{classes} {_CSS_CLASS_FOCUSED}"

		html_text=(
			f"""<div id="{html_id_asset(asset_id)}" """
				f"""class="{classes}" """
				">\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_html_asset_as_panel(
		lang:str,
		the_asset:Mapping,
		authorized:bool=True,
	)->str:

	asset_id=the_asset.get(_KEY_ASSET)
	if asset_id is None:
		return write_div_display_error(lang)

	html_text=write_html_asset_info(lang,the_asset)

	if authorized:
		html_text=(
			f"{html_text}\n"
			f"{write_form_edit_asset_metadata(lang,asset_id)}"
		)

	html_text=(
		f"{html_text}\n"
		f"""<div id="{html_id_asset(asset_id,controls=True)}">""" "\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">"""
				f"{write_button_asset_fullview_or_update(lang,asset_id,True)}\n"
			"</div>"
	)
	if authorized:
		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">"""
				f"{write_form_delete_asset(lang,asset_id,False)}"
			"</div>"
		)

	html_text=(
				f"{html_text}\n"
			"</div>"
		"</div>"
	)

	# History

	tl={
		_LANG_EN:"History",
		_LANG_ES:"Historial"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"<!-- HISTORY FOR {asset_id} -->\n"
		f"<h3>{tl}</h3>"
	)

	if authorized:
		html_text=(
			f"{html_text}\n"
			f"""<div id="{html_id_asset(asset_id,history=True,controls=True)}">""" "\n"
				f"{write_form_add_record(lang,asset_id)}\n"
			"</div>"
		)

	html_text=(
		f"{html_text}\n"
		f"""<div id="{html_id_asset(asset_id,history=True)}">"""
	)

	history_empty=(not isinstance(the_asset.get(_KEY_HISTORY),Mapping))
	if not history_empty:
		history_empty=(len(the_asset[_KEY_HISTORY])==0)


	if history_empty:

		tl={
			_LANG_EN:"History is empty/unknown",
			_LANG_ES:"Historial vacío/desconocido"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}</div>"
		)

	if not history_empty:

		# The most recent ones will be first

		html_text_history=""

		for record_uid in the_asset[_KEY_HISTORY]:
			if not isinstance(
				the_asset[_KEY_HISTORY].get(record_uid),
				Mapping
			):
				continue

			if len(the_asset[_KEY_HISTORY][record_uid])==0:
				continue

			html_text_history=write_html_record(
				lang,asset_id,
				the_asset[_KEY_HISTORY][record_uid],
				record_uid=record_uid,
				authorized=authorized,
			)+f"\n{html_text_history}"

		if len(html_text_history)>0:
			html_text=f"{html_text}\n{html_text_history}"

	# History ends here

	html_text=(
			f"{html_text}\n"
		"</div>"
	)

	return html_text

