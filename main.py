#!/usr/bin/python3.9

from pathlib import Path
from typing import Optional
from secrets import token_hex

from aiohttp.web import (
	Application,
	run_app,
	get as web_GET,
	post as web_POST,
	delete as web_DELETE,
)

from motor.motor_asyncio import AsyncIOMotorClient

from control_Any import (
	the_middleware_factory,
	route_src,
	route_main as route_Home
)

from control_accounts import (
	_ROUTE_PAGE as _ROUTE_PAGE_ACCOUNTS,
	route_main as route_Accounts,
	route_fgmt_login as route_Accounts_fgmt_Login,
	route_api_login as route_Accounts_api_Login,
	route_api_login_otp as route_Accounts_api_LoginOTP,
	route_api_login_magical as route_Accounts_api_LoginMagical,
	route_api_logout as route_Accounts_api_Logout,
)

from control_admin import (
	_ROUTE_PAGE as _ROUTE_PAGE_ADMIN,
	route_main as route_Admin,
	route_api_change_config as route_Admin_api_ChangeConfig,
	route_api_update_known_asset_names as route_Admin_api_UpdateKnownAssetNames,
	route_fgmt_section_users as route_Admin_fgmt_UsersConfig,
	route_fgmt_section_misc as route_Admin_fgmt_MiscConfig
)

from control_assets import (
	route_main as route_Assets,
	route_api_select_asset as route_Assets_api_GetAsset,
	route_fgmt_asset_panel as route_Assets_fgmt_AssetPanel,
	route_fgmt_new_asset as route_Assets_fgmt_NewAsset,
	route_api_new_asset as route_Assets_api_NewAsset,
	route_api_asset_change_metadata as route_Assets_api_ChangeMetadata,
	route_fgmt_search_assets as route_Assets_fgmt_SearchAssets,
	route_api_drop_asset as route_Assets_api_DropAsset,
	route_api_add_record as route_Assets_api_AddRecord,
	route_api_get_record as route_Assets_api_GetRecord,
	util_update_known_assets as init_assets_cache
)

from control_assets_search import route_api_search_assets as route_Assets_api_SearchAssets

from control_orders import (
	route_main as route_Orders,
	route_fgmt_new_order as route_Orders_fgmt_NewOrder,
	route_fgmt_list_orders as route_Orders_fgmt_ListOrders,
	route_fgmt_order_details as route_Order_fgmt_Details,
	route_api_new_order as route_Orders_api_NewOrder,
	route_api_delete_order as route_Orders_api_DeleteOrder,
	route_api_update_asset_in_order as route_Orders_api_UpdateAsset,
	route_api_remove_asset_from_order as route_Orders_api_RemoveAsset,
	route_api_run_order as route_Orders_api_RunOrder
)

from dbi_accounts import (
	ldbi_init_sessions,
	ldbi_init_users,
	# ldbi_save_user,
)

from internals import (
	read_yaml_file,
	util_valid_int,
	util_valid_int_inrange,
	util_valid_str,
	util_valid_list,
)

from symbols_assets import _ROUTE_PAGE as _ROUTE_PAGE_ASSETS

from symbols_orders import _ROUTE_PAGE as _ROUTE_PAGE_ORDERS

from symbols_Any import (

	# _ROOT_USER,

	_APP_LANG,_LANG_EN,_LANG_ES,

	_APP_CACHE_ASSETS,_APP_PROGRAMDIR,_APP_ROOT_USERID,
	_APP_RDBC,_APP_RDBN,

	_CFG_PORT,_CFG_LANG,_CFG_DB_NAME,_CFG_DB_URL,_CFG_FLAGS,

	# _CFG_FLAG_ROOT_LOCAL_AUTOLOGIN,
	# _CFG_FLAG_PUB_READ_ACCESS_TO_HISTORY,
	# _CFG_FLAG_PUB_READ_ACCESS_TO_ORDERS,
	# _CFG_FLAG_PVT_READ_ACCESS_TO_ASSETS,

	_CFG_PORT_MIN,_CFG_PORT_MAX
)

def read_config(path_config:Path)->dict:

	print(
		"Config File:\n"
		f"\t{path_config.absolute()}"
	)

	rawconfig=read_yaml_file(path_config)

	print("Config:",rawconfig)

	# port

	cfg_port=util_valid_int_inrange(
		util_valid_int(
			rawconfig.get(_CFG_PORT),
		),
		minimum=_CFG_PORT_MIN,
		maximum=_CFG_PORT_MAX
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
		_CFG_LANG:cfg_lang,
		_CFG_FLAGS:util_valid_list(rawconfig.get(_CFG_FLAGS),True)
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
		flags:list
	)->Application:

	msg_err:Optional[str]=ldbi_init_sessions(path_programdir)
	if msg_err is not None:
		raise Exception(f"LDBI err.1: {msg_err}")

	userid_root=f"0x{token_hex(24)[:-2]}"

	msg_err:Optional[str]=ldbi_init_users(path_programdir,userid_root)
	if msg_err is not None:
		raise Exception(f"LDBI err.2: {msg_err}")

	# msg_err:Optional[str]=ldbi_save_user(
	# 	path_programdir,_ROOT_USER,_ROOT_USER
	# )
	# if msg_err is not None:
	# 	raise Exception(f"LDBI err.3: {msg_err}")

	app=Application(
		middlewares=[the_middleware_factory]
	)

	app[_CFG_FLAGS]=tuple(flags)

	app[_APP_ROOT_USERID]=userid_root

	app[_APP_PROGRAMDIR]=path_programdir

	app[_APP_CACHE_ASSETS]={}
	
	app[_APP_LANG]=lang

	app[_APP_RDBN]=rdb_name

	has_connection_url=isinstance(rdb_name,str)
	if not has_connection_url:
		print("Connecting to a local MongoDB database")
		app[_APP_RDBC]=AsyncIOMotorClient()

	if has_connection_url:
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
			web_GET(
				"/fgmt/admin/misc",
				route_Admin_fgmt_MiscConfig
			),
				web_POST(
					"/api/admin/misc/change-config",
					route_Admin_api_ChangeConfig
				),
				web_POST(
					"/api/admin/misc/update-known-assets",
					route_Admin_api_UpdateKnownAssetNames
				),

			web_GET(
				"/fgmt/admin/users",
				route_Admin_fgmt_UsersConfig
			),

				# /fgmt/admin/users/get-user
				# /fgmt/admin/users/search

		# ACCOUNT

		web_GET(
			_ROUTE_PAGE_ACCOUNTS,
			route_Accounts,
		),
			web_GET(
				"/fgmt/accounts/login",
				route_Accounts_fgmt_Login
			),
			web_POST(
				"/api/accounts/login",
				route_Accounts_api_Login
			),
			web_POST(
				"/api/accounts/login-otp",
				route_Accounts_api_LoginOTP
			),
			web_POST(
				"/api/accounts/login-magical",
				route_Accounts_api_LoginMagical
			),
			web_DELETE(
				"/api/accounts/logout",
				route_Accounts_api_Logout
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
					"/api/assets/history/{asset_id}/records/{record_id}",
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
				"/fgmt/orders/list-orders",
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
				"/fgmt/orders/current/{order_id}/details",
				route_Order_fgmt_Details
			),
			web_POST(
				"/api/orders/current/{order_id}/add-asset",
				route_Orders_api_UpdateAsset
			),
			web_POST(
				"/api/orders/current/{order_id}/update-asset",
				route_Orders_api_UpdateAsset
			),
			web_DELETE(
				"/api/orders/current/{order_id}/remove-asset",
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

	cfg_port=the_config.get(_CFG_PORT)
	if not isinstance(cfg_port,int):
		sys_exit(1)
		
	cfg_lang=the_config.get(_CFG_LANG)
	if not isinstance(cfg_lang,str):
		sys_exit(1)

	cfg_db_name=the_config.get(_CFG_DB_NAME)
	if not isinstance(cfg_db_name,str):
		sys_exit(1)

	cfg_db_url=the_config.get(_CFG_DB_URL)

	run_app(
		build_app(
			path_appdir,
			cfg_lang,
			cfg_db_name,
			cfg_db_url,
			the_config[_CFG_FLAGS]
		),
		port=cfg_port,
	)
