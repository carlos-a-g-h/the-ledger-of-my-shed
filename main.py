#!/usr/bin/python3.9

from pathlib import Path
from typing import Optional

from aiohttp.web import Application
from aiohttp.web import run_app
from aiohttp.web import get as web_GET
from aiohttp.web import post as web_POST
from aiohttp.web import delete as web_DELETE

# from aiohttp.web import Request,Response,json_response

from motor.motor_asyncio import AsyncIOMotorClient

from symbols_Any import _APP_LANG,_LANG_EN,_LANG_ES
# from symbols_Any import _TYPE_CUSTOM
from symbols_Any import _APP_CACHE_ASSETS,_APP_PROGRAMDIR,_APP_RDBC,_APP_RDBN
from symbols_Any import _CFG_PORT,_CFG_LANG,_CFG_DB_NAME,_CFG_DB_URL

# from control_Any import get_client_type
from control_Any import the_middleware_factory
from control_Any import route_src
from control_Any import route_main as route_Home

from control_account import _ROUTE_PAGE as _ROUTE_PAGE_ACCOUNT
from control_account import route_main as route_Account
from control_account import route_api_login as route_Account_api_Login
from control_account import route_api_login_otp as route_Account_api_LoginOTP
from control_account import route_api_logout as route_Account_api_Logout

from control_admin import _ROUTE_PAGE as _ROUTE_PAGE_ADMIN
from control_admin import route_main as route_Admin
from control_admin import route_api_update_config as route_Admin_api_UpdateConfig
from control_admin import route_api_update_known_asset_names as route_Admin_api_UpdateKnownAssetNames

from control_assets import _ROUTE_PAGE as _ROUTE_PAGE_ASSETS
from control_assets import route_main as route_Assets
from control_assets import route_api_select_asset as route_Assets_api_GetAsset
from control_assets import route_fgmt_asset_panel as route_Assets_fgmt_AssetPanel
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

from dbi_account import init_sessions_database

from internals import read_yaml_file
from internals import util_valid_int
from internals import util_valid_int_inrange
from internals import util_valid_str

def read_config(path_config:Path)->dict:

	print(
		"Config File:\n"
		f"\t{path_config.absolute()}"
	)

	rawconfig=read_yaml_file(path_config)

	# port

	cfg_port=util_valid_int_inrange(
		util_valid_int(
			rawconfig.get(_CFG_PORT),
		),
		minimum=1024,
		maximum=65536
	)
	if not isinstance(cfg_port,int):
		print(
			f"'{_CFG_PORT}' key not found in config "
			"or not in the range 1024 < x < 65536"
		)
		return {}

	# lang

	cfg_lang=util_valid_str(
		rawconfig.get(_CFG_LANG),
		True
	)
	if not isinstance(cfg_lang,str):
		print(
			f"'{_CFG_LANG}' key not found in config"
		)
		return {}

	if cfg_lang not in (_LANG_EN,_LANG_ES):
		print(
			"Language unsupported or not found in config file, defaulting to English" "\n"
			"Available languages are: 'en' (English) and 'es' (Spanish)"
		)
		cfg_lang=_LANG_EN

	# db-name

	cfg_db_name=util_valid_str(
		rawconfig.get(_CFG_DB_NAME),
		True
	)
	if not isinstance(cfg_db_name,str):
		print(
			f"'{_CFG_DB_NAME}' key not found in config"
		)
		return {}

	# db-url

	cfg_db_url=util_valid_str(
		rawconfig.get(_CFG_DB_URL),
		True
	)
	if not isinstance(cfg_db_url,str):
		print(
			f"'{_CFG_DB_URL}' key not found in config: A local database will be used instead"
		)

	# all ok

	return {
		_CFG_DB_NAME:cfg_db_name,
		_CFG_DB_URL:cfg_db_url,
		_CFG_PORT:cfg_port,
		_CFG_LANG:cfg_lang
	}

# def print_request_info(request:Request):
# 	user_agent=request.headers.get("User-Agent")
# 	print(
# 		"\n" f"- Recieved: {request.method}:{request.url}" "\n"
# 		"\t" f"Client: {request.remote} {user_agent}" "\n"
# 		"\t" f"Cookies: {request.cookies}"
# 	)

def build_app(
		path_programdir:Path,
		lang:str,
		rdb_name:str,
		rdb_url:Optional[str],
	)->Application:

	msg_err:Optional[str]=init_sessions_database(path_programdir)
	if msg_err is not None:
		raise Exception(msg_err)

	app=Application(
		middlewares=[the_middleware_factory]
	)

	app[_APP_PROGRAMDIR]=path_programdir
	app[_APP_CACHE_ASSETS]={}
	app[_APP_LANG]=lang

	app[_APP_RDBN]=rdb_name

	has_connection_url=isinstance(rdb_name,str)
	if has_connection_url:
		print("Connecting to a local MongoDB database")
		app[_APP_RDBC]=AsyncIOMotorClient()

	if not has_connection_url:
		print(
			"Connecting to a remote MongoDB database:",
			rdb_url
		)
		app[_APP_RDBC]=AsyncIOMotorClient(rdb_url)

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

		# ACCOUNT

		web_GET(
			_ROUTE_PAGE_ACCOUNT,
			route_Account,
		),
			web_POST(
				"/api/account/login",
				route_Account_api_Login
			),
			web_POST(
				"/api/account/login-otp",
				route_Account_api_LoginOTP
			),
			web_DELETE(
				"/api/account/logout",
				route_Account_api_Logout
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
				"/fgmt/assets/panel/{asset_id}",
				route_Assets_fgmt_AssetPanel
		
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
