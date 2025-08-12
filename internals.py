#!/usr/bin/python3.9

from datetime import datetime,timedelta
from hashlib import (
	sha256 as hash_sha256,
	md5 as hash_md5
)
from pathlib import Path
from typing import Mapping,Optional,Union

# from aiohttp.web import Request
from aiofiles import open as async_open
from yaml import (
	Loader as yaml_Loader,
	load as yaml_load,
	dump as yaml_dump,
	Dumper as yaml_Dumper
)
# from yarl import URL as Yurl

from symbols_Any import (
	# _excel_columns,
	# _MONGO_URL_DEFAULT,

	# _COOKIE_AKEY,_COOKIE_USER,
	# _HEADER_USER_AGENT,

	_FMT_DATE_YM,
	_FMT_DATE_YMD,
	_FMT_DATE_YMDH,
	_FMT_DATE_YMDHM,
	_FMT_DATE_YMDHMS
)

# Others

def exc_info(exc:Exception)->str:
	filename=f"{exc.__traceback__.tb_frame.f_code.co_filename}"
	line=f"{exc.__traceback__.tb_lineno}"
	return f"{filename}:{line}:{exc}"

def util_path_resolv(
		path_base:Path,
		path_given:Path
	)->Path:

	if path_given.is_absolute():
		return path_given

	return path_base.joinpath(path_given)

# def util_parse_mongo_url(given_url:Optional[str])->Yurl:

# 	if not isinstance(given_url,str):
# 		return Yurl(_MONGO_URL_DEFAULT)

# 	if not given_url.startswith("mongodb://"):
# 		return Yurl(_MONGO_URL_DEFAULT)

# 	the_yurl:Optional[Yurl]=None
# 	try:
# 		the_yurl=Yurl(given_url)

# 	except:
# 		return Yurl(_MONGO_URL_DEFAULT)

# hi-level string to hash functions

def util_hash_sha256(content:str)->str:
	m=hash_sha256()
	m.update(content.encode())
	return m.hexdigest()

def util_hash_md5(content:str)->str:
	m=hash_md5()
	m.update(content.encode())
	return m.hexdigest()

# user session management related

# def util_extract_from_cookies(
# 		request:Request
# 	)->Optional[tuple]:

# 	# Pulls username and access key from request cookies

# 	username=request.cookies.get(_COOKIE_USER)
# 	if username is None:
# 		return None

# 	access_key=request.cookies.get(_COOKIE_AKEY)
# 	if access_key is None:
# 		return None

# 	return (username,access_key)

# date and time

def util_date_get_day(dt_obj:datetime)->datetime:
	return datetime(
		dt_obj.year,
		dt_obj.month,
		dt_obj.day
	)

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
		get_dt:bool=False,
		date_min:Optional[datetime]=None,
		date_max:Optional[datetime]=None,
		fullres:bool=False,
	)->Optional[Union[str,datetime,tuple]]:

	if not isinstance(dt_string,str):
		return None

	if len(dt_string)==0:
		return None

	the_format=""
	parts=len(dt_string.split("-"))
	if parts==2:
		the_format=_FMT_DATE_YM
	if parts==3:
		the_format=_FMT_DATE_YMD
	if parts==4:
		the_format=_FMT_DATE_YMDH
	if parts==5:
		the_format=_FMT_DATE_YMDHM
	if parts==6:
		the_format=_FMT_DATE_YMDHMS

	dtobj:Optional[datetime]=None
	try:
		dtobj=datetime.strptime(
			dt_string,
			the_format
		)
	except Exception as exc:
		print("date parsing error:",exc)
		if get_dt:
			return None
		return None

	if isinstance(date_min,datetime):
		if dtobj<date_min:
			if fullres:
				return dt_string,False
			return None

	if isinstance(date_max,datetime):
		if dtobj>date_max:
			if fullres:
				return dt_string,False
			return None

	if fullres:
		return dt_string,True

	if get_dt:
		return dtobj

	return dt_string

def util_dt_to_str(dtobj:Optional[datetime])->str:

	if dtobj is None:
		return None

	return (
		f"{dtobj.year}-"
		f"{str(dtobj.month).zfill(2)}-"
		f"{str(dtobj.day).zfill(2)}-"
		f"{str(dtobj.hour).zfill(2)}-"
		f"{str(dtobj.minute).zfill(2)}-"
		f"{str(dtobj.second).zfill(2)}"
	)

def util_rnow(level=4)->str:
	now=datetime.now().utcnow()
	t=f"{now.year}"
	t=f"{t}-{str(now.month).zfill(2)}"
	t=f"{t}-{str(now.day).zfill(2)}"
	if level>1:
		t=f"{t}-{str(now.hour).zfill(2)}"
	if level>2:
		t=f"{t}-{str(now.minute).zfill(2)}"
	if level>3:
		t=f"{t}-{str(now.second).zfill(2)}"

	return t

def util_date_in_date(
		date:datetime,
		date_day:datetime
	)->bool:

	if not date.day==date_day.day:
		return False
	if not date.month==date_day.month:
		return False
	if not date.year==date_day.year:
		return False
	return True

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

def util_valid_int_ext(
		data:Optional[Union[str,int]],
		fallback:Optional[int]=None,
		minimum:Optional[bool]=None,
		maximum:Optional[bool]=None,
	)->Optional[int]:

	value=util_valid_int(data)
	if not isinstance(value,int):
		return fallback

	chk_min=isinstance(minimum,int)
	chk_max=isinstance(maximum,int)

	if chk_max and chk_min:
		if value in range(chk_min,chk_max+1):
			return value

	if chk_max and (not chk_min):
		if value<chk_max+1:
			return value

	if (not chk_max) and chk_min:
		if value>chk_min:
			return value

	return fallback

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

def read_yaml_file(
		filepath:Path,
		kfil:Optional[str]=None
	)->dict:

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

	if isinstance(kfil,str):

		if not isinstance(
				data.get(kfil),
				Mapping
			):
			return {}

		return data.pop(kfil)

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

def write_yaml_file(
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

# sorting

# class Node:
# 	def __init__(self,data:Mapping):
# 		self.data=data
# 		self.side_left:Optional[Mapping]=None
# 		self.side_right:Optional[Mapping]=None

# if __name__=="__main__":

# 	for i in range(0,33):
# 		print(i,util_excel_dectocol(i))
