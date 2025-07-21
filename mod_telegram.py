#!/usr/bin/python3.9

from pathlib import Path
from typing import (
	Mapping,
	Optional,
	Union
)
from sqlite3 import (
	Connection as SQLConnection,
	connect as sql_connect
)

from aiohttp import ClientSession

from pyrogram import Client as PyroClient
from pyrogram.types import User

from internals import (
	# util_valid_bool,
	util_valid_str,
	util_valid_int,
)

from pysqlitekv import (
	db_init,db_get,
	DBTransaction,
)

from symbols_Any import (

	# _APP_TGHC,
		# _CFG_TELEGRAM_API_ID,
		# _CFG_TELEGRAM_API_HASH,
		# _CFG_TELEGRAM_BOT_TOKEN,

	_DIR_TEMP,
	_LANG_EN,_LANG_ES,

	_HEADER_ACCEPT,_HEADER_CONTENT_TYPE,

	_ERR,
	_MIMETYPE_JSON,
)

_CFG_TELEGRAM="telegram"
_CFG_TELEGRAM_API_ID="api-id"
_CFG_TELEGRAM_API_HASH="api-hash"
_CFG_TELEGRAM_BOT_TOKEN="bot-token"
# _CFG_TELEGRAM_API_LVL="tg-api-lvl"

_TL_OTP={
	_LANG_EN:"Your password to SHLED",
	_LANG_ES:"Su contraseña para entrar a SHLED"
}

# _TGHC_LABEL="Telegram MTProto Client"

# async def mtproto_start(app:Application):

# 	print(_TGHC_LABEL,"Starting...")

# 	tghc:Optional[PyroClient]=app[_APP_TGHC]

# 	if not isinstance(tghc,PyroClient):
# 		tg_api_id=app[_CFG_TELEGRAM_API_ID]
# 		tg_api_hash=app[_CFG_TELEGRAM_API_HASH]
# 		tg_bot_token=app[_CFG_TELEGRAM_BOT_TOKEN]
# 		tghc=PyroClient(
# 			"shled_tgc",
# 			tg_api_id,tg_api_hash,
# 			bot_token=tg_bot_token
# 		)
# 		app[_APP_TGHC]=tghc

# 	async with tghc:
# 		await tghc.start()
# 	print(_TGHC_LABEL,"started!")

# async def mtproto_restart(app:Application):

# 	print(_TGHC_LABEL,"Restarting...")
# 	tghc:PyroClient=app[_APP_TGHC]
# 	await tghc.restart()
# 	print(_TGHC_LABEL,"restarted!")

# async def mtproto_stop(app:Application):

# 	print(_TGHC_LABEL,"Stopping...")
# 	tghc:PyroClient=app[_APP_TGHC]
# 	await tghc.stop()
# 	print(_TGHC_LABEL,"stoppeed!")

# Level 1

_SQL_FILE="config_telegram.db"

def util_get_db_file(
		basedir:Path,
		new:bool=False
	)->Path:

	fpath=basedir.joinpath(
		_DIR_TEMP,
		_SQL_FILE
	)
	fpath.parent.mkdir(
		parents=True,
		exist_ok=True
	)
	if new:
		if fpath.exists():
			fpath.unlink()

	return fpath

def util_read_config(data:Mapping)->Mapping:

	# if not isinstance(data.get(_CFG_TELEGRAM),Mapping):
	# 	return {}

	tg_bot_token=util_valid_str(
		# data[_CFG_TELEGRAM].get(_CFG_TELEGRAM_BOT_TOKEN)
		data.get(_CFG_TELEGRAM_BOT_TOKEN)
	)
	if not isinstance(tg_bot_token,str):
		return {}

	config_ok={
		_CFG_TELEGRAM_BOT_TOKEN:tg_bot_token
	}

	tg_api_id=util_valid_str(
		# data[_CFG_TELEGRAM].get(_CFG_TELEGRAM_API_ID)
		data.get(_CFG_TELEGRAM_API_ID)
	)
	tg_api_hash=util_valid_str(
		# data[_CFG_TELEGRAM].get(_CFG_TELEGRAM_API_HASH)
		data.get(_CFG_TELEGRAM_API_HASH)
	)
	has_api_id=isinstance(tg_api_id,str)
	has_api_hash=isinstance(tg_api_hash,str)

	if not (has_api_id or has_api_hash):
		return config_ok

	if not has_api_hash:
		return config_ok

	if not has_api_id:
		return config_ok

	config_ok.update({
		_CFG_TELEGRAM_API_ID:tg_api_id,
		_CFG_TELEGRAM_API_HASH:tg_api_hash
	})

	return config_ok

def config_import(
		basedir:Path,
		config:Mapping,
	):

	config_ok=util_read_config(config)
	if len(config_ok)==0:
		return

	sqlcon:SQLConnection=db_init(
		util_get_db_file(
			basedir,
			new=True
		)
	)

	has_api_id=(
		_CFG_TELEGRAM_API_ID in config_ok.keys()
	)
	has_api_hash=(
		_CFG_TELEGRAM_API_HASH in config_ok.keys()
	)

	with DBTransaction(sqlcon) as tx:

		tx.db_post(
			_CFG_TELEGRAM_BOT_TOKEN,
			config_ok[_CFG_TELEGRAM_BOT_TOKEN],
		)

		if has_api_id and has_api_hash:
			tx.db_post(
				_CFG_TELEGRAM_API_ID,
				config_ok[_CFG_TELEGRAM_API_ID],
			)

			tx.db_post(
				_CFG_TELEGRAM_API_HASH,
				config_ok[_CFG_TELEGRAM_API_HASH],
			)

	sqlcon.close()

def config_read(basedir:Path)->Mapping:

	sqlcon:SQLConnection=sql_connect(
		util_get_db_file(
			basedir
		)
	)

	bot_token:Optional[str]=None
	api_id:Optional[str]=None
	api_hash:Optional[str]=None

	with sqlcon.cursor() as cur:

		bot_token=db_get(cur,_CFG_TELEGRAM_BOT_TOKEN)
		api_id=db_get(cur,_CFG_TELEGRAM_API_ID)
		api_hash=db_get(cur,_CFG_TELEGRAM_API_HASH)

	sqlcon.close()

	if bot_token is None:
		return {}

	config={_CFG_TELEGRAM_BOT_TOKEN:bot_token}

	if (api_id is not None) or (api_hash is not None):

		config.update({
			_CFG_TELEGRAM_API_ID:api_id,
			_CFG_TELEGRAM_API_HASH:api_hash
		})

	return config

def util_check_user(
		data:Union[User,Mapping],
		check_type:int=0
	)->bool:

	# Check types
	# 1 → Valid user (has a username, id, and first_name)
	# 2 → Check if the user is a bot (is_bot == True)
	# 3 → Check if the user is a human (is_bot == False)

	prop_userid:Union[int,Optional[str]]=None
	prop_username:Optional[str]=None
	prop_fname:Optional[str]=None
	prop_isbot:Optional[bool]=None

	is_user_obj=isinstance(data,User)

	# User ID

	if is_user_obj:
		prop_userid=data.id
	if not is_user_obj:
		prop_userid=util_valid_int(
			data.get("id")
		)
	if prop_userid is None:
		return False

	# Username

	if check_type==2:

		if is_user_obj:
			prop_username=data.username
		if not is_user_obj:
			prop_username=util_valid_str(
				data.get("username")
			)

		if prop_username is None:
			return False

	# First Name

	if is_user_obj:
		prop_fname=data.first_name
	if not is_user_obj:
		prop_fname=util_valid_str(
			data.get("first_name")
		)
	if prop_fname is None:
		return False

	# Is Bot

	if is_user_obj:
		prop_isbot=data.is_bot
	if not is_user_obj:
		prop_isbot=data.get("is_bot")
	if not isinstance(prop_isbot,bool):
		return False

	if check_type==0:
		return True

	print("\nChecking if this is a user:",data)

	if check_type==1 and prop_isbot:
		return True

	if check_type==2 and (not prop_isbot):
		return True

	return False

	#####################################################3

	# if check_type==0:
	# 	return True

	# is_bot=util_valid_bool(
	# 	data.get("is_bot"),
	# 	dval=False
	# )

	# if check_type==1 and (is_bot):
	# 	return True

	# if check_type==2 and (not is_bot):
	# 	return True

	# return False

async def util_apicall(
		tg_bot_token:str,
		tg_bot_api_method:str,
		get_instead_of_post:bool=False,
		given_headers:Mapping={},
		given_params:Mapping={}
	)->Mapping:

	# https://core.telegram.org/bots/api#making-requests
	# https://core.telegram.org/bots/api#available-methods

	req_url=f"https://api.telegram.org/bot{tg_bot_token}/{tg_bot_api_method}"

	# HTTP Verb

	verb={
		True:"GET",
		False:"POST"
	}[get_instead_of_post]

	# HTTP request headers

	the_headers={_HEADER_ACCEPT:_MIMETYPE_JSON}
	if verb=="POST":
		the_headers.update({
			_HEADER_CONTENT_TYPE:_MIMETYPE_JSON
		})

	the_headers.update(given_headers)

	# HTTP GET Parameters OR POST JSON Body

	req_params:Optional[Mapping]=None
	req_json:Optional[Mapping]=None
	if not len(given_params)==0:
		if verb=="GET":
			req_params=given_params.copy()
		if verb=="POST":
			req_json=given_params.copy()

	# The ACKSHUAL REQWEST

	the_response={}
	try:
		async with ClientSession(headers=the_headers) as session:
			async with session.request(
				verb,req_url,
				params=req_params,
				json=req_json
			) as response:

				the_response.update(
					await response.json()
				)
	except Exception as exc:
		return {_ERR:str(exc)}

	if len(the_response)==0:
		return {_ERR:"empty response???"}

	if the_response.get("ok") is not True:

		# NOTE:
		# the description field is moved to the error field
		# the parameters field (if present) is moved to the params field

		msg_err=the_response.get("description")
		if msg_err is None:
			return {_ERR:"Unknown error"}

		err_json={_ERR:msg_err}

		if the_response.get("parameters"):
			err_json.update({
				"params":the_response["parameters"]
			})

		return err_json

	return the_response

# Level 2

async def util_apicall_get_bot_info(tg_bot_token:str)->Mapping:

	# https://core.telegram.org/bots/api#getme
	# https://core.telegram.org/bots/api#user

	the_response=await util_apicall(
		tg_bot_token,"getMe"
	)
	if the_response.get(_ERR) is not None:
		return the_response

	if not util_check_user(
		the_response["result"],
		check_type=1
	):
		the_response.update({_ERR:"The given bot token is not a bot...?"})

	return the_response["result"].pop("user")

async def util_apicall_get_chat(
		tg_bot_token:str,
		tg_chat:str
	)->Mapping:

	# https://core.telegram.org/bots/api#getchat

	the_response=await util_apicall(
		tg_bot_token,"getChat",
		given_params={"chat_id":tg_chat}
	)
	if the_response.get(_ERR) is not None:
		return the_response

	return the_response

async def util_apicall_get_chat_member(
		tg_bot_token:str,
		tg_chat:str,tg_user:str
	)->Mapping:

	# https://core.telegram.org/bots/api#getchatmember

	the_response=await util_apicall(
		tg_bot_token,"getChatMember",
		given_params={
			"chat_id":tg_chat,
			"user_id":tg_user
		}
	)
	if the_response.get(_ERR) is not None:
		return the_response

	return the_response

async def util_apicall_send_text_message(
		tg_bot_token:str,
		tg_chat:str,
		text:str,
		protect:bool=True
	)->Mapping:

	# https://core.telegram.org/bots/api#sendmessage

	the_response=await util_apicall(
		tg_bot_token,"sendMessage",
		given_params={
			"chat_id":tg_chat,
			"text":text,
			"protect_content":protect,
		}
	)
	if the_response.get(_ERR) is not None:
		return the_response

	return the_response

async def util_mtproto_send_test_message(
		tg_client:PyroClient,
		tg_chat:Union[int,str],
		text:str,
		protect:bool=True
	)->Mapping:

	try:
		await tg_client.send_message(
			tg_chat,text
		)
	except Exception as exc:
		print(_ERR,exc)
		return {_ERR,exc}

	return {}

async def func_botapi_get_user(
		tg_bot_token:str,
		tg_user:str,
		check_type:int=0,
	)->Mapping:

	apicall_res=await util_apicall_get_chat_member(
		tg_bot_token,
		tg_user,
		tg_user
	)

	print("\nAPI Call result:",apicall_res)

	msg_err=apicall_res.get(_ERR)

	if msg_err:
		return {_ERR:msg_err}

	if not util_check_user(
		apicall_res["result"]["user"],
		check_type=check_type
	):
		tl={
			0:"The given ID is not a telegram user",
			1:"The given ID is not a telegram bot",
			2:"The given ID is not a human user"
		}[check_type]
		return {_ERR:tl}

	# Return the user mapping directly instead of the entire result object

	return apicall_res["result"].pop("user")

async def func_botapi_send_otp(
		tg_bot_token:str,
		tg_user:str,
		otp:str,
		lang:str
	)->Mapping:

	text_msg=f"""{_TL_OTP[lang]} {otp}"""

	res_sendmsg=await util_apicall_send_text_message(
		tg_bot_token,
		tg_user,
		text_msg
	)
	if res_sendmsg.get(_ERR) is not None:
		return res_sendmsg

	return {}

async def func_mtproto_send_otp(
		tg_client:PyroClient,
		tg_user:str,
		otp:str,
		lang:str
	)->Mapping:

	text_msg=f"""{_TL_OTP[lang]} {otp}"""

	return (
		await util_mtproto_send_test_message(
			tg_client,tg_user,text_msg
		)
	)

###############################################################################

# async def test(

# 		tg_api_id:str,
# 		tg_api_hash:str,

# 		tg_bot_token:str,
# 		tg_user:str
# 	):

# 	tg_client:PyroClient=PyroClient(
# 		"test",
# 		tg_api_id,tg_api_hash,
# 		bot_token=tg_bot_token
# 	)

# 	print(
# 		"Bot Info:",
# 		await util_apicall_get_bot_info(tg_bot_token)
# 	)

# 	await func_botapi_get_user(tg_bot_token,tg_user,check_type=2)

# 	await func_botapi_send_otp(
# 		tg_bot_token,tg_user,
# 		"0987654321",_LANG_EN
# 	)

# 	# MTProto not sending the message...?

# 	await tg_client.start()

# 	await func_mtproto_send_otp(
# 		tg_client,tg_user,
# 		"12345678",_LANG_ES
# 	)

# 	await tg_client.stop()

# if __name__=="__main__":

# 	# TEST: Send any string as the "password"

# 	# NOTE:
# 	# The user must have contacted the bot previously

# 	# test_otp_telegram.txt:
# 	# Line 1: telegram user ID
# 	# Line 2: telegram bot token

# 	from asyncio import run as async_run
# 	from pathlib import Path
# 	from sys import argv as sys_argv

# 	# path_dir=Path(sys_argv[0]).parent

# 	path_file=Path(sys_argv[1])

# 	# Text file (test credentials) contents
# 	# API_ID
# 	# API_HASH
# 	# BOT_TOKEN
# 	# ANY_TG_USER

# 	tg_api_id,tg_api_hash,tg_bot_token,tg_user=path_file.read_text().splitlines()

# 	result=async_run(

# 		# util_apicall_get_bot_info(tg_bot_token)

# 		# bot.send_message(tg_user,"HELLO")

# 		test(
# 			tg_api_id,tg_api_hash,
# 			tg_bot_token,tg_user
# 		)

# 		# main(
# 		# 	"en",tg_bot_token,
# 		# 	tg_user,anypass,
# 		# )
# 	)

# 	print("FINAL RESULT",result)
