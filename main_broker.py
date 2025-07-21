#!/usr/bin/python3.9

from asyncio import to_thread
from pathlib import Path
from secrets import token_hex
from sqlite3 import (
	Connection as SQLiteConnection,
	Cursor as SQLiteCursor,
)
from time import sleep
from typing import (
	Any,
	Mapping,
	Optional,
	Union
)

from internals import (
	# exc_info,
	# util_path_resolv,
	util_valid_str,
	# util_valid_int,
	# read_yaml_file
)

from mod_email import (
	func_send_email,
	config_read as read_config_email,
	_CFG_EMAIL as _TYPE_EMAIL,
)

from mod_telegram import (

	config_read as read_config_telegram,

	util_apicall_send_text_message,

	_CFG_TELEGRAM as _TYPE_TELEGRAM,
		_CFG_TELEGRAM_BOT_TOKEN,
		_CFG_TELEGRAM_API_ID,
		_CFG_TELEGRAM_API_HASH,
)

# from mod_telegram import (
# 	util_read_config as read_cfg_telegram,
# 	util_apicall_send_text_message as st_telegram,
# )

from pysqlitekv import (
		db_init as pysqlitekv_init,
		db_getcon,
		db_post,
		db_lpost,
		db_ldelete,
	)

from symbols_Any import (
	_ERR,
	_DIR_TEMP,
)

# _ACT_HELP="help"
_ACT_CONTINUE="continue"
_ACT_FORCE="restart"
_ACT_LIST="list"
_ACT_RESET="reset"
_ACT_SHUTDOWN="shutdown"
_ACT_HALT="halt"

_SQL_FILE="jobs_queue.db"

_LIST_FIRST=0
_LIST_LAST=-1

_KEYPREFIX_JQUEUE="JQueue"

_LSIG_KILL="KILL"

_EMAIL_MSG_CONT="msg_cont"
_EMAIL_MSG_DEST="msg_dest"
_EMAIL_MSG_SUBJ="msg_subj"

_TELEGRAM_MSG="message"
_TELEGRAM_DEST="dest"

_CMD_SCHEDULE_QUIT="squit"
_CMD_CLEAR_QUEUE="clear"

# Jobs queue (table)

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

def queue_addjob(
		basedir:Path,
		queue_id:int,
		jobdata:Mapping
	)->bool:

	sqlcon:SQLiteConnection=db_getcon(
		util_get_db_file(basedir)
	)
	ok=db_lpost(
		sqlcon,
		f"{_KEYPREFIX_JQUEUE}.{queue_id}",
		jobdata
	)
	sqlcon.close()

	if not ok:
		return False

	return True

def queue_pulljob(
		basedir:Path,
		queue_id:int
	)->Mapping:

	sqlcon:SQLiteConnection=db_getcon(
		util_get_db_file(basedir)
	)
	jobdata:Optional[Any]=db_ldelete(
		sqlcon,
		f"{_KEYPREFIX_JQUEUE}.{queue_id}",
		_LIST_FIRST,
		return_val=True
	)
	sqlcon.close()

	print("Job data:",jobdata)

	if jobdata is None:
		return {}

	if not isinstance(jobdata,Mapping):
		return {}

	return jobdata

def queue_clearjobs(
		basedir:Path,
		queue_id:int
	):

	sqlcon:SQLiteConnection=db_getcon(
		util_get_db_file(basedir)
	)
	ok=db_post(
		sqlcon,
		f"{_KEYPREFIX_JQUEUE}.{queue_id}",
		[],force=True
	)
	if not ok:
		print("Failed to wipe")

	sqlcon.close()

async def next_one(basedir:Path,queue_id:int)->bool:

	job_data:Mapping={}
	try:
		result=await to_thread(
			queue_pulljob,
			basedir,queue_id
		)
		job_data.update(result)
	except Exception as exc:
		print(queue_id,exc)

	if len(job_data)==0:
		return False

	job_type=util_valid_str(
		job_data.get("type"),
		lowerit=True
	)
	if job_type not in (
		_TYPE_EMAIL,
		_TYPE_TELEGRAM,
		"quit"
	):
		return False

	# E-Mails
	# {"type":"email","msg_cont":"","msg_subj":"","msg_dest":""}

	# Telegram
	# {"type":"telegram","message":"","destination"}

	# Quit
	# {"type":"quit"}


	if job_type=="quit":
		return True

	if job_type==_TYPE_EMAIL:

		email_msg_dest=util_valid_str(
			job_data.get(_EMAIL_MSG_DEST),
			lowerit=True
		)
		if email_msg_dest is None:
			return False

		email_msg_subj=util_valid_str(job_data.get(_EMAIL_MSG_SUBJ))
		if email_msg_subj is None:
			return False

		email_msg_cont=util_valid_str(job_data.get(_EMAIL_MSG_CONT))
		if email_msg_cont is None:
			return False

		cfg:Optional[tuple]=None
		try:
			cfg=await to_thread(
				read_config_email(
					basedir,
					as_tuple=True
				)
			)
		except Exception as exc:
			print(queue_id,exc)

		if cfg is None:
			return False

		security,smtp_host,smtp_port,username,password=cfg

		await to_thread(
			func_send_email,
			security,
			smtp_host,smtp_port,
			username,password,
			email_msg_dest,email_msg_subj,email_msg_cont
		)

	if job_type==_TYPE_TELEGRAM:

		email_msg_cont=util_valid_str(job_data.get(_TELEGRAM_MSG))
		if email_msg_cont is None:
			return False

		email_msg_dest=util_valid_str(job_data.get(_TELEGRAM_DEST))
		if email_msg_dest is None:
			return False

		cfg={}
		try:
			result=await to_thread(
				read_config_telegram,
				basedir
			)

			if not len(result)==0:
				cfg.update(result)

		except Exception as exc:
			print(queue_id,exc)

		if len(cfg)==0:
			return False

		tg_bot_token=util_valid_str(cfg.get(_CFG_TELEGRAM_BOT_TOKEN))
		if tg_bot_token is None:
			return False

		tg_api_id=util_valid_str(cfg.get(_CFG_TELEGRAM_API_ID))
		tg_api_hash=util_valid_str(cfg.get(_CFG_TELEGRAM_API_HASH))

		full_client=(tg_api_id is not None) or (tg_api_hash is not None)
		if full_client:
			if (tg_api_id is None) or (tg_api_hash is None):
				return False

		if not full_client:

			await util_apicall_send_text_message(tg_bot_token,)

	return False

async def main(
		basedir:Path,
		queue_id:int
	):

	while True:

		print(
			f"\n{queue_id}",
			"Waiting 1 sec before loading next job..."
		)
		sleep(1)

		kill=(
			await next_one(
				basedir,
				queue_id
			)
		)
		if kill:
			break

if __name__=="__main__":

	from asyncio import run as async_run

	from os import getpid as os_getpid
	from sys import (
		argv as sys_argv,
		exit as sys_exit
	)

	basedir=Path(sys_argv[0]).parent
	queue_id=os_getpid()

	print(
		"PID (QueueID):",
		queue_id
	)

	if not len(sys_argv)==1:

		if len(sys_argv)==3:

			queue_id=int(sys_argv[2])

			if sys_argv[1]==_CMD_CLEAR_QUEUE:
				queue_clearjobs(
					basedir,
					queue_id
				)
				sys_exit(0)

			if sys_argv[1]==_CMD_SCHEDULE_QUIT:
				queue_addjob(
					basedir,
					queue_id,
					{"type":"quit"}
				)
				sys_exit(0)

	ok=pysqlitekv_init(
		util_get_db_file(
			basedir,
			new=True
		),
		confirm_only=True
	)
	if not ok:
		sys_exit(1)

	async_run(
		main(
			basedir,
			queue_id
		)
	)

	sys_exit(0)
