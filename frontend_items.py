#!/usr/bin/python3.9


from typing import Mapping
# from typing import Optional

from frontend_Any import _LANG_EN
from frontend_Any import _LANG_ES

from internals import util_valid_list
from internals import util_valid_str
from internals import util_valid_int

def write_div_display_error(lang)->str:
	html_text=(
		"""<div class="display-error">""" "\n"
	)

	html_text=f"{html_text}"+{
		_LANG_EN:"Display error",
		_LANG_ES:"Error al mostrar"
	}[lang]

	return (
			f"{html_text}\n"
		"<div>\n"
	)

def write_button_new_item(lang)->str:

	html_text=(
		"""<button class="common" """
			"""hx-get="/fgmt/items/new" """
			"""hx-swap="innerHTML" """
			"""hx-target="#main" """
			">"
	)

	html_text=f"{html_text}"+{
		_LANG_EN:"Create new item",
		_LANG_ES:"Crear objeto nuevo"
	}[lang]

	return (
			f"{html_text}"
		"</button>\n"
	)

def write_button_search_items(lang)->str:

	html_text=(
		"""<button class="common" """
			"""hx-get="/fgmt/items/search" """
			"""hx-swap="innerHTML" """
			"""hx-target="#main" """
			">"
	)

	html_text=f"{html_text}"+{
		_LANG_EN:"Search item(s)",
		_LANG_ES:"Buscar objeto(s)"
	}[lang]

	return (
			f"{html_text}"
		"</button>"
	)

def write_form_new_item(lang)->str:

	tl={
		_LANG_EN:"Creation of a new item",
		_LANG_ES:"Creación de un nuevo objeto"
	}[lang]

	html_text=(
		f"<h3>{tl}</h3>\n"
		"""<form """
			"""hx-post="/api/items/new" """
			"""hx-trigger="submit" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"

		"<div>"
	)

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]

	html_text=(
		f"{html_text}"
		"""<div class="hcontainer">""" "\n"
			f"""<label style="display:block;" for="item-name">{tl}</label>""" "\n"
			"""<input class="common" """
				""" id="item-name" """
				""" name="name" """
				"""type="text" """
				"""max-length=64 """
				">\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Sign",
		_LANG_ES:"Firma"
	}[lang]

	html_text=(
		f"{html_text}"
		"""<div class="hcontainer">""" "\n"
			f"""<label style="display:block;" for="item-sign">{tl}</label>""" "\n"
			"""<input class="common" """
				""" id="item-sign" """
				""" name="sign" """
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
		f"{html_text}"
		"""<div class="hcontainer">""" "\n"
			f"""<label style="display:block;" for="item-tag">{tl}</label>""" "\n"
			"""<input class="common" """
				""" id="item-tag" """
				""" name="tag" """
				"""type="text" """
				"""max-length=32 """
				">\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]

	html_text=(
			f"{html_text}"
		"</div>"
		f"""<label style="display:block;" for="item-comment">{tl}</label>"""
		"""<textarea class="common" id="item-comment" name="comment" """
			""" max-length=256 ></textarea>"""
	)

	tl={
		_LANG_EN:"Create",
		_LANG_ES:"Crear"
	}[lang]

	return (
			f"{html_text}"
			"""<button """
				"""type="submit" """
				"""class="common" """
				">"
				f"{tl}"
			"</button>"
		"</form>"
	)

def write_form_search_items(lang)->str:

	tl={
		_LANG_EN:"Item(s) searcher",
		_LANG_ES:"Buscador de objetos"
	}[lang]

	html_text=(
		f"<h3>{tl}</h3>\n"
		"""<form """
			"""hx-post="/api/items/search" """
			"""hx-trigger="submit" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">"

			"<div>"

		# """<label for="item-name">Name</label>""" "\n"
		# "<div>\n"
		# 	"""<input id="item-name" name="name" """
		# 		"""type="text" max-length=64 >""" "\n"
		# "</div>\n"

		# """<label for="item-id">ID</label>""" "\n"
		# "<div>\n"
		# 	"""<input id="item-id" name="id" """
		# 		""" type="text" max-length=16 >""" "\n"
		# "</div>\n"
	)

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]

	html_text=(
		f"{html_text}"
		"""<div class="hcontainer">""" "\n"
			f"""<label style="display:block;" for="item-name">{tl}</label>""" "\n"
			"""<input class="common" """
				"""id="item-name" """
				"""name="name" """
				"""type="text" """
				"""max-length=32 """
				">\n"
		"</div>\n"
	)

	tl={
		_LANG_EN:"Sign",
		_LANG_ES:"Firma"
	}[lang]

	html_text=(
		f"{html_text}"
		"""<div class="hcontainer">""" "\n"
			f"""<label style="display:block;" for="item-sign">{tl}</label>""" "\n"
			"""<input class="common" """
				"""id="item-sign" """
				"""name="sign" """
				"""type="text" """
				"""max-length=32 """
				">\n"
		"</div>\n"
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]

	html_text=(
		f"{html_text}"
		"""<div class="hcontainer">""" "\n"
			f"""<label style="display:block;" for="item-tag">{tl}</label>""" "\n"
			"""<input class="common" """
				"""id="item-tag" """
				"""name="tag" """
				"""type="text" """
				"""max-length=32 """
				">\n"
		"</div>\n"
	)

	tl={
		_LANG_EN:"Perform search",
		_LANG_ES:"Realizar búsqueda"
	}[lang]

	return (
				f"{html_text}\n"
			"</div>\n"

			"""<button """
				"""type="submit" """
				"""class="common" """
				">"
				f"{tl}"
			"</button>\n"
		"</form>\n"
	)

def write_form_add_modev(lang:str,item_id:str)->str:

	tl={
		_LANG_EN:"Add or remove",
		_LANG_ES:"Agregar o sustraer"
	}[lang]

	html_text=(

		"<form "
			f"""hx-post="/api/items/history/{item_id}/add" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">\n"

			# WARN: HIDDEN INPUT
			"""<input id="modev-item" """
				"""name="item-id" """
				"""type="hidden" """
				f"""value="{item_id}" """
				">\n"

			"""<div class="hcontainer">""" "\n"
				f"""<label style="display:block;" for="modev-mod">{tl}</label>""" "\n"
				"""<input class="common" """
					"""id="modev-mod" """
					""" name="mod" """
					"""type="number" """
					"""value=0 """
					">\n"
			"</div>"
	)

	tl={
		_LANG_EN:"Sign",
		_LANG_ES:"Firma"
	}[lang]

	html_text=(
		f"{html_text}"
		"""<div class="hcontainer">""" "\n"
			f"""<label style="display:block;" for="modev-sign">{tl}</label>""" "\n"
			"""<input class="common" """
				"""  id="modev-sign" """
				""" name="sign" """
				""" type="text" """
				"""max-length=32 """
				">\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Tag",
		_LANG_ES:"Etiqueta"
	}[lang]

	html_text=(
		f"{html_text}"
		"""<div class="hcontainer">""" "\n"
			f"""<label style="display:block;" for="modev-tag">{tl}</label>""" "\n"
			"""<input class="common" """
				"""  id="modev-tag" """
				""" name="tag" """
				""" type="text" """
				"""max-length=32 """
				">\n"
		"</div>\n"
	)

	tl={
		_LANG_EN:"Comment",
		_LANG_ES:"Comentario"
	}[lang]

	html_text=(
		f"{html_text}"
		f"""<label style="display:block;" for="modev-comment">{tl}</label>"""
		"""<textarea class="common" id="modev-comment" name="comment" """
			"""max-length=256 ></textarea>"""
	)


	tl={
		_LANG_EN:"Add to history",
		_LANG_ES:"Agregar al historial"
	}[lang]

	return (
			f"{html_text}\n"
			"""<button """
				"""type="submit" """
				"""class="common" """
				">"
				f"{tl}"
			"</button>\n"
		"</form>\n"
		# "</div>\n"
	)

def write_html_modev(lang:str,data:Mapping)->str:

	modev_uid=util_valid_str(data.get("uid"))
	if not isinstance(modev_uid,str):
		return write_div_display_error(lang)

	modev_sign=util_valid_str(data.get("sign"))
	if not isinstance(modev_sign,str):
		return write_div_display_error(lang)

	modev_date=util_valid_str(data.get("date"))
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

	html_text=(
		"""<div class="common">""" "\n"
			f"<div>UID: <code>{modev_uid}</code></div>\n"
			f"<div>{tl_mod}: <code>{modev_mod}</code></div>\n"
			f"<div>{tl_sign}: <code>{modev_sign}</code></div>\n"
			f"<div>{tl_date}: <code>{modev_date}</code></div>\n"
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
		lang:str,history:list,
	)->str:

	html_text=""

	# outer=(isinstance(item_id,str))

	# if outer:
	# 	html_text=(
	# 		f"""<div id="item-{item_id}-history">"""
	# 	)

	zero=True
	size=len(history)
	if size>0:
		zero=False
		while True:
			size=size-1
			if size<0:
				break
			html_text=(
				f"{html_text}\n"
			)+write_html_modev(
				lang,history[size]
			)

	if zero:
		html_text=(
			f"{html_text}\n"
		)+"<p>"+{
			_LANG_EN:"History is empty/unknown",
			_LANG_ES:"Historial vacío/desconocido"
		}[lang]+"</p>"

	# if outer:
	# 	html_text=(
	# 			f"{html_text}\n"
	# 		"</div>"
	# 	)

	return html_text


def write_html_item(
		lang:str,
		data:Mapping,
		fullview:bool=False,
	)->str:

	print(data)

	item_id=util_valid_str(data.get("id"))
	if not isinstance(item_id,str):
		return write_div_display_error(lang)

	item_name=util_valid_str(data.get("name"))
	if not isinstance(item_name,str):
		return write_div_display_error(lang)

	# Item info

	tl={
		_LANG_EN:"Name",
		_LANG_ES:"Nombre"
	}[lang]
	html_text=(
		f"""<div class="common" id="item-{item_id}-info">""" "\n"
			f"<div>ID: <code>{item_id}</code></div>\n"
			f"<div>{tl}: <code>{item_name}</code></div>"
	)

	item_tag=util_valid_str(data.get("tag"))
	if isinstance(item_tag,str):
		tl={
			_LANG_EN:"Tag",
			_LANG_ES:"Etiqueta"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{item_tag}</code></div>"
		)

	item_sign=util_valid_str(data.get("sign"))
	if isinstance(item_sign,str):
		tl={
			_LANG_EN:"Sign",
			_LANG_ES:"Firma"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<div>{tl}: <code>{item_sign}</code></div>"
		)

	item_total=util_valid_int(data.get("total"))
	if isinstance(item_total,int):
		tl={
			_LANG_EN:"Current ammount",
			_LANG_ES:"Cantidad actual"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"""<div>{tl}: <code id="item-{item_id}-total">{item_total}</code></div>"""
		)

	html_text=(
		f"{html_text}\n"
		f"""<div class="inner-controls" id="item-{item_id}-controls">"""
	)

	# Delete or view/edit button

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

	html_text=(
		f"{html_text}\n"
		"""<button class="common" """
			f"""hx-get="/fgmt/items/get/{item_id}" """
			"""hx-target="#messages" """
			"""hx-swap="innerHTML" """
			">"
			f"{tl}"
		"</button>"
	)

	if fullview:

		tl={
			_LANG_EN:"Are you sure you want to delete this item?",
			_LANG_ES:"¿Está seguro de que quiere eliminar este objeto?"
		}[lang]

		html_text=(
			f"{html_text}\n"
			"""<form class="horiz" """
				"""hx-trigger="submit" """
				"""hx-delete="/api/items/drop" """
				"""hx-target="#messages" """
				"""hx-swap="innerHTML" """
				f"""hx-confirm="{tl}" """
				">\n"
		)

		tl={
			_LANG_EN:"Delete this item",
			_LANG_ES:"Eliminar este objeto"
		}[lang]
		html_text=(
				f"{html_text}\n"
				f"""<input name="id" type="hidden" value="{item_id}">"""
				"""<button type="submit" class="common">"""
					f"{tl}"
				"</button>\n"
			"</form>"
		)

	html_text=(
				f"{html_text}\n"
			"</div>\n"
		"</div>\n"
	)

	if fullview:

		tl={
			_LANG_EN:"History",
			_LANG_ES:"Historial"
		}[lang]
		html_modev_history=write_html_modev_history(
			lang,util_valid_list(
				data.get("history"),True
			)
		)
		html_text=(
			f"{html_text}\n"
			f"<h3>{tl}</h3>\n"
			f"""<div id="item-{item_id}-history-ctl">""" "\n"
				f"{write_form_add_modev(lang,item_id)}\n"
			"</div>"
			f"""<div id="item-{item_id}-history">""" "\n"
				f"{html_modev_history}\n"
			"</div>"
		)

	return html_text

	# 	# MODEV History

	# 	html_text=(
	# 		f"{html_text}\n"
	# 		f"""<div id="item-{item_id}-history-ctl">"""
	# 			f"{write_form_add_modev(lang,item_id)}\n"
	# 		"</div>"
	# 	)

	# html_text=(
	# 		f"{html_text}"
	# 	"</div>\n"
	# )

	# if not has_controls:
	# 	return html_text

	# tl={
	# 	_LANG_EN:"History",
	# 	_LANG_ES:"Historial"
	# }[lang]

	# html_text=(
	# 	f"{html_text}\n"
	# 	f"<h3>{tl}</h3>\n"
	# 	f"""<div id="item-{item_id}-history">""" "\n"
	# )+write_html_modev_history(
	# 	lang,
	# )+"</div>"

	# at_least_one=False
	# if "history" in data.keys():
	# 	if isinstance(data["history"],list):
	# 		size=len(data["history"])
	# 		if size>0:
	# 			at_least_one=True
	# 			while True:
	# 				size=size-1
	# 				if size<0:
	# 					break
	# 				html_text=(
	# 					f"{html_text}"
	# 				)+write_html_modev(
	# 					lang,data["history"][size]
	# 				)

	# if not at_least_one:
	# 	html_text=(
	# 		f"{html_text}\n"
	# 	)+"<p>"+{
	# 		_LANG_EN:"History is empty/unknown",
	# 		_LANG_ES:"Historial vacío/desconocido"
	# 	}[lang]+"</p>"

	# return (
	# 		f"{html_text}\n"
	# 	"</div>\n"
	# )

def write_html_list_of_items(
		lang:str,itemlist:list,
		reverse:bool=False
	)->str:

	html_text="""<div id="list-of-items">""" "\n"

	empty=(len(itemlist)==0)

	if empty:
		html_text=(
			f"{html_text}\n"
			"""<div class="grayed">""" "\n"
				"There are no items"
			"</div>\n"
		)

	if not empty:

		if not reverse:
			for item in itemlist:
				html_text=(
					f"{html_text}\n"
					f"{write_html_item(lang,item)}"
				)

		if reverse:
			x=len(itemlist)
			while True:
				x=x-1
				if x<0:
					break
				html_text=(
					f"{html_text}\n"
					f"{write_html_item(lang,itemlist[x])}"
				)

	return (
			f"{html_text}\n"
		"</div>\n"
	)
