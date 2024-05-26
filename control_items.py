#!/usr/bin/python3.9

# from pathlib import Path
from secrets import token_hex
from typing import Mapping
from typing import Union
from typing import Optional

# from aiohttp.web import Application
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp.web import json_response

# from motor.motor_asyncio import AsyncIOMotorClient

from control_Any import _MIMETYPE_HTML
from control_Any import _SCRIPT_HTMX
from control_Any import _STYLE_CUSTOM
from control_Any import _STYLE_POPUP
from control_Any import _TYPE_CUSTOM
from control_Any import get_lang
from control_Any import get_client_type
from control_Any import get_request_body_dict
from control_Any import response_errormsg

from control_items_cache import _CACHE_ITEMS
from control_items_cache import util_items_cache_name_lookup

from dbi import dbi_inv_CreateItem
from dbi import dbi_inv_ItemQuery
# from dbi import dbi_inv_GetItem
from dbi import dbi_inv_DropItem
from dbi import dbi_inv_ModEv_Add

from frontend_Any import _LANG_EN
from frontend_Any import _LANG_ES
from frontend_Any import write_fullpage
from frontend_Any import write_popupmsg
from frontend_Any import write_ul

from frontend_items import write_button_new_item
from frontend_items import write_button_search_items
from frontend_items import write_form_new_item
from frontend_items import write_form_search_items
from frontend_items import write_form_add_modev
from frontend_items import write_html_modev
from frontend_items import write_html_item
from frontend_items import write_html_list_of_items

from internals import util_valid_bool
from internals import util_valid_int
from internals import util_valid_str
# from internals import util_rnow

_ERR_TITLE_MODEV_MOD={
	_LANG_EN:"History modification error",
	_LANG_ES:"Error al modificar el historial"
}

_ERR_TITLE_SEARCH_ITEMS={
	_LANG_EN:"Item(s) search error",
	_LANG_ES:"Error de búsqueda de objeto(s)"
}

_ERR_TITLE_NEW_ITEM={
	_LANG_EN:"Item creation error",
	_LANG_ES:"Error al crear el objeto"
}
_ERR_TITLE_GET_ITEM={
	_LANG_EN:"Item request error",
	_LANG_ES:"Error de petición de objeto"
}
_ERR_TITLE_DROP_ITEM={
	_LANG_EN:"Item deletion error",
	_LANG_ES:"Error de eliminación de objeto"
}

_ERR_DETAIL_DATA_NOT_VALID={
	_LANG_EN:"The data from the request body is not valid",
	_LANG_ES:"Los datos recogidos del cuerpo de la petición no son válidos"
}
_ERR_DETAIL_DBI_FAIL={
	_LANG_EN:"The operation failed or returned a negative result",
	_LANG_ES:"La operación falló o devolvió un resultado negativo"
}

# async def util_build_items_cache(
# 		rdbc:AsyncIOMotorClient,
# 		rdbn:str
# 	)->Mapping:

# 	results=await dbi_inv_ItemList(rdbc,rdbn)

# 	if len(results)==0:
# 		return {}

# 	items_cache={}

# 	for item in results:
# 		item_id=





# 	return items

# async def util_update_items_cache(app:Application):
	

async def route_fgmt_new_item(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

	return Response(
		body=(
			f"{write_form_new_item(lang)}"
			"""<section hx-swap-oob="innerHTML:#navigation">"""
				f"{write_ul([write_button_search_items(lang)])}"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_search_items(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

	return Response(
		body=(
			f"{write_form_search_items(lang)}"
			"""<section hx-swap-oob="innerHTML:#navigation">"""
				f"{write_ul([write_button_new_item(lang)])}"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_new_item(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_NEW_ITEM[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	item_name=util_valid_str(
		request_data.get("name")
	)
	if not isinstance(item_name,str):
		return response_errormsg(
			_ERR_TITLE_NEW_ITEM[lang],
			{
				_LANG_EN:"Check the 'name' field",
				_LANG_ES:"Revise el campo 'name' (el nombre)"
			}[lang],
			ct,status_code=406
		)

	ematch=util_items_cache_name_lookup(
		request.app,item_name,True
	)
	if len(ematch)>0:

		ematch_id=ematch["id"]

		tl={
			_LANG_EN:"An item with the same name already exists",
			_LANG_ES:"Un objeto con el mismo nombre ya existe"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_NEW_ITEM[lang],
			f"{tl}: id={ematch_id}",
			ct,status_code=406
		)

	item_sign=util_valid_str(
		request_data.get("sign")
	)
	if not isinstance(item_sign,str):
		return response_errormsg(
			_ERR_TITLE_NEW_ITEM[lang],
			{
				_LANG_EN:"Check the 'sign' field",
				_LANG_ES:"Revise el campo 'sign' (la firma)"
			}[lang],
			ct,status_code=406
		)

	item_comment=util_valid_str(
		request_data.get("comment")
	)

	item_tag=util_valid_str(
		request_data.get("tag")
	)

	item_id=util_valid_str(
		request_data.get("id"),
		lowerit=True
	)
	if not isinstance(item_id,str):
		item_id=token_hex(8)

	get_copy=True
	if ct==_TYPE_CUSTOM:
		# TODO: get get_copy from json body
		get_copy=True

	result=await dbi_inv_CreateItem(
		request.app["rdbc"],
		request.app["rdbn"],
		item_id,item_name,
		item_sign,item_tag=item_tag,
		item_comment=item_comment,
		rcopy=get_copy
	)

	ok=False
	if isinstance(result,bool):
		ok=result

	ismapping=isinstance(result,Mapping)
	if ismapping:
		ok=(len(result)>0)

	if not ok:
		return response_errormsg(
			_ERR_TITLE_NEW_ITEM[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct,400
		)

	# request.app["items_cache"].update({item_id:item_name})

	if ct==_TYPE_CUSTOM:
		return json_response(
			data={
				True:result,
				False:{},
			}[ismapping]
		)

	request.app[_CACHE_ITEMS].update({
		item_id:item_name
	})

	lang=request.app["lang"]

	html_popup=write_popupmsg(
		"<h2>"+{
			_LANG_EN:"Item created",
			_LANG_ES:"Objeto creado"
		}[lang]+"</h2>"
	)

	tl={
		_LANG_EN:"Latest item",
		_LANG_ES:"Objeto más reciente"
	}[lang]

	return Response(
		body=(
			f"{html_popup}"

			"""<section hx-swap-oob="innerHTML:#navigation">"""
				f"{write_ul([write_button_search_items(lang)])}"
			"</section>"

			"""<section hx-swap-oob="innerHTML:#main">"""
				f"{write_form_new_item(lang)}"
				f"<p>{tl}:</p>"
				f"{write_html_item(lang,result)}"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_mixup_get_item(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	# print(
	# 	"\n",
	# 	"\n>",request.method,
	# 	"\n>",request.url.path,
	# 	"\n>",request.headers
	# )

	if ct==_TYPE_CUSTOM:

		if not (
			request.method=="POST" and
			request.url.path.startswith("/api/")
		):
			return Response(status=406)

	if not ct==_TYPE_CUSTOM:

		if not (
			request.method=="GET" and
			request.url.path.startswith("/fgmt/")
		):
			return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

	item_id=util_valid_str(
		request.match_info["item_id"]
	)
	if not isinstance(item_id,str):
		return response_errormsg(
			_ERR_TITLE_GET_ITEM[lang],
			{
				_LANG_EN:"Item Id not valid",
				_LANG_ES:"Id de objeto no válido"
			}[lang],
			ct,status_code=406
		)

	inc_history=True
	inc_total=True
	inc_comment=True

	if ct==_TYPE_CUSTOM:

		request_data=await get_request_body_dict(ct,request)
		# if not request_data:
		if not isinstance(request_data,Mapping):
			return response_errormsg(
				_ERR_TITLE_GET_ITEM[lang],
				_ERR_DETAIL_DATA_NOT_VALID[lang],
				ct,status_code=406
			)

		inc_history=util_valid_bool(
			request_data.get("get_history"),
			False
		)
		inc_total=util_valid_bool(
			request_data.get("get_total"),
			False
		)
		inc_comment=util_valid_bool(
			request_data.get("get_comment"),
			False
		)

	dbi_results=await dbi_inv_ItemQuery(
		request.app["rdbc"],request.app["rdbn"],
		item_id=item_id,
		get_comment=inc_comment,
		get_total=inc_total,
		get_history=inc_history
	)
	if not len(dbi_results)==1:
		return response_errormsg(
			_ERR_TITLE_GET_ITEM[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]} (1)",
			ct,status_code=400
		)

	the_item=dbi_results.pop()
	if len(the_item)==0:
		return response_errormsg(
			_ERR_TITLE_GET_ITEM[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]} (2)",
			ct,status_code=400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(
			data=the_item
		)

	lang=request.app["lang"]

	tl={
		_LANG_EN:"Item info",
		_LANG_ES:"Información del objeto"
	}[lang]

	return Response(
		body=(
			f"<!-- Selected the item: {item_id} -->\n"

			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				"<!-- GET OK !-->\n"
				f"{write_ul([write_button_search_items(lang),write_button_new_item(lang)])}\n"
			"</section>"

			"""<section hx-swap-oob="innerHTML:#main">""" "\n"
				"<!-- GET OK !!!!!-->\n"
				f"<h3>{tl}</h3>\n"
				f"{write_html_item(lang,the_item,True)}\n"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_search_items(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_SEARCH_ITEMS[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	search_name=util_valid_str(
		request_data.get("name")
	)
	search_sign=util_valid_str(
		request_data.get("sign")
	)
	search_tag=util_valid_str(
		request_data.get("tag")
	)
	# get_history=util_valid_bool(
	# 	request_data.get("get_history")
	# )
	# get_total=util_valid_bool(
	# 	request_data.get("get_total")
	# )
	# get_comment=util_valid_bool(
	# 	request_data.get("get_comment")
	# )

	exact_name_match:Optional[Mapping]=None
	search_results=[]
	if_id_list=[]
	buffer=[]

	print(request.app[_CACHE_ITEMS])

	if isinstance(search_name,str):
		buffer.extend(
			util_items_cache_name_lookup(
				request.app,search_name
			)
		)
		# print("BUFFER:",buffer)
		x=len(buffer)
		while True:
			x=x-1
			if x<0:
				break

			if_id=buffer[x]["id"]
			if_exact=buffer[x]["exact"]
			if if_id in if_id_list:
				buffer.pop()
				continue

			if_id_list.append(if_id)
			if (
				if_exact and
				(not isinstance(exact_name_match,str))
			):
				exact_name_match=buffer.pop()
				continue

			search_results.append(
				buffer.pop()
			)

	get_all=(
		(not isinstance(search_sign,str)) and
		(not isinstance(search_tag,str)) and
		(not isinstance(search_name,str))
	)

	if get_all or isinstance(search_sign,str) or isinstance(search_tag,str):
		buffer.extend(
			await dbi_inv_ItemQuery(
				request.app["rdbc"],
				request.app["rdbn"],
				item_tag=search_tag,
				item_sign=search_sign,
				get_total=True,
			)
		)
		x=len(buffer)
		while True:
			x=x-1
			if x<0:
				break

			if_id=buffer[x]["id"]
			if if_id in if_id_list:
				buffer.pop()
				continue

			if_id_list.append(if_id)
			search_results.append(
				buffer.pop()
			)

	if exact_name_match is not None:
		search_results.append(
			exact_name_match
		)

	if len(search_results)==0:
		return response_errormsg(
			_ERR_TITLE_SEARCH_ITEMS[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct,400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(
			data={"items":search_results}
		)

	html_text_params=""
	params_used=(
		isinstance(search_sign,str) or
		isinstance(search_tag,str) or
		isinstance(search_name,str)
	)
	if params_used:
		tl={
			_LANG_EN:"Parameters used",
			_LANG_ES:"Parámetros usados"
		}[lang]
		html_text_params=f"<h3>{tl}</h3>"
		if isinstance(search_name,str):
			html_text_params=(
				f"{html_text_params}\n"
				f"<p>Name: <code>{search_name}</code></p>"
			)
		if isinstance(search_sign,str):
			html_text_params=(
				f"{html_text_params}\n"
				f"<p>Sign: <code>{search_sign}</code></p>"
			)
		if isinstance(search_tag,str):
			html_text_params=(
				f"{html_text_params}\n"
				f"<p>Tag: <code>{search_tag}</code></p>"
			)

	lang=request.app["lang"]

	tl={
		_LANG_EN:"Item(s) found",
		_LANG_ES:"Objeto(s) encontrado(s)"
	}[lang]

	return Response(
		body=(
			f"<!-- sign: {search_sign} ; tag: {search_tag}-->\n"

			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				f"{write_ul([write_button_new_item(lang)])}\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main">""" "\n"
				f"{write_form_search_items(lang)}\n"
				f"{html_text_params}\n"
				f"<h3>{tl}:</h3>\n"
				f"{write_html_list_of_items(lang,search_results,True)}\n"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_drop_item(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

	request_data=await get_request_body_dict(ct,request)
	print("DELETE",request_data)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_DROP_ITEM[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	item_id=util_valid_str(
		request_data.get("id")
	)
	if not isinstance(item_id,str):
		return response_errormsg(
			_ERR_TITLE_DROP_ITEM[lang],
			{
				_LANG_EN:"Check the 'id' field",
				_LANG_ES:"Revisa el campo 'id'"
			}[lang],
			ct,status_code=406
		)

	recover_item=False
	if ct==_TYPE_CUSTOM:
		recover_item=util_valid_bool(
			request_data.get("recover"),
			dval=False
		)

	dbi_result=await dbi_inv_DropItem(
		request.app["rdbc"],request.app["rdbn"],
		item_id,rcopy=recover_item
	)

	ok=False
	if isinstance(dbi_result,bool):
		ok=dbi_result
	is_mapping=isinstance(dbi_result,Mapping)
	if is_mapping:
		ok=len(dbi_result)>0

	if not ok:
		return response_errormsg(
			_ERR_TITLE_DROP_ITEM[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct,status_code=406
		)

	if ct==_TYPE_CUSTOM:
		if not is_mapping:
			return {}

		return dbi_result

	html_popup=write_popupmsg(
		"<h2>"+{
			_LANG_EN:"Item deleted",
			_LANG_ES:"Objeto eliminado"
		}[lang]+"</h2>"
	)

	return Response(
		body=(
			f"{html_popup}\n"

			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				f"{write_ul([write_button_search_items(lang),write_button_new_item(lang)])}\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main">""" "\n"
				f"<!-- Recently deleted: {item_id} -->"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_add_modev(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_NEW_ITEM[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	item_id=util_valid_str(
		request.match_info["item_id"]
	)
	if not isinstance(item_id,str):
		return response_errormsg(
			_ERR_TITLE_MODEV_MOD[lang],
			{
				_LANG_EN:"Item Id not valid",
				_LANG_ES:"Id de objeto no válido"
			}[lang],
			ct,status_code=406
		)

	the_sign=util_valid_str(
		request_data.get("sign")
	)
	if not isinstance(the_sign,str):
		return response_errormsg(
			_ERR_TITLE_MODEV_MOD[lang],
			{
				_LANG_EN:"Check the 'sign' field",
				_LANG_ES:"Revisa el campo 'sign' (firma)"
			}[lang],
			ct,status_code=406
		)

	the_mod=util_valid_int(
		request_data.get("mod"),
		fallback=0
	)
	if the_mod==0:
		return response_errormsg(
			_ERR_TITLE_MODEV_MOD[lang],
			{
				_LANG_EN:(
					"Check the 'mod' field (increase/decrease). "
					"Make sure it is different than zero"
				),
				_LANG_ES:(
					"Revisa el campo 'mod' (agregar/sustraer). "
					"Asegúrese de que no sea igual a cero"
				)
			}[lang],
			ct,status_code=406
		)

	the_tag=util_valid_str(
		request_data.get("tag")
	)
	the_comment=util_valid_str(
		request_data.get("comment")
	)

	dbi_result=await dbi_inv_ModEv_Add(
		request.app["rdbc"],
		request.app["rdbn"],
		item_id,
		the_sign,the_mod,
		modev_tag=the_tag,
		modev_comment=the_comment
	)
	if dbi_result is None:
		return response_errormsg(
			_ERR_TITLE_MODEV_MOD[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct,status_code=400
		)

	modev_uid,modev_date=dbi_result

	if ct==_TYPE_CUSTOM:
		return json_response(
			data={
				"uid":modev_uid,
				"date":modev_date
			}
		)


	html_text="<h2>"+{
		_LANG_EN:"Added the requested modification",
		_LANG_ES:"Se realizó la modificación"
	}[lang]+"</h2>\n"


	html_modev=write_html_modev(
		lang,
		{
			"uid":modev_uid,
			"date":modev_date,
			"mod":the_mod,
			"tag":the_tag,
			"sign":the_sign,
			"comment":the_comment,
		}
	)

	# html_text=(
	# 	f"{html_text}\n"
	# 	f"{html_modev}"
	# )

	return Response(
		body=(

			f"{write_popupmsg(html_text)}\n"

			f"""<code hx-swap-oob="innerHTML:#item-{item_id}-total">???</code>""" "\n"

			f"""<div hx-swap-oob="innerHTML:#item-{item_id}-history-ctl">""" "\n"
				f"{write_form_add_modev(lang,item_id)}\n"
			"</div>"

			f"""<div hx-swap-oob="afterbegin:#item-{item_id}-history">""" "\n"
				f"{html_modev}\n"
			"</div>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_main(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

	tl1={
		_LANG_EN:"Basic item manager",
		_LANG_ES:"Gestor básico de objetos"
	}[lang]

	tl2={
		_LANG_EN:"Simple creation and management of items",
		_LANG_ES:"Creación y gestión simple e individual de objetos"
	}[lang]

	tl3={
		_LANG_EN:"Back to main page",
		_LANG_ES:"Voler a la página principal"
	}[lang]

	return Response(
		body=write_fullpage(
			lang,
			tl1,
			(
				f"<h1>{tl1}</h1>\n"
				f"<p>{tl2}</p>\n"
				f"""<p><a href="/">{tl3}</a></p>\n"""
				"""<section id="navigation">""" "\n"
					f"{write_ul([write_button_search_items(lang),write_button_new_item(lang)])}\n"
				"</section>\n"
				"""<section id="main">""" "\n"
					"<!-- FRAGMENTS GO HERE -->\n"
				"</section>\n"
				"""<section id="messages">""" "\n"
					"<!-- MESSAGES GO HERE -->\n"
				"</section>"
			),
			html_header_extra=[
				_SCRIPT_HTMX,
				_STYLE_POPUP,
				_STYLE_CUSTOM
			]
		),
		content_type=_MIMETYPE_HTML
	)
