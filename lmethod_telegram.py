#!/usr/bin/python3.9

from typing import Optional

from aiohttp import ClientSession

from internals import (
	util_valid_bool,
	util_valid_str
)

from symbols_Any import (
	_LANG_EN,_LANG_ES,
	_HEADER_ACCEPT,_HEADER_CONTENT_TYPE,
	_MIMETYPE_JSON
)

async def lmethod_telegram(

		lang:str,
		otp:str,

		tg_user:str,
		tg_bot_token:str

	)->Optional[str]:

	# SOURCE: https://core.telegram.org/bots/api#sendmessage
	# LAST CHECKED: 2025-02-18

	url=f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"

	tl={
		_LANG_EN:"Your password is",
		_LANG_ES:"Su contraseña es"
	}[lang]

	the_json={
		"chat_id":tg_user,
		"text":f"{tl}: {otp}",
		"protect_content":True,
	}

	the_headers={
		_HEADER_ACCEPT:_MIMETYPE_JSON,
		_HEADER_CONTENT_TYPE:_MIMETYPE_JSON
	}

	print(
		"\nSending OTP through Telegram bot"
		f"\n\tUser: {tg_user}"
	)

	result={}

	try:
		async with ClientSession(headers=the_headers) as session:
			# session.headers.update(the_headers)
			async with session.post(url,json=the_json) as response:
				result.update(
					await response.json()
				)
	except Exception as exc:
		tl={
			_LANG_EN:"HTTP request error",
			_LANG_ES:"error en la petición HTTP"
		}[lang]
		return f"{tl} → {str(exc)}"

	print("\tResult:",result)

	ok=util_valid_bool(result.get("ok"))
	if not ok:
		desc=util_valid_str(result.get("description"))
		if desc is None:
			return {
				_LANG_EN:"unknown error",
				_LANG_ES:"error desconocido"
			}[lang]

		tl={
			_LANG_EN:"possible motive",
			_LANG_ES:"posible motivo"
		}[lang]

		return f"{tl} → {desc}"
	
	return None

if __name__=="__main__":

	# TEST: Send any string as the "password"

	# NOTE:
	# The user must have contacted the bot previously
	# Line 1: telegram user ID
	# Line 2: telegram bot token

	from asyncio import run as async_run
	from pathlib import Path
	from sys import argv as sys_argv

	anypass=sys_argv[1]

	path_dir=Path(sys_argv[0]).parent

	path_file=path_dir.joinpath("test_otp_telegram.txt")

	tg_user,tg_bot_token=path_file.read_text().splitlines()

	result=async_run(
		lmethod_telegram(
			"en",anypass,
			tg_user,tg_bot_token
		)
	)

	print(result)