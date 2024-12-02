#!/usr/bin/python3.9

from datetime import datetime,timedelta
from hashlib import sha256 as hash_sha256
from hashlib import md5 as hash_md5
from pathlib import Path
from typing import Optional,Union,Mapping

from aiohttp.web import Request
from aiofiles import open as async_open
from yaml import Loader as yaml_Loader
from yaml import load as yaml_load
from yaml import dump as yaml_dump
from yaml import Dumper as yaml_Dumper

from symbols_Any import _excel_columns
from symbols_Any import _COOKIE_AKEY,_COOKIE_USER
from symbols_Any import _HEADER_USER_AGENT

# excel related

def util_excel_dectocol(decimal_start:int):

	table_size=len(_excel_columns)

	result:str=""
	decimal:int=decimal_start

	while decimal>0:

		remainder=decimal%table_size
		result=f"{_excel_columns[remainder]}{result}"
		decimal=decimal//table_size
	
	return result

# hashing stuff

def util_hash_sha256(content:str)->str:
	m=hash_sha256()
	m.update(content.encode())
	return m.hexdigest()

def util_hash_md5(content:str)->str:
	m=hash_md5()
	m.update(content.encode())
	return m.hexdigest()

# user session management related

def util_get_pid_from_request(request:Request)->tuple:

	# PID = Partially Identifiable Data

	ip_address=request.remote
	user_agent=util_valid_str(
		request.headers.get(_HEADER_USER_AGENT)
	)

	return (ip_address,user_agent)

def util_extract_from_cookies(
		request:Request
	)->Optional[tuple]:

	# Pulls username and access key from request cookies

	username=request.cookies.get(_COOKIE_USER)
	if username is None:
		return None

	access_key=request.cookies.get(_COOKIE_AKEY)
	if access_key is None:
		return None

	return (username,access_key)

def util_date_calc_age(
		pit:datetime,
		in_min:bool=False,
	)->int:

	now=datetime.now().utcnow()
	age_td=now-pit

	age=age_td.total_seconds()

	if in_min:
		return age/60

	return age

def util_valid_date(
		dt_string:str,
		get_dt:bool=False
	)->Optional[Union[str,datetime]]:

	if not isinstance(dt_string,str):
		return None

	dtobj:Optional[datetime]=None
	try:
		dtobj=datetime.strptime(
			dt_string,
			"%Y-%m-%d-%H-%M-%S"
		)
	except Exception as exc:
		print("date parsing error:",exc)
		if get_dt:
			return None
		return None

	if get_dt:
		return dtobj

	return dt_string

def util_rnow()->str:
	now=datetime.now().utcnow()
	t=f"{now.year}"
	t=f"{t}-{str(now.month).zfill(2)}"
	t=f"{t}-{str(now.day).zfill(2)}"
	t=f"{t}-{str(now.hour).zfill(2)}"
	t=f"{t}-{str(now.minute).zfill(2)}"
	return f"{t}-{str(now.second).zfill(2)}"

def util_date_calc_expiration(
		pit:Optional[datetime],
		thold:int,in_min:bool=False,
		get_age:bool=True,
		get_exp_flag:bool=True,
		get_exp_date:bool=True
	)->Mapping:

	if not isinstance(pit,datetime):
		return {}

	the_age=util_date_calc_age(
		pit,in_min=in_min
	)

	result={}

	if get_age:
		result.update({"age":the_age})

	if get_exp_flag:
		result.update({"expired":(the_age>thold)})

	if get_exp_date:
		if in_min:
			thold=thold*60

		exp_date=pit+timedelta(seconds=thold)

		result.update({"exp_date":exp_date})

	return result

# Validation stuff

def util_valid_str_inrange(
		data:Optional[str],
		values:Union[list,tuple],
	)->str:

	if not isinstance(data,str):
		return None

	if data not in values:
		return None

	return data

def util_valid_str(
		data:Optional[str],
		lowerit:bool=False
	)->Optional[str]:

	if not isinstance(data,str):
		return None

	data_ok=data.strip()
	if len(data_ok)==0:
		return None

	if lowerit:
		return data_ok.lower()

	return data_ok

def util_valid_int_inrange(
		data:Optional[int],
		fallback:Optional[int]=None,
		minimum:Optional[int]=None,
		maximum:Optional[int]=None,
	)->Optional[int]:

	if not isinstance(data,int):
		return fallback

	chk_min=isinstance(minimum,int)
	chk_max=isinstance(maximum,int)
	closed=(chk_min and chk_max)

	above_min=False
	if chk_min:
		if data>minimum-1:
			above_min=True

	below_max=False
	if chk_max:
		if data<maximum+1:
			below_max=True

	if closed:
		if above_min and below_max:
			return data
		return fallback

	if chk_min:
		if above_min:
			return data

	if chk_max:
		if below_max:
			return data

	return fallback

def util_valid_int(
		data:Optional[Union[str,int]],
		fallback:Optional[int]=None,
	)->Optional[int]:

	if not isinstance(data,(str,int)):
		return fallback

	if isinstance(data,int):
		return data

	if data.isdigit():
		return int(data)

	if not data.startswith("-"):
		return fallback

	if not data[1:].isdigit():
		return fallback

	return int(data)

def util_valid_bool(
		data:Union[Optional[str],bool],
		dval:Optional[bool]=None
	)->Optional[bool]:

	if not isinstance(data,(str,bool)):
		return dval

	if isinstance(data,bool):
		return data

	data_lowered=data.strip().lower()

	if data_lowered=="true" or data_lowered=="on":
		return True

	if data_lowered=="false":
		return False

	return dval

def util_valid_list(
		data:Optional[list],
		default_to_empty:bool=False,
	)->Optional[list]:

	if not isinstance(data,list):
		if default_to_empty:
			return []
		return None

	return data

# YAML related

def is_yaml(filepath):
	if not filepath.exists():
		return False
	if not filepath.is_file():
		return False
	if filepath.stat().st_size>1024*8:
		return False
	if filepath.suffix.lower() not in (".yaml",".yml"):
		return False

	return True

def read_yaml_file(filepath:Path)->dict:
	if not is_yaml(filepath):
		return {}

	data={}
	try:
		data.update(
			yaml_load(
				filepath.read_text(),
				Loader=yaml_Loader,
			)
		)
	except Exception as e:
		print(e)
		return {}

	return data

async def read_yaml_file_async(filepath:Path)->dict:

	if not is_yaml(filepath):
		return {}

	data={}
	try:

		the_text=""

		async with async_open(filepath) as f:
			the_text=await f.read()

		data.update(
			yaml_load(
				the_text,
				Loader=yaml_Loader,
			)
		)
	except Exception as e:
		print(e)
		return {}

	return data

async def write_yaml_file(
		filepath:Path,data:dict,
		check_first:bool=True
	)->bool:

	if check_first:
		if filepath.exists() and (not filepath.is_file()):
			return False

	try:
		dump=yaml_dump(
			data,
			Dumper=yaml_Dumper
		)
		filepath.write_text(dump)

	except Exception as e:
		print(e)
		return False

	return True

async def write_yaml_file_async(
		filepath:Path,data:dict,
		check_first:bool=True
	)->bool:

	if check_first:
		if filepath.exists() and (not filepath.is_file()):
			return False

	try:
		dump=yaml_dump(
			data,
			Dumper=yaml_Dumper
		)
		async with async_open(filepath,mode="wt") as f:
			await f.write(dump)

	except Exception as e:
		print(e)
		return False

	return True
