#!/usr/bin/python3.9

from pathlib import Path
from typing import Mapping,Optional
from subprocess import run as sub_run
# from secrets import token_hex

from aiohttp.web import (
	Application,
	run_app,
	get as web_GET,
	post as web_POST,
	delete as web_DELETE,
)

from motor.motor_asyncio import AsyncIOMotorClient

# from pyrogram import Client as PyroClient

from control_Any import (

	the_middleware_factory,
	route_src,
	route_main as route_Home,

)

from control_accounts import (

	route_main as route_Accounts,

	route_fgmt_login as route_Accounts_fgmt_Login,
		route_api_login as route_Accounts_api_Login,
		route_api_login_otp as route_Accounts_api_LoginOTP,
		route_api_login_magical as route_Accounts_api_LoginMagical,
		route_api_logout as route_Accounts_api_Logout,

	route_api_checkin as route_Accounts_api_CheckIn,

	route_fgmt_details as route_Accounts_fgmt_Details,

	# route_api_otp_new as route_Accounts_api_OTPNew,
	# route_api_otp_con as route_Accounts_api_OTPCon,
)

from control_admin import (
	# _ROUTE_PAGE as _ROUTE_PAGE_ADMIN,
	route_main as route_Admin,

	route_fgmt_section_users as route_Admin_fgmt_UsersConfig,
		route_api_new_user as route_Admin_api_new_user,
		route_api_search_users as route_Admin_api_search_users,
		route_api_delete_user as route_Admin_api_delete_user,

	route_fgmt_section_misc as route_Admin_fgmt_MiscConfig,
		route_api_change_config as route_Admin_api_ChangeConfig,
		route_api_dbsync as route_Admin_api_DBSync,
		route_api_data_export as route_Admin_api_DataExport,
)

from control_assets import (
	route_main as route_Assets,
	route_fgmt_export_options as route_Assets_fgmt_ExportOptions,
	route_api_export_as_excel as route_Assets_api_ExportAsExcel,
	route_api_select_asset as route_Assets_api_GetAsset,
	route_fgmt_asset_dashboard as route_Assets_fgmt_AssetDetails,
	route_fgmt_new_asset as route_Assets_fgmt_NewAsset,
	route_api_new_asset as route_Assets_api_NewAsset,
	route_api_asset_edit_definition as route_Assets_api_EditDefinition,
	route_fgmt_search_assets as route_Assets_fgmt_SearchAssets,
	route_api_drop_asset as route_Assets_api_DropAsset,
	route_api_add_record as route_Assets_api_AddRecord,
	route_api_get_record as route_Assets_api_GetRecord,
	# util_update_known_assets as init_assets_cache
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
	# route_api_remove_asset_from_order as route_Orders_api_RemoveAsset,
	route_api_run_order as route_Orders_api_RunOrder,
	route_api_revert_order as route_Orders_api_RevertOrder,
	route_api_export_order_as_spreadsheet as route_Orders_api_ExportAsExcel
)

from dbi_iex import (
	data_import,
	# data_export
)

from dbi_accounts import (
	dbi_init as dbi_init_users,
	# dbi_init_create_users_file,
	# dbi_init_import_users
)

from dbi_assets import (
	dbi_init as dbi_init_assets
)

from dbi_accounts_sessions import (
	dbi_init as dbi_init_sessions,
	# ldbi_save_user,
)

from frontend_Any import util_css_bake

from internals import (
	read_yaml_file,
	util_path_resolv,
	util_valid_int,
	util_valid_int_inrange,
	util_valid_str,
	util_valid_list,
)

# from mod_telegram import util_read_config

from mod_email import (
	config_import as import_cfg_email,
	_CFG_EMAIL
)
from mod_telegram import (
	config_import as import_cfg_telegram,
	_CFG_TELEGRAM,
)

from symbols_Any import (

	# _ROOT_USER,

	_MONGO_URL_DEFAULT,

	_DIR_TEMP,

	_APP_LANG,
	_LANG_EN,_LANG_ES,

	# _APP_CACHE_ASSETS,
	_APP_PROGRAMDIR,
	# _APP_ROOT_USERID,
	# _APP_BAKED_CSS,
	_APP_RDBC,_APP_RDBN,

	# _APP_TGHC,

	_CFG_PORT,_CFG_LANG,_CFG_DB_NAME,_CFG_DB_URL,_CFG_FLAGS,

	_CFG_ACC,
	_CFG_ACC_TIMEOUT_OTP,
	_CFG_ACC_TIMEOUT_SESSION,

	_CFG_FLAG_D_SECURITY,
	_CFG_FLAG_D_STARTUP_CSS_BAKING,
	_CFG_FLAG_E_STARTUP_PRINT_NW_INTERFACES,
	_CFG_FLAG_E_STARTUP_PRINT_ASSETS,
	# _CFG_FLAG_ROOT_LOCAL_AUTOLOGIN,
	# _CFG_FLAG_PUB_READ_ACCESS_TO_HISTORY,
	# _CFG_FLAG_PUB_READ_ACCESS_TO_ORDERS,
	# _CFG_FLAG_PVT_READ_ACCESS_TO_ASSETS,

	_CFG_PORT_MIN,
	_CFG_PORT_MAX,

	# _CFG_TELEGRAM_API_LVL,
	# _CFG_TELEGRAM,
	# 	_CFG_TELEGRAM_API_ID,
	# 	_CFG_TELEGRAM_API_HASH,
	# 	_CFG_TELEGRAM_BOT_TOKEN
)

from symbols_accounts import (

	_ROUTE_PAGE as _ROUTE_PAGE_ACCOUNTS,
		_ROUTE_API_CHECKIN as _ROUTE_ACC_API_CHECKIN,
		_ROUTE_FGMT_LOGIN as _ROUTE_ACC_FGMT_LOGIN,
			_ROUTE_API_LOGIN as _ROUTE_ACC_API_LOGIN,
			_ROUTE_API_LOGIN_OTP as _ROUTE_ACC_API_LOGIN_OTP,
			_ROUTE_API_LOGIN_MAGIC as _ROUTE_ACC_API_LOGIN_MAGIC,
			_ROUTE_API_LOGOUT as _ROUTE_ACC_API_LOGOUT,

		# _ROUTE_API_OTP_NEW as _ROUTE_ACC_API_OTP_NEW,
		# _ROUTE_API_OTP_CON as _ROUTE_ACC_API_OTP_CON
)
from symbols_assets import _ROUTE_PAGE as _ROUTE_PAGE_ASSETS
from symbols_orders import _ROUTE_PAGE as _ROUTE_PAGE_ORDERS

from symbols_admin import (

	_ROUTE_PAGE as _ROUTE_PAGE_ADMIN,
		_ROUTE_FGMT_USERS as _ROUTE_ADMIN_FGMT_USERS,
			_ROUTE_API_USERS_NEW as _ROUTE_ADMIN_API_USERS_NEW,
			_ROUTE_API_USERS_SEARCH as _ROUTE_ADMIN_API_USERS_SEARCH,
			_ROUTE_API_USERS_DELETE as _ROUTE_ADMIN_API_USERS_DELETE,

		_ROUTE_FGMT_MISC as _ROUTE_ADMIN_FGMT_MISC,
			_ROUTE_API_MISC_CHANGE_CONFIG as _ROUTE_ADMIN_API_MISC_CHANGE_CONFIG,
			_ROUTE_API_MISC_DBSYNC as _ROUTE_ADMIN_API_MISC_DBSYNC,
			_ROUTE_API_MISC_EXPORT_DATA as _ROUTE_ADMIN_API_MISC_EXPORT_DATA,
			# _ROUTE_API_MISC_IMPORT_DATA as _ROUTE_ADMIN_API_MISC_IMPORT_DATA,
)

_CMD_HELP="help"
_CMD_IMPORT="import"
_CMD_EXPORT="export"
_CMD_UNKNOWN="Unknown or misused command"


def run_ifconfig_or_ipconfig(platform:str)->Optional[str]:

	name:Optional[str]=None
	if platform=="win32":
		name="ipconfig"

	if platform=="linux":
		name="ifconfig"

	if name is None:
		print("Unlisted platform:",platform)
		return

	print("\nNW Int. {")
	proc=sub_run(name)
	print(
		"} NW Int, ",
		f"return code is {proc.returncode}\n"
	)

def read_config(config_raw:Mapping)->dict:

	cfg_port=util_valid_int_inrange(
		util_valid_int(
			config_raw.get(_CFG_PORT),
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
		config_raw.get(_CFG_LANG),
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
		config_raw.get(_CFG_DB_NAME),
		True
	)
	if not isinstance(cfg_db_name,str):
		print(
			f"'{_CFG_DB_NAME}' key not found in config"
		)
		return {}

	# db-url

	cfg_db_url=util_valid_str(
		config_raw.get(_CFG_DB_URL),
	)
	if not isinstance(cfg_db_url,str):
		print(
			f"'{_CFG_DB_URL}' key not found in config: A local database will be used instead"
		)
		cfg_db_url=_MONGO_URL_DEFAULT,

	cfg_acc_timeout_otp=60
	cfg_acc_timeout_session=60

	if isinstance(
		config_raw.get(_CFG_ACC),
		Mapping
	):
		cfg_acc_timeout_otp=util_valid_int(
			config_raw[_CFG_ACC].get(_CFG_ACC_TIMEOUT_OTP),
			fallback=60
		)
		cfg_acc_timeout_session=util_valid_int(
			config_raw[_CFG_ACC].get(_CFG_ACC_TIMEOUT_SESSION),
			fallback=60
		)

	if cfg_acc_timeout_otp<60:
		cfg_acc_timeout_otp=60

	if cfg_acc_timeout_session<60:
		cfg_acc_timeout_session=60

	# all ok

	config={
		_CFG_DB_NAME:cfg_db_name,
		_CFG_DB_URL:cfg_db_url,
		_CFG_PORT:cfg_port,
		_CFG_LANG:cfg_lang,
		_CFG_FLAGS:util_valid_list(config_raw.get(_CFG_FLAGS),True),
		_CFG_ACC_TIMEOUT_OTP:cfg_acc_timeout_otp,
		_CFG_ACC_TIMEOUT_SESSION:cfg_acc_timeout_session
	}

	return config

def build_app(
		path_programdir:Path,
		platform:str,
		config:Mapping,
	)->Application:

	# Essentials

	lang=config.get(_CFG_LANG)
	rdb_name=config.get(_CFG_DB_NAME)
	rdb_url=config.get(_CFG_DB_URL)

	# Tweaks

	acc_timeout_otp=config.get(_CFG_ACC_TIMEOUT_OTP)
	acc_timeout_session=config.get(_CFG_ACC_TIMEOUT_SESSION)

	flags=config.get(_CFG_FLAGS)
	security_disabled=(_CFG_FLAG_D_SECURITY in flags)

	# Base directory

	path_programdir.joinpath(_DIR_TEMP).mkdir(
		exist_ok=True,
		parents=True
	)

	if not security_disabled:
		dbi_init_users(
			path_programdir,
			rdb_name,rdb_url
		)
		dbi_init_sessions(path_programdir)

	dbi_init_assets(
		path_programdir,
		rdb_name,rdb_url,
		verbose=(
			_CFG_FLAG_E_STARTUP_PRINT_ASSETS in flags
		)
	)

	app=Application(
		middlewares=[the_middleware_factory]
	)

	app[_CFG_ACC_TIMEOUT_OTP]=acc_timeout_otp
	app[_CFG_ACC_TIMEOUT_SESSION]=acc_timeout_session
	app[_CFG_FLAGS]=tuple(flags)

	app[_APP_PROGRAMDIR]=path_programdir
	# app[_APP_CACHE_ASSETS]={}
	app[_APP_LANG]=lang
	app[_APP_RDBN]=rdb_name

	# motor (MongoDB)

	app[_APP_RDBC]=AsyncIOMotorClient(rdb_url)

	# Routes

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
				_ROUTE_ADMIN_FGMT_MISC,
				route_Admin_fgmt_MiscConfig
			),
				web_POST(
					_ROUTE_ADMIN_API_MISC_CHANGE_CONFIG,
					route_Admin_api_ChangeConfig
				),
				web_POST(
					_ROUTE_ADMIN_API_MISC_DBSYNC,
					route_Admin_api_DBSync
				),
				web_GET(
					_ROUTE_ADMIN_API_MISC_EXPORT_DATA,
					route_Admin_api_DataExport
				),
					web_POST(
						_ROUTE_ADMIN_API_MISC_EXPORT_DATA,
						route_Admin_api_DataExport
					),

				# web_POST(
				# 	_ROUTE_ADMIN_API_MISC_IMPORT_DATA,
				# 	pass
				# ),

			web_GET(
				_ROUTE_ADMIN_FGMT_USERS,
				route_Admin_fgmt_UsersConfig
			),
				web_POST(
					_ROUTE_ADMIN_API_USERS_NEW,
					route_Admin_api_new_user
				),
				web_POST(
					_ROUTE_ADMIN_API_USERS_SEARCH,
					route_Admin_api_search_users
				),
				web_DELETE(
					_ROUTE_ADMIN_API_USERS_DELETE,
					route_Admin_api_delete_user
				),

		# ACCOUNT

		web_GET(
			_ROUTE_PAGE_ACCOUNTS,
			route_Accounts,
		),
			web_POST(
				_ROUTE_ACC_API_CHECKIN,
				route_Accounts_api_CheckIn
			),
			web_GET(
				_ROUTE_ACC_FGMT_LOGIN,
				route_Accounts_fgmt_Login
			),
			web_POST(
				_ROUTE_ACC_API_LOGIN,
				route_Accounts_api_Login
			),
			web_POST(
				_ROUTE_ACC_API_LOGIN_OTP,
				route_Accounts_api_LoginOTP
			),
				# web_POST(
				# 	_ROUTE_ACC_API_OTP_NEW,
				# 	route_Accounts_api_OTPNew
				# ),
				# web_POST(
				# 	_ROUTE_ACC_API_OTP_CON,
				# 	route_Accounts_api_OTPCon
				# ),

			web_POST(
				_ROUTE_ACC_API_LOGIN_MAGIC,
				route_Accounts_api_LoginMagical
			),
			web_DELETE(
				_ROUTE_ACC_API_LOGOUT,
				route_Accounts_api_Logout
			),

			web_GET(
				"/fgmt/accounts/details",
				route_Accounts_fgmt_Details
			),
				web_GET(
					"/fgmt/accounts/details/{userid_req}",
					route_Accounts_fgmt_Details
				),

		# ASSETS

		web_GET(
			_ROUTE_PAGE_ASSETS,
			route_Assets
		),
			web_GET(
				"/fgmt/assets/export-options",
				route_Assets_fgmt_ExportOptions
			),

				web_GET(
					"/api/assets/export-as-spreadsheet",
					route_Assets_api_ExportAsExcel,
				),
				web_POST(
					"/api/assets/export-as-spreadsheet",
					route_Assets_api_ExportAsExcel,
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

			web_POST(
				# NOTE: For custom clients only
				"/api/assets/get-asset",
				route_Assets_api_GetAsset
			),

			web_POST(
				# NOTE: nope, this is not a mistake
				"/api/assets/exact-match",
				route_Assets_fgmt_AssetDetails
			),

			web_GET(
				"/fgmt/assets/pool/{asset_id}",
				route_Assets_fgmt_AssetDetails
			),
				web_GET(
					"/fgmt/assets/pool/{asset_id}/details",
					route_Assets_fgmt_AssetDetails
				),
				web_POST(
					"/api/assets/pool/{asset_id}/edit",
					route_Assets_api_EditDefinition
				),

				web_DELETE(
					"/api/assets/pool/{asset_id}/drop",
					route_Assets_api_DropAsset
				),
					web_DELETE(
						"/api/assets/drop-asset",
						route_Assets_api_DropAsset
					),
					web_DELETE(
						"/api/assets/pool/{asset_id}/drop-as-item",
						route_Assets_api_DropAsset
					),

				web_POST(
					"/api/assets/pool/{asset_id}/history/add",
					route_Assets_api_AddRecord
				),
					web_POST(
						"/api/assets/history/add",
						route_Assets_api_AddRecord
					),

				web_GET(
					"/fgmt/assets/pool/{asset_id}/history/records/{record_id}",
					route_Assets_api_GetRecord
				),

		# ORDERS

		web_GET(
			# "/page/orders",
			_ROUTE_PAGE_ORDERS,
			route_Orders
		),
			web_GET(
				"/api/orders/pool/{order_id}/spreadsheet",
				route_Orders_api_ExportAsExcel
			),
				web_POST(
					"/api/orders/pool/{order_id}/spreadsheet",
					route_Orders_api_ExportAsExcel
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
				"/fgmt/orders/all-orders",
				route_Orders_fgmt_ListOrders
			),

			web_GET(
				# NOTE: Full Order dashboard layout
				"/fgmt/orders/pool/{order_id}",
				route_Order_fgmt_Details
			),
				web_GET(
					# NOTE: Order details (as item)
					"/fgmt/orders/pool/{order_id}/details-item",
					route_Order_fgmt_Details
				),
				web_GET(
					# NOTE: Order details (dashboard)
					"/fgmt/orders/pool/{order_id}/details",
					route_Order_fgmt_Details
				),
				web_GET(
					# NOTE: Order assets (dashboard)
					"/fgmt/orders/pool/{order_id}/assets",
					route_Order_fgmt_Details
				),

			web_GET(
				"/fgmt/orders/pool/{order_id}/search-assets",
				route_Assets_fgmt_SearchAssets
			),
				web_POST(
					"/api/orders/pool/{order_id}/search-assets",
					route_Assets_api_SearchAssets
				),

			web_POST(
				"/api/orders/pool/{order_id}/add-asset",
				route_Orders_api_UpdateAsset
			),
			web_POST(
				"/api/orders/pool/{order_id}/update-asset",
				route_Orders_api_UpdateAsset
			),
			web_DELETE(
			# web_POST(
				"/api/orders/pool/{order_id}/remove-asset",
				route_Orders_api_UpdateAsset
				# route_Orders_api_RemoveAsset
			),
			web_POST(
				"/api/orders/pool/{order_id}/run",
				route_Orders_api_RunOrder
			),
			web_POST(
				"/api/orders/pool/{order_id}/revert",
				route_Orders_api_RevertOrder
			),
			web_DELETE(
				"/api/orders/pool/{order_id}/drop",
				route_Orders_api_DeleteOrder
			),
				web_DELETE(
					"/api/orders/pool/{order_id}/drop-as-item",
					route_Orders_api_DeleteOrder
				),
				web_DELETE(
					"/api/orders/drop-order",
					route_Orders_api_DeleteOrder
				),
	])

	# Display network interfaces ?

	if _CFG_FLAG_E_STARTUP_PRINT_NW_INTERFACES in flags:
		run_ifconfig_or_ipconfig(platform)

	# Disable CSS Baking ?

	devmode_css=(_CFG_FLAG_D_STARTUP_CSS_BAKING in flags)
	if not devmode_css:
		if not util_css_bake(path_programdir,True):
			print("WARNING: Unable to create the custom.css file")

	return app

if __name__=="__main__":

	from sys import argv as sys_argv
	from sys import exit as sys_exit
	from sys import platform as sys_platform

	path_bin=Path(sys_argv[0])
	path_appdir=path_bin.parent

	cli_job:Optional[str]=None

	if not len(sys_argv)==1:

		if len(sys_argv)==2:
			if sys_argv[1]==_CMD_HELP:
				help=(
					# TODO: Implement the export through the CLI...
					"SHLED CLI commands" "\n"
					"\n" f"$ {path_bin.name} export [FilePath]" "\n"
						"\t" "Connects to the remote database and exports all assets, orders and users to an external file" "\n"
					"\n" f"$ {path_bin.name} import [FilePath]" "\n"
						"\t" "Imports assets, orders and users from a data file to the remote database, overwritting any existing values"
				)
				print(f"\n{help}\n")
				sys_exit(0)

		if len(sys_argv)==3:
			print(sys_argv)
			if sys_argv[1] in (_CMD_IMPORT,_CMD_EXPORT):
				cli_job=sys_argv[1]

		if cli_job is None:
			print(_CMD_UNKNOWN)
			sys_exit(1)

	path_cfg:Optional[Path]=None
	if len(sys_argv)==2:
		path_cfg=util_path_resolv(
			path_appdir,
			Path(sys_argv[1].strip())
		)

	if not isinstance(path_cfg,Path):
		path_cfg=path_appdir.joinpath(
			"config.yaml"
		)

	the_config_raw=read_yaml_file(path_cfg)

	the_config=read_config(the_config_raw)
	if len(the_config)==0:
		sys_exit(1)

	if cli_job==_CMD_IMPORT:

		tables={
			0:"Assets",
			1:"Orders",
			2:"Users"
		}

		fse=Path(sys_argv[2].strip())
		for p in (0,1,2):

			print(f"\n[ Importing {tables[p]} ]")

			msg_err=data_import(
				path_appdir,fse,
				the_config[_CFG_DB_URL],
				the_config[_CFG_DB_NAME],
				cur_page=p
			)
			if msg_err is not None:
				print(msg_err)
				break

		if msg_err is not None:
			print(msg_err)
			sys_exit(1)

		print("Import process finished")
		sys_exit(0)

	# if cli_job==_CMD_EXPORT:

	# 	fse=Path(sys_argv[2].strip())
	# 	msg_err=data_export(
	# 		fse,
	# 		the_config[_CFG_DB_URL],
	# 		the_config[_CFG_DB_NAME]
	# 	)
	# 	if msg_err is not None:
	# 		print(msg_err)
	# 		sys_exit(1)

	cfg_port=the_config.pop(_CFG_PORT)

	if isinstance(the_config_raw.get(_CFG_EMAIL),Mapping):
		print("[!] E-mail config detected")
		import_cfg_email(
			path_appdir,
			the_config_raw[_CFG_EMAIL]
		)

	if isinstance(the_config_raw.get(_CFG_TELEGRAM),Mapping):
		print("[!] Telegram config detected")
		import_cfg_telegram(
			path_appdir,
			the_config_raw[_CFG_TELEGRAM]
		)

	run_app(
		build_app(
			path_appdir,
			sys_platform,
			the_config
		),
		port=cfg_port,
	)
