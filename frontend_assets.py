#!/usr/bin/python3.9

from typing import Mapping
from typing import Optional

from symbols_Any import _LANG_EN,_LANG_ES

# from frontend_Any import _CSS_CLASS_BUTTON
from frontend_Any import _CSS_CLASS_DANGER
from frontend_Any import _CSS_CLASS_VUP
from frontend_Any import _CSS_CLASS_VDOWN
# from frontend_Any import _CSS_CLASS_INPUT

from frontend_Any import _CSS_CLASS_COMMON
from frontend_Any import _CSS_CLASS_HORIZONTAL

from frontend_Any import write_div_display_error

# from internals import util_valid_list
from internals import util_valid_str
from internals import util_valid_int
from internals import util_valid_date

def write_button_nav_new_asset(lang:str)->str:

	tl={
		_LANG_EN:"Create new asset",
		_LANG_ES:"Crear activo nuevo"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_COMMON}" """
			"""hx-get="/fgmt/assets/new" """
			"""hx-swap="innerHTML" """
			"""hx-target="#main" """
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
			"""hx-target="#main" """
			">"
			f"{tl}"
		"</button>"
	)

def write_form_new_asset(lang:str,signed_by:str="")->str:

	tl={
		_LANG_EN:"Creation of a new asset",
		_LANG_ES:"Creación de un nuevo activo"
	}[lang]
	html_text=(
		f"<h3>{tl}</h3>\n"
		"<form "
			"""hx-post="/api/assets/new" """
			"""hx-trigger="submit" """
			"""hx-target="#messages" """
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
				f"""<label class="{_CSS_CLASS_COMMON}" for="name">{tl}</label>""" "\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					""" name="name" """
					"""type="text" """
					"""max-length=64 """
					"required>\n"
			"</div>"
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
				f"""value="{signed_by}" """
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
					">\n"
			"</div>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<label class="{_CSS_CLASS_COMMON}" for="comment">{tl}</label>""" "\n"
		f"""<textarea class="{_CSS_CLASS_COMMON}" """
			"""name="comment" """
			"max-length=256 "
			">"
		"""</textarea>"""
	)

	tl={
		_LANG_EN:"Create asset",
		_LANG_ES:"Crear activo"
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
	)

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
				"""hx-target="#messages" """ "\n"
				">\n"
				f"""<input name="id" type=hidden value="{asset_id}">"""
				# f"""<div class="{_CSS_CLASS_COMMON}">"""
				"<div>"
	)

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=(
		f"{html_text}\n"

		"<div>\n"
			f"""<input name="change-name" type=checkbox>""" "\n"
			f"""<label for=change-name>{tl}</label>""" "\n"
		"</div>\n"
		f"""<input class="{_CSS_CLASS_COMMON}" name="name" type=text max-length=32>"""
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]
	html_text=(
		f"{html_text}\n"

		"<div>\n"
			f"""<input name="change-tag" type=checkbox>""" "\n"
			f"""<label for=change-tag>{tl}</label>""" "\n"
		"</div>\n"
		f"""<input class="{_CSS_CLASS_COMMON}" name="tag" type=text max-length=32>"""
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	html_text=(
		f"{html_text}\n"

		"<div>"
			f"""<input name="checkbox-comment" type=checkbox>"""
			f"""<label for=checkbox-comment>{tl}</label>"""
		"</div>"
		f"""<textarea class="{_CSS_CLASS_COMMON}" """
			"""name="comment" """
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

					f"""<button class="common" type="submit">{tl}</button>""" "\n"
				"</div>\n"
			"</form>\n"
		"</div>"
	)

	if full:
		html_text=(
			f"""<details class="{_CSS_CLASS_VUP} {_CSS_CLASS_VDOWN}" """
				f"""id="asset-{asset_id}-editor">""" "\n"
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
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">"
			f"{tl}"
		"</button>"
	)

def write_form_delete_asset(
		lang:str,
		asset_id:str,
	)->str:

	tl={
		_LANG_EN:"Are you sure you want to delete this asset?",
		_LANG_ES:"¿Está seguro de que quiere eliminar este activo?"
	}[lang]
	html_text=(
		"<form "
			"""hx-trigger="submit" """
			"""hx-delete="/api/assets/drop" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			f"""hx-confirm="{tl}" """
			">"
	)

	tl={
		_LANG_EN:"Delete this asset",
		_LANG_ES:"Eliminar este activo"
	}[lang]
	html_text=(
		f"{html_text}\n"
			f"""<input name="id" type="hidden" value="{asset_id}">"""
			f"""<button class="{_CSS_CLASS_COMMON} {_CSS_CLASS_DANGER}" """
				"""type="submit">"""
				f"{tl}"
			"</button>\n"
		"</form>\n"
	)

	return html_text

def write_form_search_assets(
		lang:str,
		order_id:Optional[str]=None
	)->str:

	order_specific=isinstance(order_id,str)

	the_route={
		True:f"/api/orders/current/{order_id}/search-assets",
		False:"/api/assets/search-assets"
	}[order_specific]

	tl={
		_LANG_EN:"Asset searcher",
		_LANG_ES:"Buscador de activos"
	}[lang]
	html_text=(
		f"<h3>{tl}</h3>\n"
	)

	if order_specific:
		tl={
			_LANG_EN:"Go to the editor",
			_LANG_ES:"Ir al editor"
		}[lang]
		html_text=(
			f"{html_text}\n"
			"<div>\n"
				f"ID: {order_id}"
			"</div>\n"
			"<div>\n"
				f"""<button class="{_CSS_CLASS_COMMON}" """
					f"""hx-get="/fgmt/orders/current/{order_id}/editor" """
					"""hx-target="#messages" """
					"""hx-swap="innerHTML" """
					">\n"
					f"{tl}\n"
				"</button>\n"
			"</div>"
		)

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"""<form """
			f"""hx-post="{the_route}" """
			"""hx-trigger="submit" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">"
				"<div>\n"
					f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
						f"""<label class="{_CSS_CLASS_COMMON}" for="name">{tl}</label>"""
						"\n"
						f"""<input class="{_CSS_CLASS_COMMON}" """
							"""name="name" """
							"""type="text" """
							"""max-length=32 """
							">\n"
					"</div>"
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
				"""name="sign" """
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
				f"""<label class="{_CSS_CLASS_COMMON}" for="tag">{tl}</label>"""
				"\n"
				f"""<input class="{_CSS_CLASS_COMMON}" """
					"""name="tag" """
					"""type="text" """
					"""max-length=32 """
					">\n"
			"</div>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Perform search",
		_LANG_ES:"Realizar búsqueda"
	}[lang]

	return (
			f"{html_text}\n"

			"""<button type="submit" """
				f"""class="{_CSS_CLASS_COMMON}" """
				">"
				f"{tl}"
			"</button>\n"
		"</form>"
	)

def write_form_add_record(lang:str,asset_id:str,username:str="")->str:

	tl={
		_LANG_EN:"Add or remove",
		_LANG_ES:"Agregar o sustraer"
	}[lang]
	html_text=(
		"<!-- ADD RECORD FORM -->\n"
		"<form "
			f"""hx-post="/api/assets/history/{asset_id}/add" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"

			# WARN: HIDDEN INPUT
			"""<input id="record-asset" """
				"""name="asset-id" """
				"""type="hidden" """
				f"""value="{asset_id}" """
				">\n"

			"<div>"

				f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
					f"""<label class="{_CSS_CLASS_COMMON}" for="mod">{tl}</label>""" "\n"
					f"""<input class="{_CSS_CLASS_COMMON}" """
						""" name="mod" """
						"""type="number" """
						"""value=0 """
						"required>\n"
				"</div>"
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
				""" type="text" """
				"""max-length=32 """
				f"""value="{username}" """
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
				""" type="text" """
				"""max-length=32 """
				">\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]
	html_text=(
			f"{html_text}\n"
		"</div>\n"
		f"""<label class="{_CSS_CLASS_COMMON}" for="comment">{tl}</label>""" "\n"
		f"""<textarea class="{_CSS_CLASS_COMMON}" """ 
			"""name="comment" """
			"max-length=256 "
			">"
		"</textarea>"
	)

	tl={
		_LANG_EN:"Add to history",
		_LANG_ES:"Agregar al historial"
	}[lang]

	return (
			f"{html_text}\n"
			"""<button type="submit" """
				f"""class="{_CSS_CLASS_COMMON}" """
				">"
				f"{tl}"
			"</button>\n"
		"</form>\n"
	)


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
			"""hx-target="#messages" """
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
		detailed:bool=False,
		authorized:bool=False,
	)->str:

	record_uid_ok:Optional[str]=record_uid

	print(type(record_uid_ok),record_uid_ok)

	if record_uid_ok is None:

		print("???",record_uid_ok)

		record_uid_ok=util_valid_str(
			data.get("uid"),
			True
		)

	if record_uid_ok is None:
		print(1)
		return write_div_display_error(lang)

	record_date=util_valid_date(data.get("date"))
	if not isinstance(record_date,str):
		print(2)
		return write_div_display_error(lang)

	record_mod=util_valid_int(data.get("mod"))
	if not isinstance(record_mod,int):
		print(3)
		return write_div_display_error(lang)

	record_sign=util_valid_str(data.get("sign"),True)
	if not isinstance(record_sign,str):
		print(4)
		return write_div_display_error(lang)

	record_tag=util_valid_str(data.get("tag"),True)

	html_text=f"<!-- HISTORY RECORD {record_uid_ok} -->"

	if not detailed:

		tl={
			_LANG_EN:"Adjustment",
			_LANG_ES:"Ajuste",
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div><strong>{record_date}</strong></div>\n"
			"<div>\n"
				f"""<div class="{_CSS_CLASS_HORIZONTAL}">"""
					f"{tl}: {record_mod}"
				"</div>\n"
		)

		tl={
			_LANG_EN:"Signed by",
			_LANG_ES:"Firmado por"
		}[lang]
		html_text=(
			f"{html_text}\n"
				f"""<div class="{_CSS_CLASS_HORIZONTAL}">"""
					f"{tl}: {record_sign}"
				"</div>\n"
			"</div>"
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

			html_text=f"{html_text}\n"+write_button_record_details(
				lang,asset_id,
				record_uid_ok
			)

		html_text=(
			f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	if detailed and authorized:

		tl={
			_LANG_EN:"Record details",
			_LANG_ES:"Detalles del registro"
		}[lang]
		html_text=(
			f"{html_text}\n"
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
			_LANG_EN:"From asset",
			_LANG_ES:"Del activo"
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
				f"<td>{tl}</td>\n"
				f"<td>{record_sign}</td>\n"
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

		record_comment=util_valid_str(data.get("comment"),True)
		if record_comment is not None:

			html_text=(
				f"{html_text}\n"
				"""<tr>""" "\n"
					"<td colspan=2>\n"
						"""<div style="padding-top:8px;">""" "\n"
							f"{record_comment}"
						"</div>"
					"</td>\n"
				"</tr>\n"
			)

		html_text=(
					f"{html_text}\n"
				"</tbody>\n"
			"</table>"
		)

	return html_text

def write_html_asset_info(
		lang:str,data:Mapping,
		full:bool=True
	)->str:

	asset_id=util_valid_str(data.get("id"))
	if not isinstance(asset_id,str):
		return write_div_display_error(lang)

	asset_name=util_valid_str(data.get("name"))
	if not isinstance(asset_name,str):
		return write_div_display_error(lang)

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=(
		f"<div>ID: <code>{asset_id}</code></div>\n"
		f"<div>{tl}: <code>{asset_name}</code></div>"
	)

	asset_tag=util_valid_str(data.get("tag"),True)
	if isinstance(asset_tag,str):
		tl={
			_LANG_EN:"Tag",
			_LANG_ES:"Etiqueta"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{asset_tag}</code></div>"
		)

	asset_sign=util_valid_str(data.get("sign"))
	if isinstance(asset_sign,str):
		tl={
			_LANG_EN:"Sign",
			_LANG_ES:"Firma"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{asset_sign}</code></div>"
		)

	asset_comment=util_valid_str(data.get("comment"))
	if isinstance(asset_comment,str):
		tl={
			_LANG_EN:"Comment",
			_LANG_ES:"Comentario"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{asset_comment}</code></div>"
		)

	if full:
		html_text=(
			f"""<div id="asset-{asset_id}-info">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_html_asset(
		lang:str,
		data:Mapping,
		fullview:bool=False,
		username:Optional[str]=None,
	)->str:

	print("ASSET PRINTED BY",username)

	has_username=isinstance(username,str)

	asset_id=util_valid_str(data.get("id"))
	if not isinstance(asset_id,str):
		return write_div_display_error(lang)

	# info

	html_text=(
		f"<!-- ASSET {asset_id} -->\n"
		f"""<div class={_CSS_CLASS_COMMON} id="asset-{asset_id}">""" "\n"
			f"{write_html_asset_info(lang,data,fullview)}"
	)

	asset_total=util_valid_int(data.get("total"))
	if isinstance(asset_total,int):
		tl={
			_LANG_EN:"Current amount",
			_LANG_ES:"Cantidad actual"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"""<div>{tl}: <code id="asset-{asset_id}-total">{asset_total}</code></div>"""
		)

	if fullview and has_username:
		html_text=(
			f"{html_text}\n"
			f"{write_form_edit_asset_metadata(lang,asset_id)}"
		)

	# Actions

	html_text=(
		f"{html_text}\n"
		f"""<div class="inner-controls" id="asset-{asset_id}-controls">""" "\n"
			f"{write_button_asset_fullview_or_update(lang,asset_id,fullview)}\n"
	)

	if fullview and has_username:

		html_text=(
			f"{html_text}\n"
			f"{write_form_delete_asset(lang,asset_id)}"
		)

	html_text=(
				f"{html_text}\n"
			"</div>"
		"</div>"
	)

	if fullview:

		# History

		tl={
			_LANG_EN:"History",
			_LANG_ES:"Historial"
		}[lang]
		# html_record_history=write_html_record_history(
		# 	lang,asset_id,
		# 	data.get("history")
		# )
		html_text=(
			f"{html_text}\n"
			f"<!-- HISTORY FOR {asset_id} -->\n"
			f"<h3>{tl}</h3>"
		)

		if has_username:
			html_text=(
				f"{html_text}\n"
				f"""<div id="asset-{asset_id}-history-ctl" class="{_CSS_CLASS_COMMON}">""" "\n"
					f"{write_form_add_record(lang,asset_id,username)}\n"
				"</div>"
			)

		# History starts here

		html_text=(
			f"{html_text}\n"
			f"""<div id="asset-{asset_id}-history">"""
		)

		history_empty=(not isinstance(data.get("history"),Mapping))
		if not history_empty:
			history_empty=(len(data["history"])==0)

		# print("HISTORY",data["history"])

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

			for record_uid in data["history"]:
				if not isinstance(
					data["history"].get(record_uid),
					Mapping
				):
					continue

				if len(data["history"][record_uid])==0:
					continue

				html_text_history=write_html_record(
					lang,asset_id,
					data["history"][record_uid],
					record_uid=record_uid,
					authorized=has_username,
				)+f"\n{html_text_history}"


			if len(html_text_history)>0:
				html_text=f"{html_text}\n{html_text_history}"

		# History ends here

		html_text=(
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_html_list_of_assets(
		lang:str,assetlist:list,
		order_id:Optional[str]=None
	)->str:

	html_text="""<div id="list-of-assets">"""

	empty=(len(assetlist)==0)

	if empty:
		tl={
			_LANG_EN:"There are no assets",
			_LANG_ES:"No hay activos"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}</div>"
		)

	if not empty:

		x=len(assetlist)
		while True:
			x=x-1
			if x<0:
				break
			html_text=(
				f"{html_text}\n"
				f"{write_html_asset(lang,assetlist[x])}"
			)

	return (
			f"{html_text}\n"
		"</div>"
	)
