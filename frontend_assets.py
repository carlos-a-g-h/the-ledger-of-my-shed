#!/usr/bin/python3.9

from typing import Mapping
from typing import Optional

from frontend_Any import _LANG_EN,_LANG_ES

# from frontend_Any import _CSS_CLASS_BUTTON
from frontend_Any import _CSS_CLASS_DANGER
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

def write_form_new_asset(lang:str)->str:

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

def write_form_add_modev(lang:str,asset_id:str)->str:

	tl={
		_LANG_EN:"Add or remove",
		_LANG_ES:"Agregar o sustraer"
	}[lang]
	html_text=(
		"<form "
			f"""hx-post="/api/assets/history/{asset_id}/add" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"

			# WARN: HIDDEN INPUT
			"""<input id="modev-asset" """
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

def write_html_modev(lang:str,data:Mapping)->str:

	print("MODEV:",data)

	modev_uid=util_valid_str(data.get("uid"))

	modev_sign=util_valid_str(data.get("sign"))
	if not isinstance(modev_sign,str):
		return write_div_display_error(lang)

	modev_date=util_valid_date(
		util_valid_str(data.get("date"))
	)

	if not isinstance(modev_date,str):
		return write_div_display_error(lang)

	modev_mod=util_valid_int(data.get("mod"))
	if not isinstance(modev_mod,int):
		return write_div_display_error(lang)

	tl_sign={
		_LANG_EN:"Sign",
		_LANG_ES:"Firma"
	}[lang]

	tl_date={
		_LANG_EN:"Date",
		_LANG_ES:"Fecha"
	}[lang]

	tl_mod={
		_LANG_EN:"Adjustment",
		_LANG_ES:"Ajuste"
	}[lang]

	html_text=f"""<div class="{_CSS_CLASS_COMMON}">"""

	if isinstance(modev_uid,str):
		html_text=(
			f"{html_text}\n"
			f"<div>UID: <code>{modev_uid}</code></div>"
		)

	html_text=(
		f"{html_text}\n"
		f"<div>{tl_mod}: <code>{modev_mod}</code></div>\n"
		f"<div>{tl_sign}: <code>{modev_sign}</code></div>\n"
		f"<div>{tl_date}: <code>{modev_date}</code></div>"
	)

	modev_tag=util_valid_str(
		data.get("tag")
	)
	modev_comment=util_valid_str(
		data.get("comment")
	)

	if isinstance(modev_tag,str):
		tl={
			_LANG_EN:"Tag",
			_LANG_ES:"Etiqueta"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{modev_tag}</code></div>\n"
		)

	if isinstance(modev_comment,str):
		tl={
			_LANG_EN:"Comment",
			_LANG_ES:"Comentario"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{modev_comment}</code></div>\n"
		)

	return (
			f"{html_text}\n"
		"</div>\n"
	)

def write_html_modev_history(
		lang:str,
		history:Optional[Mapping]
	):

	if not isinstance(history,Mapping):
		return (
			"<p>"+{
				_LANG_EN:"History is empty/unknown",
				_LANG_ES:"Historial vacío/desconocido"
			}[lang]+"</p>"
		)

	if len(history)==0:
		return (
			"<p>"+{
				_LANG_EN:"History is empty/unknown",
				_LANG_ES:"Historial vacío/desconocido"
			}[lang]+"</p>"
		)

	html_text=""

	for modev_id in history:
		html_text=(
			f"{html_text}\n"
			f"{write_html_modev(lang,history[modev_id])}"
		)

	# 	lang:str,history:list,
	# )->str:

	# html_text=""

	# zero=True
	# size=len(history)
	# if size>0:
	# 	zero=False
	# 	while True:
	# 		size=size-1
	# 		if size<0:
	# 			break
	# 		html_text=(
	# 			f"{html_text}\n"
			# )+write_html_modev(
			# 	lang,history[size]
			# )

	# if zero:
	# 	html_text=(
	# 		f"{html_text}\n"
	# 	)+"<p>"+{
	# 		_LANG_EN:"History is empty/unknown",
	# 		_LANG_ES:"Historial vacío/desconocido"
	# 	}[lang]+"</p>"

	return html_text

def write_html_asset(
		lang:str,
		data:Mapping,
		fullview:bool=False,
	)->str:

	# print(data)

	asset_id=util_valid_str(data.get("id"))
	if not isinstance(asset_id,str):
		return write_div_display_error(lang)

	asset_name=util_valid_str(data.get("name"))
	if not isinstance(asset_name,str):
		return write_div_display_error(lang)

	# asset info

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=(
		f"""<div id="asset-{asset_id}-info" class="{_CSS_CLASS_COMMON}">""" "\n"
			f"<div>ID: <code>{asset_id}</code></div>\n"
			f"<div>{tl}: <code>{asset_name}</code></div>"
	)

	asset_tag=util_valid_str(data.get("tag"))
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

	if fullview:
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

	asset_total=util_valid_int(data.get("total"))
	if isinstance(asset_total,int):
		tl={
			_LANG_EN:"Current ammount",
			_LANG_ES:"Cantidad actual"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"""<div>{tl}: <code id="asset-{asset_id}-total">{asset_total}</code></div>"""
		)

	html_text=(
		f"{html_text}\n"
		f"""<div class="inner-controls" id="asset-{asset_id}-controls">"""
	)

	# view/edit button only,or, delete and refresh buttons

	tl={
		True:{
			_LANG_EN:"Refresh now",
			_LANG_ES:"Actualizar ahora"
		}[lang],
		False:{
			_LANG_EN:"View or edit",
			_LANG_ES:"Ver o editar"
		}[lang]
	}[fullview]

	html_text_get_asset_button=(
		f"""<button class="{_CSS_CLASS_COMMON}" """
			f"""hx-get="/fgmt/assets/editor/{asset_id}" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">"
			f"{tl}"
		"</button>"
	)

	if not fullview:
		tl={
			_LANG_EN:"View or edit",
			_LANG_ES:"Ver o editar"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"{html_text_get_asset_button}"
		)

	if fullview:

		tl={
			_LANG_EN:"Are you sure you want to delete this asset?",
			_LANG_ES:"¿Está seguro de que quiere eliminar este activo?"
		}[lang]
		html_text=(
			f"{html_text}\n"
			"<div>\n"
				f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
					f"{html_text_get_asset_button}\n"
				"</div>\n"
				f"""<div class="{_CSS_CLASS_HORIZONTAL}">""" "\n"
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
				"</div>\n"
			"</div>"
		)

	html_text=(
				f"{html_text}\n"
			"</div>"
		"</div>"
	)

	if fullview:

		tl={
			_LANG_EN:"History",
			_LANG_ES:"Historial"
		}[lang]
		html_modev_history=write_html_modev_history(
			# lang,util_valid_list(
			# 	data.get("history"),True
			# )
			lang,data.get("history")
		)
		html_text=(
			f"{html_text}\n"
			f"<h3>{tl}</h3>\n"
			f"""<div id="asset-{asset_id}-history-ctl" class="{_CSS_CLASS_COMMON}">""" "\n"
				f"{write_form_add_modev(lang,asset_id)}\n"
			"</div>"
			f"""<div id="asset-{asset_id}-history">""" "\n"
				f"{html_modev_history}\n"
			"</div>"
		)

	return html_text

def write_html_list_of_assets(
		lang:str,assetlist:list,
		order_id:Optional[str]=None
	)->str:

	html_text="""<div id="list-of-assets">""" "\n"

	empty=(len(assetlist)==0)

	if empty:
		tl={
			_LANG_EN:"There are no assets",
			_LANG_ES:"No hay activos"
		}[lang]
		html_text=(
			f"{html_text}\n"
			"<div>\n"
				f"{tl}\n"
			"</div>"
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
