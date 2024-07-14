#!/usr/bin/python3.9

from datetime import datetime
# from logging import error as log_err
# from logging import exception as log_exc
from pathlib import Path
from typing import Optional,Union

from aiofiles import open as async_open
from yaml import Loader as yaml_Loader
from yaml import load as yaml_load
from yaml import dump as yaml_dump
from yaml import Dumper as yaml_Dumper

def util_rnow()->str:
	now=datetime.now()
	t=f"{now.year}"
	t=f"{t}-{str(now.month).zfill(2)}"
	t=f"{t}-{str(now.day).zfill(2)}"
	t=f"{t}-{str(now.hour).zfill(2)}"
	t=f"{t}-{str(now.minute).zfill(2)}"
	return f"{t}-{str(now.second).zfill(2)}"

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
		minimum:Optional[int]=None,
		maximum:Optional[int]=None,
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

	if data_lowered=="true":
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
