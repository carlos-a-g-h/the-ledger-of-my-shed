#!/usr/bin/python3.9

# from asyncio import run as aiorun
from pathlib import Path
from typing import Optional

from aiohttp.web import Application
from aiohttp.web import run_app
from aiohttp.web import get as web_GET
from aiohttp.web import post as web_POST
from aiohttp.web import delete as web_DELETE

from aiohttp.web import Request,Response,json_response

from motor.motor_asyncio import AsyncIOMotorClient

from control_Any import _TYPE_CUSTOM
from control_Any import get_client_type
from control_Any import route_src
from control_Any import route_main as route_Home

from control_admin import _ROUTE_PAGE as _ROUTE_PAGE_ADMIN
from control_admin import route_main as route_Admin
from control_admin import route_api_update_config as route_Admin_api_UpdateConfig
from control_admin import route_api_update_known_asset_names as route_Admin_api_UpdateKnownAssetNames

from control_assets import _CACHE_ASSETS
from control_assets import _ROUTE_PAGE as _ROUTE_PAGE_ASSETS
from control_assets import route_main as route_Assets
from control_assets import route_api_select_asset as route_Assets_api_GetAsset
from control_assets import route_fgmt_asset_editor as route_Assets_fgmt_EditAsset
from control_assets import route_fgmt_new_asset as route_Assets_fgmt_NewAsset
from control_assets import route_api_new_asset as route_Assets_api_NewAsset
from control_assets import route_api_asset_metadata_change as route_Assets_api_ChangeMetadata
from control_assets import route_fgmt_search_assets as route_Assets_fgmt_SearchAssets
from control_assets import route_api_search_assets as route_Assets_api_SearchAssets
from control_assets import route_api_drop_asset as route_Assets_api_DropAsset
from control_assets import route_api_add_record as route_Assets_api_AddRecord
from control_assets import route_api_get_record as route_Assets_api_GetRecord
from control_assets import util_update_known_assets as init_assets_cache

from control_orders import _ROUTE_PAGE as _ROUTE_PAGE_ORDERS
from control_orders import route_main as route_Orders
from control_orders import route_fgmt_new_order as route_Orders_fgmt_NewOrder
from control_orders import route_fgmt_list_orders as route_Orders_fgmt_ListOrders
from control_orders import route_fgmt_order_editor as route_Order_fgmt_Editor
from control_orders import route_api_new_order as route_Orders_api_NewOrder
from control_orders import route_api_delete_order as route_Orders_api_DeleteOrder
from control_orders import route_api_update_asset_in_order as route_Orders_api_UpdateAsset
from control_orders import route_api_remove_asset_from_order as route_Orders_api_RemoveAsset
from control_orders import route_api_run_order as route_Orders_api_RunOrder

from internals import read_yaml_file
from internals import util_valid_int
from internals import util_valid_int_inrange
from internals import util_valid_str

def read_config(path_config:Path)->dict:

	print(
		"CFG File:\n"
		f"\t{path_config.absolute()}\n"
	)

	rawconfig=read_yaml_file(path_config)

	# port

	cfg_port=util_valid_int_inrange(
		util_valid_int(
			rawconfig.get("port"),
		),
		minimum=1024,
		maximum=65536
	)
	if not isinstance(cfg_port,int):
		print(
			"'port' key not found in config or not in the range 1024 < x < 65536"
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
			"Language unsupported or not found in config file, defaulting to English" "\n"
			"Available languages are: 'en' (English) and 'es' (Spanish)"
		)
		cfg_lang="en"

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

async def mware_factory(app,handler):

	async def mware_handler(request:Request):

		# Local source files

		if request.path.startswith("/src/"):
			return (
				await handler(request)
			)

		ct=get_client_type(request)
		if not isinstance(ct,str):
			return Response(status=406)

		if ct==_TYPE_CUSTOM:

			if (
				request.path=="/" or
				request.path.startswith("/page/") or
				request.path.startswith("/fgmt/")
			):
				return json_response(data={})

		return (
			await handler(request)
		)

	return mware_handler

def build_app(
		path_programdir:Path,
		lang:str,
		rdb_name:str,
		rdb_url:Optional[str],
	)->Application:

	app=Application(
		middlewares=[mware_factory]
	)

	app["path_programdir"]=path_programdir
	app[_CACHE_ASSETS]={}
	app["rdbn"]=rdb_name
	app["lang"]=lang

	has_connection_url=isinstance(rdb_name,str)
	if has_connection_url:
		print("Connecting to a local MongoDB database")
		app["rdbc"]=AsyncIOMotorClient()

	if not has_connection_url:
		print(
			"Connecting to a remote MongoDB database:",
			rdb_url
		)
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

		# ADMIN

		web_GET(
			_ROUTE_PAGE_ADMIN,
			route_Admin
		),
			web_POST(
				"/api/admin/update-config",
				route_Admin_api_UpdateConfig
			),
			web_POST(
				"/api/admin/update-known-assets",
				route_Admin_api_UpdateKnownAssetNames
			),

		# ASSETS

		web_GET(
			_ROUTE_PAGE_ASSETS,
			route_Assets
		),

			web_GET(
				"/fgmt/assets/new",
				route_Assets_fgmt_NewAsset
			),
				web_POST(
					"/api/assets/new",
					route_Assets_api_NewAsset
				),

			web_GET(
				"/fgmt/assets/search-assets",
				route_Assets_fgmt_SearchAssets
			),
				web_POST(
					"/api/assets/search-assets",
					route_Assets_api_SearchAssets
				),

			web_GET(
				"/fgmt/assets/editor/{asset_id}",
				route_Assets_fgmt_EditAsset
			),
				web_POST(
					"/api/assets/select/{asset_id}",
					route_Assets_api_GetAsset
				),
				web_POST(
					"/api/assets/change-metadata",
					route_Assets_api_ChangeMetadata
				),

			web_DELETE(
				"/api/assets/drop",
				route_Assets_api_DropAsset
			),

			web_POST(
				"/api/assets/history/{asset_id}/add",
				route_Assets_api_AddRecord
			),
				web_GET(
					"/api/assets/history/{asset_id}/records/{record_uid}",
					route_Assets_api_GetRecord
				),


		# ORDERS

		web_GET(
			# "/page/orders",
			_ROUTE_PAGE_ORDERS,
			route_Orders
		),
			web_GET(
				"/fgmt/orders/new",
				route_Orders_fgmt_NewOrder
			),
				web_POST(
					"/api/orders/new",
					route_Orders_api_NewOrder
				),

			web_GET(
				"/fgmt/orders/current",
				route_Orders_fgmt_ListOrders
			),

			web_GET(
				"/fgmt/orders/current/{order_id}/search-assets",
				route_Assets_fgmt_SearchAssets
			),
				web_POST(
					"/api/orders/current/{order_id}/search-assets",
					route_Assets_api_SearchAssets
				),

			web_GET(
				"/fgmt/orders/current/{order_id}/editor",
				route_Order_fgmt_Editor
			),
			web_POST(
				"/api/orders/current/{order_id}/update",
				route_Orders_api_UpdateAsset
			),
			web_DELETE(
				"/api/orders/current/{order_id}/update",
				route_Orders_api_RemoveAsset
			),
			web_POST(
				"/api/orders/current/{order_id}/run",
				route_Orders_api_RunOrder
			),
			web_DELETE(
				"/api/orders/current/{order_id}/drop",
				route_Orders_api_DeleteOrder
			),
			web_DELETE(
				"/api/orders/current/{order_id}/drop-fol",
				route_Orders_api_DeleteOrder
			),

		# web_GET(
		# 	"/page/assets/new",
		# 	route_Assets_page_NewAsset
		# ),

		# web_GET(
		# 	"/page/assets/view/{asset_id}",
		# 	route_Assets_page_ViewAsset
		# ),

		# web_POST(
		# 	"/api/assets/create",
		# 	route_Assets_api_CreateAsset
		# ),
		# web_GET(
		# 	"/api/assets/select/{asset_id}",
		# 	route_Assets_api_GetAsset
		# ),
		# web_GET(
		# 	"/api/assets/search",
		# 	route_Assets_api_SearchAssets
		# ),
		# web_DELETE(
		# 	"/api/assets/delete/{asset_id}",
		# 	route_Assets_api_DropAsset
		# ),

		# web_GET(
		# 	"/api/assets/select/{asset_id}/modev-view/{modev_date}/{modev_uid}",
		# 	route_Assets_api_GetRecord
		# ),
		# web_DELETE(
		# 	"/api/assets/select/{asset_id}/modev-drop",
		# 	route_Assets_api_DropRecord
		# )

	])

	app.on_startup.append(init_assets_cache)
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
