#!/usr/bin/python3.9

from typing import Mapping

from symbols_Any import (
	_LANG_EN,_LANG_ES,
	_CFG_PORT_MIN,_CFG_PORT_MAX,
	_CFG_LANG,_CFG_PORT,

	_KEY_DELETE_AS_ITEM,
)

from symbols_admin import (
	_ID_MISC_SETTINGS,
	_ID_UKANC,
	_ID_CREATE_USER,
	_ID_SEARCH_USERS,

	_ROUTE_FGMT_MISC,
		_ROUTE_API_MISC_CHANGE_CONFIG,
		_ROUTE_API_MISC_UKANC,

	_ROUTE_FGMT_USERS,
		_ROUTE_API_USERS_NEW,
		_ROUTE_API_USERS_SEARCH,
		_ROUTE_API_USERS_DELETE,

)

from symbols_accounts import (
	_KEY_USERID,
	_KEY_USERNAME,

	_KEY_CON_EMAIL,
	_KEY_CON_TELEGRAM,
	id_user,
)

from frontend_Any import (

	_ID_MSGZONE,

	_CSS_CLASS_COMMON,
	_CSS_CLASS_CONTROLS,
	_CSS_CLASS_DANGER,
	_CSS_CLASS_NAV,

	_CSS_CLASS_IG_FIELDS,

	write_button_submit,

	write_html_input_radio,
	write_html_input_string,
	write_html_input_checkbox,
	write_html_input_number
)

from frontend_accounts import write_html_user

def write_button_nav_users(lang:str)->str:
	tl={
		_LANG_EN:"Users control panel",
		_LANG_ES:"Panel de control de usuarios"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_NAV}" """
			f"""hx-get="{_ROUTE_FGMT_USERS}" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-swap="innerHTML">"""
			f"{tl}"
		"</button>"
	)

def write_button_nav_misc_settings(lang:str)->str:
	tl={
		_LANG_EN:"Misc settings",
		_LANG_ES:"Ajustes varios"
	}[lang]
	return (
		f"""<button class="{_CSS_CLASS_NAV}" """
			f"""hx-get="{_ROUTE_FGMT_MISC}" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-swap="innerHTML">"""
			f"{tl}"
		"</button>"
	)

def write_form_new_user(
		lang:str,
		show_title:bool=True,
		full:bool=True
	)->str:

	# POST: /api/admin/users/new-user

	tl={
		_LANG_EN:"Username",
		_LANG_ES:"Nombre de usuario"
	}[lang]
	html_text=(
		f"{write_html_input_string(_KEY_USERNAME,label=tl,maxlen=24,required=True)}"
	)

	tl={
		_LANG_EN:"E-Mail",
		_LANG_ES:"Correo electrónico"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_CON_EMAIL,label=tl,maxlen=24,input_type=1)}"
	)

	tl={
		_LANG_EN:"Telegram User",
		_LANG_ES:"Usuario de Telegram"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_CON_TELEGRAM,label=tl,maxlen=24)}"
	)

	tl={
		_LANG_EN:"Create",
		_LANG_ES:"Crear"
	}[lang]
	html_text=(
		f"""<form hx-post="{_ROUTE_API_USERS_NEW}" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-trigger="submit" """
			"""hx-swap="innerHTML">""" "\n"

			f"""<div class="{_CSS_CLASS_IG_FIELDS}">""" "\n"
				f"{html_text}\n"
			"</div>\n"

			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_submit(tl)}\n"
			"</div>\n"

		"</form>"
	)

	if full:

		html_text=(
			f"""<div id="{_ID_CREATE_USER}-inner">""" "\n"
				f"{html_text}\n"
			"</div>\n"
			# f"""<div id="{_ID_CREATE_USER}-result">""" "\n"
			# 	"<!-- RECENTLY CREATED USERS GO HERE -->\n"
			# "</div>"
		)

		if show_title:
			tl={
				_LANG_EN:"User creation",
				_LANG_ES:"Creación de usuarios"
			}[lang]
			html_text=(
				f"<h3>{tl}</h3>\n"
				f"{html_text}"
			)

		html_text=(
			f"""<div id="{_ID_CREATE_USER}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_form_search_users(
		lang:str,
		show_title:bool=True,
		full:bool=True
	)->str:

	# POST: /api/admin/users/search

	tl={
		_LANG_EN:"Username",
		_LANG_ES:"Nombre de usuario"
	}[lang]
	html_text=(
		f"{write_html_input_string(_KEY_USERNAME,label=tl,maxlen=24)}\n"
	)

	tl={
		_LANG_EN:"E-Mail",
		_LANG_ES:"Correo electrónico"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_CON_EMAIL,label=tl,maxlen=24,input_type=1)}\n"
	)

	tl={
		_LANG_EN:"Telegram User ID",
		_LANG_ES:"ID de usuario de Telegram"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_html_input_string(_KEY_CON_TELEGRAM,label=tl,maxlen=24)}"
	)

	tl={
		_LANG_EN:"Search",
		_LANG_ES:"Buscar"
	}[lang]
	html_text=(
		f"""<form hx-post="{_ROUTE_API_USERS_SEARCH}" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-trigger="submit" """
			"""hx-swap="innerHTML">""" "\n"

			f"""<div class="{_CSS_CLASS_IG_FIELDS}">""" "\n"
				f"{html_text}\n"
			"</div>\n"
			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_submit(tl)}\n"
			"</div>\n"

		"</form>"
	)

	if full:

		html_text=(
			f"""<div id="{_ID_SEARCH_USERS}-inner">""" "\n"
				f"{html_text}\n"
			"</div>\n"
			# f"""<div id="{_ID_SEARCH_USERS}-result">""" "\n"
			# 	"<!-- SEARCH RESULTS GO HERE -->\n"
			# "</div>"
		)

		if show_title:

			tl={
				_LANG_EN:"User(s) search",
				_LANG_ES:"Búsqueda de usuario(s)"
			}[lang]
			html_text=(
				f"<h3>{tl}</h3>\n"
				f"{html_text}"
			)


		html_text=(
			f"""<div id="{_ID_SEARCH_USERS}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_button_delete_user(
		lang:str,userid:str,
		as_item:bool=True
	)->str:

	html_text=(
		f"""<input type="hidden" name="{_KEY_USERID}" value="{userid}" >"""
	)

	if as_item:
		html_text=(
			f"{html_text}\n"
			f"""<input type="hidden" name="{_KEY_DELETE_AS_ITEM}" value="true" >"""
		)

	tl={
		_LANG_EN:"Delete user",
		_LANG_ES:"Eliminar usuario"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"""<button type="submit" """
			f"""class="{_CSS_CLASS_COMMON} {_CSS_CLASS_DANGER}">"""
			f"{tl}"
		"</button>"
	)

	tl={
		_LANG_EN:"The user will be permanently deleted. Are you sure?",
		_LANG_ES:"El usuario será eliminado de forma permanente. ¿Está seguro?"
	}[lang]
	html_text=(
		f"""<form hx-delete="{_ROUTE_API_USERS_DELETE}" """
			f"""hx-confirm="{tl}" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-trigger="submit" """
			"""hx-swap="innerHTML">""" "\n"

			f"{html_text}\n"

		"</form>"
	)

	return html_text

def write_html_user_as_item(lang:str,user:Mapping)->str:

	userid=user.get(_KEY_USERID)

	html_text=(
		f"""<div id="{id_user(userid)}" class="{_CSS_CLASS_COMMON}">""" "\n"
			f"{write_html_user(lang,user,full=False)}\n"
			f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
				f"{write_button_delete_user(lang,userid)}\n"
			"</div>\n"
		"</div>"
	)

	return html_text

def write_form_update_config(
		lang:str,
		full:bool=True
	)->str:

	# POST: /api/admin/misc/change-config
	# {
	# 	change-lang:bool,
	# 	lang:str,
	# 	change-port:bool,
	# 	port:int
	# }


	lang_radio_opts=[
		(_LANG_EN,"English"),
		(_LANG_ES,"Español")
	]
	tl={
		_LANG_EN:"Language",
		_LANG_ES:"Idioma"
	}[lang]
	tl_ch=f"change-{_CFG_LANG}"
	html_text=(
		"<!-- LANG CONFIG -->\n"
		"<div>\n"
			f"{write_html_input_checkbox(tl_ch,tl)}\n"
			f"{write_html_input_radio(_CFG_LANG,lang_radio_opts)}"
		"</div>"
	)

	tl={
		_LANG_EN:"Port number",
		_LANG_ES:"Puerto"
	}[lang]
	tl_ch=f"change-{_CFG_PORT}"
	html_text=(
		f"{html_text}\n"

		"<!-- PORT CONFIG -->\n"
		# f"""<div class="{_CSS_CLASS_COMMON}">"""
		"<div>\n"
			f"{write_html_input_checkbox(tl_ch,tl)}\n"
			"<div>\n"
				f"{write_html_input_number(_CFG_PORT,value=_CFG_PORT_MIN,minimum=_CFG_PORT_MIN,maximum=_CFG_PORT_MAX)}\n"
			"</div>\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Apply changes",
		_LANG_ES:"Aplicar cambios"
	}[lang]

	html_text=(
		f"{html_text}\n"

		f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
			f"{write_button_submit(tl)}\n"
		"</div>\n"
	)

	html_text=(
		f"""<form hx-post="{_ROUTE_API_MISC_CHANGE_CONFIG}" """
			f"""hx-target="#{_ID_MSGZONE}" """
			"""hx-trigger="submit" """
			"""hx-swap="innerHTML" """
			">\n"

			f"{html_text}\n"

		"</form>"
	)

	if full:
		tl={
			_LANG_EN:"Server configuration",
			_LANG_ES:"Configuración del servidor"
		}[lang]
		html_text=(
			f"""<div id="{_ID_MISC_SETTINGS}" class="{_CSS_CLASS_COMMON}">""" "\n"
				f"<h3>{tl}</h3>\n"
				f"""<div id="{_ID_MISC_SETTINGS}-inner">""" "\n"
					f"{html_text}\n"
				"</div>\n"
			"</div>"
		)

	return html_text

	# ############################################################

	# html_text=(
	# 	f"""<form hx-post="{_ROUTE_API_MISC_CHANGE_CONFIG}" """
	# 		f"""hx-target="#{_ID_MSGZONE}" """
	# 		"""hx-trigger="submit" """
	# 		"""hx-swap="innerHTML" """
	# 		">\n"
	# )

	# lang_radio_opts=[
	# 	(_LANG_EN,"English"),
	# 	(_LANG_ES,"Español")
	# ]
	# tl={
	# 	_LANG_EN:"Language",
	# 	_LANG_ES:"Idioma"
	# }[lang]
	# tl_ch=f"change-{_CFG_LANG}"
	# html_text=(
	# 	f"{html_text}\n"

	# 	"<!-- LANG CONFIG -->\n"

	# 	# f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
	# 	"<div>\n"
	# 		f"{write_html_input_checkbox(tl_ch,tl)}\n"
	# 		f"{write_html_input_radio(_CFG_LANG,lang_radio_opts)}"
	# 	"</div>"
	# )

	# tl={
	# 	_LANG_EN:"Port number",
	# 	_LANG_ES:"Puerto"
	# }[lang]
	# tl_ch=f"change-{_CFG_PORT}"
	# html_text=(
	# 	f"{html_text}\n"

	# 	"<!-- PORT CONFIG -->\n"

	# 	# f"""<div class="{_CSS_CLASS_COMMON}">"""
	# 	"<div>\n"
	# 		f"{write_html_input_checkbox(tl_ch,tl)}\n"
	# 		"<div>\n"
	# 			f"{write_html_input_number(_CFG_PORT,value=_CFG_PORT_MIN,minimum=_CFG_PORT_MIN,maximum=_CFG_PORT_MAX)}\n"
	# 		"</div>\n"
	# 	"</div>"
	# )

	# tl={
	# 	_LANG_EN:"Apply changes",
	# 	_LANG_ES:"Aplicar cambios"
	# }[lang]

	# html_text=(
	# 		f"{html_text}\n"

	# 		"<!-- APPLY CHANGES -->\n"

	# 		f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
	# 			f"{write_button_submit(tl)}\n"
	# 		"</div>\n"

	# 	"</form>"
	# )

	# if full:
	# 	tl={
	# 		_LANG_EN:"Server configuration",
	# 		_LANG_ES:"Configuración del servidor"
	# 	}[lang]
	# 	html_text=(
	# 		f"""<div id="{_ID_MISC_SETTINGS}" class="{_CSS_CLASS_COMMON}">""" "\n"
	# 			f"<h3>{tl}</h3>\n"
	# 			f"""<div id="admin-config">""" "\n"
	# 				f"{html_text}\n"
	# 			"</div>"
	# 		"</div>"
	# 	)

	# return html_text

def write_button_update_known_asset_names(lang:str)->str:

	tl={
		_LANG_EN:"Update known asset names",
		_LANG_ES:"Actualizar nombres de activos conocidos"
	}[lang]
	html_text=(
		f"""<div id="{_ID_UKANC}" """
			f"""class="{_CSS_CLASS_COMMON}" """
			">\n"
			f"<h3>{tl}</h3>"
	)

	tl={
		_LANG_EN:"Do this only if the asset definitions were modified recently by external means",
		_LANG_ES:"Haga esto solamente si las definiciones de los activos han sido modificadas recientemente usando aplicaciones externas"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"<p>{tl}</p>"
	)

	tl={
		_LANG_EN:"Update",
		_LANG_ES:"Actualizar"
	}[lang]
	return (
			f"{html_text}\n"
			"""<button class="common" """
				f"""hx-post="{_ROUTE_API_MISC_UKANC}" """
				f"""hx-target="#{_ID_MSGZONE}" """
				"""hx-swap="innerHTML" """
				">\n"
				f"{tl}"
			"</button>\n"
		"</div>"
	)

