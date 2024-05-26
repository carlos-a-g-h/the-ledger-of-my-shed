#!/usr/bin/python3.9

# from asyncio import run as aiorun
from pathlib import Path
from typing import Optional

from aiohttp.web import Application
from aiohttp.web import run_app
from aiohttp.web import get as web_GET
from aiohttp.web import post as web_POST
# from aiohttp.web import put as web_PUT
from aiohttp.web import delete as web_DELETE

# from aiohttp.web import Request,Response,json_response

from motor.motor_asyncio import AsyncIOMotorClient

from control_Any import route_src
from control_Any import route_main as route_Home

from control_items import route_main as route_Items
from control_items import route_mixup_get_item as route_Items_mixup_GetItem
from control_items import route_fgmt_new_item as route_Items_fgmt_NewItem
from control_items import route_api_new_item as route_Items_api_NewItem
from control_items import route_fgmt_search_items as route_Items_fgmt_SearchItems
from control_items import route_api_search_items as route_Items_api_SearchItems
from control_items import route_api_drop_item as route_Items_api_DropItem
from control_items import route_api_add_modev as route_Items_api_AddModEv

from control_items_cache import init as init_items_cache

from internals import read_yaml_file
from internals import util_valid_int
from internals import util_valid_str

def read_config(path_config:Path)->dict:

	rawconfig=read_yaml_file(path_config)

	# port

	cfg_port=util_valid_int(
		rawconfig.get("port"),
	)
	if not isinstance(cfg_port,int):
		print(
			"'port' key not found in config"
		)
		return {}

	if not (
		cfg_port>1023 and
		cfg_port<65536
	):
		print(
			"Port must be larger than 1023 and smaller than 65536"
		)
		return {}

	# lang

	cfg_lang=util_valid_str(
		rawconfig.get("lang"),
		True
	)
	if not isinstance(cfg_lang,str):
		print(
			"'lang' key not found in config"
		)
		return {}

	if cfg_lang not in ("en","es"):
		print(
			"Available languages are: 'en' (English) and 'es' (Spanish)"
		)
		return {}

	# db-name

	cfg_db_name=util_valid_str(
		rawconfig.get("db-name"),
		True
	)
	if not isinstance(cfg_db_name,str):
		print(
			"'db-name' key not found in config"
		)
		return {}

	# db-url

	cfg_db_url=util_valid_str(
		rawconfig.get("db-url"),
		True
	)
	if not isinstance(cfg_db_url,str):
		print(
			"'db-url' key not found in config: A local database will be used instead"
		)

	# all ok

	return {
		"db-name":cfg_db_name,
		"db-url":cfg_db_url,
		"port":cfg_port,
		"lang":cfg_lang
	}

def build_app(
		path_programdir:Path,
		lang:str,
		rdb_name:str,
		rdb_url:Optional[str],
	)->Application:

	app=Application()

	app["path_programdir"]=path_programdir
	app["cache_items"]={}
	app["rdbn"]=rdb_name
	app["lang"]=lang

	has_connection_url=isinstance(rdb_name,str)
	if has_connection_url:
		app["rdbc"]=AsyncIOMotorClient()
	if not has_connection_url:
		print("MongoDB Connection string:",rdb_url)
		app["rdbc"]=AsyncIOMotorClient(rdb_url)
	
	app.add_routes([

		web_GET(
			"/src/{srctype}/{filename}",
			route_src
		),

		web_GET(
			"/",
			route_Home
		),

		web_GET(
			"/page/items",
			route_Items
		),

		web_GET(
			"/fgmt/items/new",
			route_Items_fgmt_NewItem
		),
			web_POST(
				"/api/items/new",
				route_Items_api_NewItem
			),

		web_GET(
			"/fgmt/items/search",
			route_Items_fgmt_SearchItems
		),
			web_POST(
				"/api/items/search",
				route_Items_api_SearchItems
			),

		web_GET(
			"/fgmt/items/get/{item_id}",
			route_Items_mixup_GetItem
		),
			web_POST(
				"/api/items/get/{item_id}",
				route_Items_mixup_GetItem
			),
		web_DELETE(
			"/api/items/drop",
			route_Items_api_DropItem
		),

		# web_GET(
		# 	"/page/items/new",
		# 	route_Items_page_NewItem
		# ),

		# web_GET(
		# 	"/page/items/view/{item_id}",
		# 	route_Items_page_ViewItem
		# ),

		# web_POST(
		# 	"/api/items/create",
		# 	route_Items_api_CreateItem
		# ),
		# web_GET(
		# 	"/api/items/select/{item_id}",
		# 	route_Items_api_GetItem
		# ),
		# web_GET(
		# 	"/api/items/search",
		# 	route_Items_api_SearchItems
		# ),
		# web_DELETE(
		# 	"/api/items/delete/{item_id}",
		# 	route_Items_api_DropItem
		# ),

		web_POST(
			"/api/items/history/{item_id}/add",
			route_Items_api_AddModEv
		),
		# web_GET(
		# 	"/api/items/select/{item_id}/modev-view/{modev_date}/{modev_uid}",
		# 	route_Items_api_GetModEv
		# ),
		# web_DELETE(
		# 	"/api/items/select/{item_id}/modev-drop",
		# 	route_Items_api_DropModEv
		# )

	])

	app.on_startup.append(init_items_cache)

	return app

if __name__=="__main__":

	from sys import argv as sys_argv
	from sys import exit as sys_exit

	path_appdir=Path(sys_argv[0]).parent

	the_config=read_config(
		path_appdir.joinpath(
				"config.yaml"
			)
		)

	cfg_port=the_config.get("port")
	if not isinstance(cfg_port,int):
		sys_exit(1)
		
	cfg_lang=the_config.get("lang")
	if not isinstance(cfg_lang,str):
		sys_exit(1)

	cfg_db_name=the_config.get("db-name")
	if not isinstance(cfg_db_name,str):
		sys_exit(1)

	cfg_db_url=the_config.get("db-url")

	run_app(
		build_app(
			path_appdir,
			cfg_lang,
			cfg_db_name,
			cfg_db_url
		),
		port=cfg_port,
	)
