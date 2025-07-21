#!/usr/bin/python3.9

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pathlib import Path

from smtplib import SMTP,SMTP_SSL
from ssl import _create_unverified_context as ssl_uvcontext
from sqlite3 import (
	Connection as SQLConnection,
	connect as sql_connect
)
from typing import Mapping,Optional,Union
from unicodedata import normalize as unorm

from internals import util_valid_int,util_valid_str
from pysqlitekv import (
	db_init,db_get,
	DBTransaction,
)
from symbols_Any import _DIR_TEMP

_CFG_EMAIL="email"
_CFG_EMAIL_SECURITY="security"
_CFG_EMAIL_USERNAME="username"
_CFG_EMAIL_PASSWORD="password"
_CFG_EMAIL_HOST="host"
_CFG_EMAIL_PORT="port"

_SQL_FILE="config_email.db"

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

	# if not isinstance(data.get(_CFG_EMAIL),Mapping):
	# 	return {}

	# E-Mail security

	val_security=util_valid_int(
		# data[_CFG_EMAIL].get(_CFG_EMAIL_SECURITY),
		data.get(_CFG_EMAIL_SECURITY),
	)
	if not isinstance(val_security,int):
		return {}

	if val_security not in range(0,4):
		return {}

	# E-Mail Username

	val_username=util_valid_str(
		# data[_CFG_EMAIL].get(_CFG_EMAIL_USER),
		data.get(_CFG_EMAIL_USERNAME),
		lowerit=True
	)
	if not isinstance(val_username,str):
		return {}

	# E-Mail Password

	val_password=util_valid_str(
		# data[_CFG_EMAIL].get(_CFG_EMAIL_PASS)
		data.get(_CFG_EMAIL_PASSWORD)
	)
	if not isinstance(val_password,str):
		return {}

	# SMTP Host

	val_host=util_valid_str(
		# data[_CFG_EMAIL].get(_CFG_EMAIL_HOST),
		data.get(_CFG_EMAIL_HOST),
		lowerit=True
	)
	if not isinstance(val_host,str):
		return {}

	# SMTP Port

	val_port=util_valid_int(
		# data[_CFG_EMAIL].get(_CFG_EMAIL_PORT)
		data.get(_CFG_EMAIL_PORT)
	)
	if not isinstance(val_port,str):
		return {}

	return {
		_CFG_EMAIL_HOST:val_host,
		_CFG_EMAIL_PORT:val_port,
		_CFG_EMAIL_USERNAME:val_username,
		_CFG_EMAIL_PASSWORD:val_password,
		_CFG_EMAIL_SECURITY:val_security
	}

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

	with DBTransaction(sqlcon) as tx:

		tx.db_post(
			_CFG_EMAIL_HOST,
			config_ok[_CFG_EMAIL_HOST],
		)
		tx.db_post(
			_CFG_EMAIL_PORT,
			config_ok[_CFG_EMAIL_PORT]
		)
		tx.db_post(
			_CFG_EMAIL_USERNAME,
			config_ok[_CFG_EMAIL_USERNAME]
		)
		tx.db_post(
			_CFG_EMAIL_PASSWORD,
			config_ok[_CFG_EMAIL_PASSWORD]
		)
		tx.db_post(
			_CFG_EMAIL_SECURITY,
			config_ok[_CFG_EMAIL_SECURITY]
		)

	sqlcon.close()

def config_read(
		basedir:Path,
		as_tuple:bool=False
	)->Union[Mapping,Optional[tuple]]:

	sqlcon:SQLConnection=sql_connect(
		util_get_db_file(
			basedir
		)
	)

	security:Optional[int]=None
	smtp_host:Optional[str]=None
	smtp_port:Optional[int]=None
	username:Optional[str]=None
	password:Optional[str]=None

	with sqlcon.cursor() as cur:

		security=db_get(cur,_CFG_EMAIL_SECURITY)
		smtp_host=db_get(cur,_CFG_EMAIL_HOST)
		smtp_port=db_get(cur,_CFG_EMAIL_PORT)
		username=db_get(cur,_CFG_EMAIL_USERNAME)
		password=db_get(cur,_CFG_EMAIL_PASSWORD)

	sqlcon.close()

	if smtp_host is None:
		if as_tuple:
			return None
		return {}
	if smtp_port is None:
		if as_tuple:
			return None
		return {}
	if username is None:
		if as_tuple:
			return None
		return {}
	if password is None:
		if as_tuple:
			return None
		return {}
	if security is None:
		if as_tuple:
			return None
		return {}

	if as_tuple:
		return (
			security,
			smtp_host,
			smtp_port,
			username,
			password,
		)

	return {
		_CFG_EMAIL_SECURITY:security,
		_CFG_EMAIL_HOST:smtp_host,
		_CFG_EMAIL_PORT:smtp_port,
		_CFG_EMAIL_USERNAME:username,
		_CFG_EMAIL_PASSWORD:password,
	}

def config_modify(
		basedir:Path,
		smtp_host:Optional[str]=None,
		smtp_port:Optional[int]=None,
		username:Optional[str]=None,
		password:Optional[str]=None,
		security:Optional[int]=None,
	):

	sqlcon:SQLConnection=sql_connect(
		util_get_db_file(basedir)
	)

	with DBTransaction(sqlcon) as tx:

		if smtp_host is not None:
			tx.db_post(
				_CFG_EMAIL_HOST,
				smtp_host,
			)

		if smtp_port is not None:
			tx.db_post(
				_CFG_EMAIL_PORT,
				smtp_port
			)

		if username is not None:
			tx.db_post(
				_CFG_EMAIL_USERNAME,
				username
			)

		if password is not None:
			tx.db_post(
				_CFG_EMAIL_PASSWORD,
				password
			)

		if security is not None:
			tx.db_post(
				_CFG_EMAIL_SECURITY,
				security
			)

	sqlcon.close()

#################################################

def util_build_message(
		addr_from:str,addr_list:list,
		msg_subj:Optional[str]=None,
		msg_text:Optional[str]=None,
		msg_att:Optional[Path]=None
	)->MIMEMultipart:

	msg=MIMEMultipart()
	msg["From"]=addr_from
	msg["To"]=addr_list[0]

	if isinstance(msg_subj,str):
		msg["Subject"]=msg_subj

	addr_qtty=len(addr_list)
	if addr_qtty>1:
		addr_cc=""
		c=0
		for addr in addr_list:
			addr_cc=f"{addr_cc}{addr}"
			c=c+1
			if c==addr_qtty:
				break
			addr_cc=f"{addr_cc},"

		msg["Cc"]=addr_cc

	if isinstance(msg_text,str):

		obj_text=MIMEText(msg_text,"plain")
		msg.attach(obj_text)

	if isinstance(msg_att,str):

		the_data=b""
		with open(msg_att,"rb") as f:
			the_data=f.read()

		safer_name=unorm("NFD",msg_att.name).encode("ascii","ignore").decode().replace(" ","_")

		obj_att=MIMEBase(
			"application",
			"octet-stream"
		)
		obj_att.set_payload(the_data)
		encoders.encode_base64(obj_att)
		obj_att.add_header(
			"Content-Disposition",
			f"attachment; filename=\"{safer_name}\""
		)
		msg.attach(obj_att)

	return msg

def util_create_smtp_client(
		host:str,port:int,
		secure_now:bool,
		use_context:bool
	)->Union[SMTP,SMTP_SSL]:

	if secure_now:
		if not use_context:
			return SMTP_SSL(host,port)

		return SMTP_SSL(
			host,port,
			context=ssl_uvcontext()
		)

	return SMTP(host,port)

def func_send_email(

		security:int,

			server_host:str,
			server_port:int,

			username:str,
			password:str,

		msg_dest:str,

			subj:Optional[str]=None,
			text:Optional[str]=None,
			att:Optional[Path]=None

	)->bool:

	# https://realpython.com/python-send-email/#sending-fancy-emails
	# https://stackoverflow.com/questions/51117357/python3-sending-email-with-smtplib-yandex

	use_starttls=(security==1)
	use_tls_wc=(security==3)

	# msg_err=None

	the_message=util_build_message(
		username,
		msg_dest,
		subj,text,att
	)

	smtp_conn:Optional[Union[SMTP,SMTP_SSL]]=None
	try:

		print("\t[-] Creating SMTP client...")
		smtp_conn=util_create_smtp_client(
			server_host,server_port,
			(security>1),use_tls_wc
		)

		if use_starttls:
			print("\t[-] Securing with STARTTLS...")
			smtp_conn.starttls()

	except Exception as exc:
		print("\t[ERR] SMTP client setup failed:",exc)
		return False

	try:
		print("\t[-] Sending EHLO or HELO...")
		smtp_conn.ehlo_or_helo_if_needed()

		print("\t[-] Login in...")
		smtp_conn.login(username,password)

		print("\t[-] Sending the message...")
		smtp_conn.send_message(the_message)

		print("\t[-] Closing connection...")
		smtp_conn.quit()

	except Exception as exc:
		print("\t[ERR] Failed to send the message",exc)
		return False

	return True

	# try:

	# 	# print("\t[-] Creating SMTP client...")
	# 	# smtp_conn=util_create_smtp_client(
	# 	# 	server_host,server_port,
	# 	# 	(security>1),use_tls_wc
	# 	# )

	# 	# if use_starttls:
	# 	# 	print("\t[-] Securing with STARTTLS...")
	# 	# 	smtp_conn.starttls()

	# 	print("\t[-] Sending EHLO or HELO...")
	# 	smtp_conn.ehlo_or_helo_if_needed()

	# 	print("\t[-] Login in...")
	# 	smtp_conn.login(username,password)

	# 	print("\t[-] Sending the message...")
	# 	smtp_conn.send_message(the_message)

	# 	print("\t[-] Closing connection...")
	# 	smtp_conn.quit()

	# except:
	# 	log_exc("Failed to send the message")
	# 	return False

	# return True
