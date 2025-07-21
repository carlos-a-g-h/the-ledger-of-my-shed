#!/usr/bin/python3.9

from asyncio import to_thread

from pickle import (
	dumps as pckl_encode,
	loads as pckl_decode
)
from pathlib import Path

from aiosqlite import (
	connect as aiosql_connect,
	Connection,Cursor
)

from typing import Any,Awaitable,Callable,Mapping,Optional,Union

from pysqlitekv import (

	_PAGE_DEFAULT,
	_SQL_TAB_ITEMS,
	_SQL_COL_KEY,
	_SQL_COL_TYPE,
	_SQL_COL_VALUE_STR,
	_SQL_COL_VALUE_INT,
	_SQL_COL_VALUE_BLOB,

	_SQL_TX_BEGIN,
	_SQL_TX_COMMIT,
	_SQL_TX_ROLLBACK,

	_SORT_LOW_TO_HI,
	_SORT_NONE,
	_SORT_HI_TO_LOW,

	_TYPE_NONE,
	_TYPE_BOOL,
	_TYPE_STRING,
	_TYPE_INT,
	_TYPE_LIST,
	_TYPE_HASHMAP,
	_TYPE_ANY,

	_TARGET_ONE,
	_TARGET_SLICE,

	# util_is_cur,

	util_fmatch,
	util_dtype_check,
	util_extract_correct_value,

	# util_get_dtype_col_from_dtype_id,
	util_get_dtype_from_value,
	util_extract_from_target_tuple,

	util_bquery_init,
	util_bquery_insert,
	util_bquery_select,
	util_bparams,
)

_RUN_NORMAL=0
_RUN_AWAITABLE=1
_RUN_TOTHREAD=2

async def data_decode(data:bytes)->Any:
	decoded=await to_thread(
		pckl_decode(data)
	)
	return decoded

async def data_encode(data:Any)->bytes:
	encoded=await to_thread(
		pckl_encode(data)
	)
	return encoded

# Init and connection functions

async def db_init(
		filepath:Path,
		new_pages:Union[int,list]=_PAGE_DEFAULT,
		confirm_only:bool=False,
		verbose:bool=False
	)->Union[bool,Connection]:

	the_pages=[]
	if isinstance(new_pages,int):
		the_pages.append(new_pages)

	if isinstance(new_pages,list):
		for p in new_pages:
			if not isinstance(p,int):
				continue
			the_pages.append(p)

	if len(the_pages)==0:
		the_pages.append(_PAGE_DEFAULT)

	con:Connection=await aiosql_connect(filepath)
	cur:Cursor=await con.cursor()
	await cur.execute(_SQL_TX_BEGIN)
	for p in the_pages:
		await cur.execute(
			util_bquery_init(
				page=p,
				show=verbose
			)
		)

	await cur.execute(_SQL_TX_COMMIT)
	await cur.close()

	if confirm_only:
		await con.close()
		return True

	if verbose:
		print(f"{db_init.__name__} new page(s):",the_pages)

	return con

async def db_getcon(filepath:Path)->Connection:

	return (
		await aiosql_connect(filepath)
	)

async def db_getcur(
		con_or_cur:Union[Connection,Cursor],
		begin_transaction:bool=False,
		verbose:bool=False
	)->Cursor:

	if isinstance(con_or_cur,Cursor):
		if begin_transaction:
			if verbose:
				print(
					db_getcur.__name__,
					"begginning transaction in the given cursor"
				)

			await con_or_cur.execute(_SQL_TX_BEGIN)

		return con_or_cur

	if verbose:
		print(
			db_getcur.__name__,
			"creating a new cursor from the given connection"
		)

	cur:Cursor=await con_or_cur.cursor()
	if begin_transaction:
		if verbose:
			print(
				db_getcur.__name__,
				"begginning transaction in the new cursor"
			)
		await cur.execute(_SQL_TX_BEGIN)

	return cur

# Not sure if I should let this exist or let the end devs shoot themselves in the foot

# async def db_check_changes(
# 		con_or_cur:Union[Connection,Cursor],
# 		verbose:bool=False
# 	)->bool:

# 	has_changes=False

# 	if isinstance(con_or_cur,Connection):

# 		has_changes=(con_or_cur.in_transaction)
# 		if verbose:
# 			print("In transaction?",has_changes)

# 	if isinstance(con_or_cur,Cursor):

# 		await con_or_cur.execute("SELECT changes()")
# 		print("CHANGES: {")
# 		qtty=0
# 		async for row in con_or_cur:
# 			print(row)
# 			qtty=qtty+1

# 		print("} pending changes =",qtty)

# 		has_changes=(not qtty==0)
# 		if verbose:
# 			print("Has changes?",has_changes,qtty)

# 	return has_changes

# Main/Data functions

async def db_post(
		con_or_cur:Union[Connection,Cursor],
		key_name:str,value:Any,
		page:int=_PAGE_DEFAULT,
		force:bool=False,
		verbose:bool=False,
	)->bool:

	dtype=util_get_dtype_from_value(value)
	if dtype==_TYPE_NONE:
		if verbose:
			print(
				f"{db_post.__name__}",
				"data type not valid"
			)

		return False

	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)

	key_ready=key_name.strip().lower()
	params:Optional[tuple]=await to_thread(
		util_bparams,
		key_ready,value,
		dtype
	)
	if params is None:
		if verbose:
			print(
				f"{db_post.__name__}",
				"unable to build params"
			)

		return False

	if isolated:
		await cur.execute(_SQL_TX_BEGIN)

	await cur.execute(
		util_bquery_insert(
			replace=force,
			page=page
		),
		params
	)

	if isolated:
		await cur.execute(_SQL_TX_COMMIT)
		await cur.close()

	if verbose:
		print(
			f"{db_post.__name__}[{page}][{key_ready}]",
			"<--",value
		)

	return True

async def db_get(
		con_or_cur:Union[Connection,Cursor],
		key_name:str,
		page:int=_PAGE_DEFAULT,
		get_type_only:bool=False,
		restrict_type:Optional[int]=None,
		display_results:bool=False,
		verbose:bool=True
	)->Optional[Any]:

	# OK

	key_ready=key_name.strip().lower()
	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)
	await cur.execute(
		util_bquery_select(
			keyname=key_ready,
			page=page
		)
	)
	select_result=await cur.fetchone()

	if isolated:
		await cur.close()

	if select_result is None:
		if verbose:
			print(
				f"{db_get.__name__}[{page}][{key_ready}]",
				"not found",
			)

		return None

	the_value=await to_thread(
		util_extract_correct_value,
		select_result
	)
	if the_value is None:
		if verbose:
			print(
				f"{db_get.__name__}[{page}][{key_ready}]",
				f"not found in {select_result} ?"
			)

		return None

	if util_dtype_check(restrict_type):
		dtype=util_get_dtype_from_value(the_value)
		if not dtype==restrict_type:
			if get_type_only:
				return _TYPE_NONE

			return None

	if get_type_only:
		dtype=util_get_dtype_from_value(the_value)
		if display_results:
			print(
				f"{db_get.__name__}[{page}][{key_ready}]",
				"-->",dtype
			)
		return dtype

	if display_results:
		print(
			f"{db_get.__name__}[{page}][{key_ready}]",
			"-->",the_value
		)
	return the_value

async def db_delete(
		con_or_cur:Union[Connection,Cursor],
		key_name:str,
		page:int=_PAGE_DEFAULT,
		return_val:bool=False,
		verbose:bool=False
	)->Union[bool,Optional[Any]]:

	key_ready=key_name.strip().lower()
	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)

	if isolated:
		await cur.execute(_SQL_TX_BEGIN)

	if return_val:

		await cur.execute(
			util_bquery_select(
				keyname=key_ready,
				page=page
			)
		)

	if not return_val:

		await cur.execute(
			f"SELECT {_SQL_COL_KEY} FROM {_SQL_TAB_ITEMS}_{page} "
				f"""WHERE {_SQL_COL_KEY}="{key_ready}" """
		)

	result=await cur.fetchone()
	if result is None:
		if verbose:
			print(
				f"{db_delete.__name__}[{page}][{key_ready}]",
				"not found",
			)
		if isolated:
			await cur.execute(_SQL_TX_ROLLBACK)
			await cur.close()
		if return_val:
			return None
		return False

	value:Optional[Any]=None

	if return_val:

		value=await to_thread(
			util_extract_correct_value,
			result
		)
		if value is None:
			if verbose:
				print(
					f"{db_delete.__name__}[{page}][{key_ready}]",
					f"not found in {result} ?"
				)
			if isolated:
				await cur.execute(_SQL_TX_ROLLBACK)
				await cur.close()

			return None

	await cur.execute(
		f"DELETE FROM {_SQL_TAB_ITEMS}_{page} "
			f"""WHERE {_SQL_COL_KEY}="{key_ready}" """
	)
	if isolated:
		await cur.execute(_SQL_TX_COMMIT)
		await cur.close()

	if return_val:
		return value

	return True

async def db_lpost(
		con_or_cur:Union[Connection,Cursor],
		key_name:str,value:Any,
		page:int=_PAGE_DEFAULT,
		force:bool=False,
		verbose:bool=False,
	)->bool:

	is_list=(isinstance(value,list))

	key_ready=key_name.strip().lower()
	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)

	await cur.execute(
		f"SELECT {_SQL_COL_TYPE},{_SQL_COL_VALUE_BLOB} "
			f"FROM {_SQL_TAB_ITEMS}_{page} "
				f"""WHERE {_SQL_COL_KEY}="{key_ready}" """
					f"""AND ({_SQL_COL_TYPE}={_TYPE_STRING} OR {_SQL_COL_TYPE}>{_TYPE_STRING}) """
					f"""AND ({_SQL_COL_TYPE}={_TYPE_ANY} OR {_SQL_COL_TYPE}<{_TYPE_ANY});"""
	)
	result=await cur.fetchone()

	if result is not None:

		if not force:

			if not result[0]==_TYPE_LIST:
				await cur.close()
				return False

			the_thing=await data_decode(result[1])

			if not is_list:
				the_thing.append(value)
			if is_list:
				the_thing.extend(value)

			if isolated:
				await cur.execute(_SQL_TX_BEGIN)

			the_query=(
				f"UPDATE {_SQL_TAB_ITEMS}_{page} "
					f"SET {_SQL_COL_VALUE_BLOB}=? "
					f"WHERE {_SQL_COL_KEY}=? "
			)
			await cur.execute(
				the_query.strip(),
				(
					pckl_encode(the_thing),
					key_ready
				)
			)
			if isolated:
				await cur.execute(_SQL_TX_COMMIT)
				await cur.close()

			if verbose:
				print(
					f"{db_lpost.__name__}[{page}][{key_ready}]",
					"<--",value
				)
			return True

	value_ok=[]
	if not is_list:
		value_ok.append(value)
	if is_list:
		value_ok.extend(value)

	if isolated:
		await cur.execute(_SQL_TX_BEGIN)

	the_params=await to_thread(
		util_bparams,
		key_ready,
		value_ok,
		_TYPE_LIST
	)

	await cur.execute(
		util_bquery_insert(
			replace=force,
			page=page
		),
		the_params
		# util_bparams(key_ready,value_ok,_TYPE_LIST)
	)
	if isolated:
		await cur.execute(_SQL_TX_COMMIT)
		await cur.close()

	if verbose:
		print(
			f"{db_lpost.__name__}[{page}][{key_ready}]",
			"-->",value_ok
		)

	return True

async def db_lget(
		con_or_cur:Union[Connection,Cursor],
		key_name:str,target:Union[int,tuple],
		page:int=_PAGE_DEFAULT,
		display_results:bool=False,
		verbose:bool=False,
	)->Union[list,Optional[Any]]:

	key_ready=key_name.strip().lower()

	target_ok=util_extract_from_target_tuple(target,for_lists=True)
	if target_ok is None:
		if display_results or verbose:
			print(
				f"{db_delete.__name__}[{key_ready}][{target}]",
				"the target is not valid"
			)

		if isinstance(target,tuple):
			return []

		return None

	select_one=(target_ok[0]==_TARGET_ONE)

	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)

	query=(
		util_bquery_select(
			keyname=key_ready,
			datatype=_TYPE_LIST,
			page=page
		)
	)
	await cur.execute(query)
	result=await cur.fetchone()
	if result is None:
		if verbose:
			print(
				db_lget.__name__,
				f"{key_ready} not found"
			)
		if isolated:
			await cur.close()
		if not select_one:
			return []
		return None

	the_thing:list=await data_decode(result[0])

	size=len(the_thing)
	last_idx=size-1

	if select_one:

		idx=target_ok[1]

		if not idx<0:

			if idx>last_idx:
				if display_results:
					print(
						f"{db_lget.__name__}[{key_ready}][{idx}]",
						"is beyond the last index"
					)
				return None

			if display_results:
				print(
					f"{db_lget.__name__}[{key_ready}][{idx}] =",
					the_thing[idx]
				)
				return None

			return the_thing[idx]

		idx_ok=size+idx
		if idx_ok<0:
			return None

		if display_results:
			print(
				f"{db_lget.__name__}[{key_ready}][{idx}] =",
				the_thing[idx]
			)
			return None

		return the_thing[idx_ok]

	idx_min_ok=target_ok[1]
	idx_max_ok=target_ok[2]
	idx_min=target_ok[3]
	idx_max=target_ok[4]

	if not idx_min_ok:
		idx_min=0
	if not idx_max_ok:
		idx_max=last_idx

	if idx_min_ok:
		if idx_min>last_idx:
			if verbose:
				print(
					f"{db_lget.__name__}[{key_ready}][{(idx_min,idx_max)}]",
					"the min is above last index"
				)
			return []

	if idx_max_ok:
		if idx_max>last_idx:
			idx_max=size-1

	if display_results:
		print(
			f"{db_lget.__name__}[{key_ready}][{idx_min} to {idx_max}] =",
			the_thing[idx_min:idx_max+1]
		)

	return the_thing[idx_min:idx_max+1]

async def db_ldelete(
		con_or_cur:Union[Connection,Cursor],
		key_name:str,
		target:Union[int,tuple],
		page:int=_PAGE_DEFAULT,
		return_val:bool=False,
		verbose:bool=False,
	)->Union[bool,list,Optional[Any]]:

	key_ready=key_name.strip().lower()

	target_ok=util_extract_from_target_tuple(target,for_lists=True)
	if target_ok is None:
		if verbose:
			print(
				f"{db_delete.__name__}[{key_ready}][{target}]",
				"the given target is not valid"
			)

		if return_val:
			return False

		return None

	select_one=(target_ok[0]==_TARGET_ONE)
	select_slice=(target_ok[0]==_TARGET_SLICE)

	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)
	await cur.execute(
		util_bquery_select(
			keyname=key_ready,
			datatype=_TYPE_LIST,
			page=page
		)
	)

	result=await cur.fetchone()
	if result is None:
		if verbose:
			print(
				f"{db_ldelete.__name__}[{key_ready}]",
				"not found"
			)
		if isolated:
			await cur.close()
		if return_val:
			if not select_one:
				return []
			return None
		return False

	the_thing:list=await data_decode(result[0])

	size=len(the_thing)
	if size==0:
		if verbose:
			print(
				f"{db_ldelete.__name__}[{key_ready}]",
				"is empty"
			)
		if isolated:
			await cur.close()
		if return_val:
			if not select_one:
				return []
			return None
		return False

	last_idx=size-1

	values=[]

	if select_one:

		target_idx=target_ok[1]

		if not target_idx<0:
			if target_idx>last_idx:
				if return_val:
					return None
				return False

			if return_val:
				return the_thing.pop(target_idx)

			the_thing.pop(target_idx)
			return True

		idx_ok=size+target_idx
		if idx_ok<0:
			if verbose:
				print(
					f"{db_ldelete.__name__}[{key_ready}][{target_idx}]",
					"does not exist"
				)
			if return_val:
				return None
			return False

		if return_val:
			values.append(
				the_thing.pop(idx_ok)
			)
		if not return_val:
			the_thing.pop(idx_ok)

	if select_slice:

		idx_min_ok=target_ok[1]
		idx_max_ok=target_ok[2]
		idx_min=target_ok[3]
		idx_max=target_ok[4]

		if not idx_min_ok:
			idx_min=0
		if not idx_max_ok:
			idx_max=last_idx

		if idx_min_ok:
			if idx_min>last_idx:
				if verbose:
					print(
						f"{db_ldelete.__name__}[{key_ready}][{(idx_min,idx_max)}]",
						"the min is above last index"
					)
				if return_val:
					return []
				return False

		if idx_max_ok:
			if idx_max>last_idx:
				idx_max=size-1

		idx=idx_min
		targets=idx_max-idx_min

		while True:
			if idx>size-1:
				break

			if targets==0:
				break

			if return_val:
				values.append(
					the_thing.pop(idx)
				)
			if not return_val:
				the_thing.pop(idx)

			size=size-1
			targets=targets-1

	if isolated:
		await cur.execute(_SQL_TX_BEGIN)

	the_query=(
		f"UPDATE {_SQL_TAB_ITEMS}_{page} "
			f"SET {_SQL_COL_VALUE_BLOB}=? "
			f"WHERE {_SQL_COL_KEY}=? "
	)

	encoded_value=await data_encode(the_thing)

	await cur.execute(
		the_query.strip(),
		(
			# pckl_encode(the_thing),
			encoded_value,
			key_ready
		)
	)

	if isolated:
		await cur.execute(_SQL_TX_COMMIT)
		await cur.close()

	if return_val:
		if select_slice:
			return values
		if select_one:
			return values.pop()

	return True

async def db_hupdate(
		con_or_cur:Union[Connection,Cursor],
		key_name:str,
		data_to_add:Mapping={},
		data_to_remove:list=[],
		force:bool=False,
		page:int=_PAGE_DEFAULT,
		return_val:bool=False,
		verbose:bool=False,
	)->Union[bool,Mapping]:

	has_stuff_to_add=(len(data_to_add)>0)
	has_stuff_to_remove=(len(data_to_remove)>0)

	if not (has_stuff_to_add or has_stuff_to_remove):
		if return_val:
			return {}

		return False

	key_ready=key_name.strip().lower()

	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)
	await cur.execute(
		util_bquery_select(
			keyname=key_ready,
			datatype=_TYPE_HASHMAP,
			page=page
		)
	)
	result=await cur.fetchone()

	if result is not None:

		if not force:

			the_thing:Mapping=await data_decode(result[0])

			removed_data:Mapping={}

			if has_stuff_to_remove:
				for target in data_to_remove:
					if target not in the_thing.keys():
						continue
					removed_data.update(
						{target:the_thing.pop(target)}
					)

			if has_stuff_to_add:
				the_thing.update(data_to_add)

			if isolated:
				await cur.execute(_SQL_TX_BEGIN)

			the_query=(
				f"UPDATE {_SQL_TAB_ITEMS}_{page} "
					f"SET {_SQL_COL_VALUE_BLOB}=? "
					f"WHERE {_SQL_COL_KEY}=? "
			)
			encoded=await data_encode(the_thing)
			await cur.execute(
				the_query.strip(),
				(
					# pckl_encode(the_thing),
					encoded,
					key_ready
				)
			)

			if isolated:
				await cur.execute(_SQL_TX_COMMIT)
				await cur.close()

			if return_val:
				return removed_data

			return True

	the_params=await to_thread(
		util_bparams,
		key_ready,
		data_to_add,
		_TYPE_HASHMAP
	)

	await cur.execute(
		util_bquery_insert(
			replace=force,
			show=verbose
		),
		the_params
		# util_bparams(
		# 	key_ready,data_to_add,
		# 	_TYPE_HASHMAP
		# )
	)
	if isolated:
		await cur.execute(_SQL_TX_COMMIT)
		await cur.close()

	return True

async def db_hget(
		con_or_cur:Union[Connection,Cursor],
		key_name:str,
		subkeys:list=[],
		aon:bool=False,
		page:int=_PAGE_DEFAULT,
		display_results:bool=False,
		verbose:bool=False,
	)->Mapping:

	if len(subkeys)==0:
		return {}

	key_ready=key_name.strip().lower()
	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)

	await cur.execute(
		util_bquery_select(
			keyname=key_ready,
			datatype=_TYPE_HASHMAP,
			page=page
		)
	)
	result=await cur.fetchone()
	if result is None:
		if verbose:
			print(
				f"{db_hget.__name__}[{key_ready}]",
				"not found"
			)
		if isolated:
			cur.close()

		return {}

	the_thing:Mapping=await data_decode(result[0])

	selection={}
	failed=False

	for item in subkeys:

		if failed:
			break

		if isinstance(item,str):
			if item not in the_thing.keys():
				if aon:
					failed=True
				continue
			selection.update(
				{item:the_thing.pop(item)}
			)

		if isinstance(item,tuple):
			if len(item)==2:
				if item[0] not in the_thing.keys():
					if aon:
						failed=True
						continue
				if not the_thing[item[0]]==item[1]:
					if aon:
						failed=True
						continue
				selection.update(
					{item[0]:the_thing.pop(item[0])}
				)

	if failed:
		if not len(selection)==0:
			selection.clear()

	if display_results:
		print(
			f"{db_hget.__name__}[{key_ready}]{subkeys} =",
			selection
		)
		return {}

	return selection

async def db_custom(
		con_or_cur:Union[Connection,Cursor],
		key_name:str,
		custom_func:Union[Callable,Awaitable],
		custom_func_params:Optional[Any]=None,
		custom_func_runtype:int=_RUN_NORMAL,
		page:int=_PAGE_DEFAULT,
		res_write:bool=False,
		res_return:bool=False,
		verbose:bool=False,
		display_result:bool=False,
	)->Union[bool,Optional[Any]]:

	if custom_func_runtype not in (
			_RUN_NORMAL,
			_RUN_AWAITABLE,
			_RUN_TOTHREAD
		):
		return None

	key_ready=key_name.strip().lower()
	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)

	await cur.execute(
		util_bquery_select(
			keyname=key_ready,
			page=page
		)
	)

	select_result=await cur.fetchone()
	if select_result is None:
		if verbose:
			print(
				f"{db_custom.__name__}[{key_ready}]",
				"Not found"
			)
		if isolated:
			await cur.close()

		return None

	the_value=await to_thread(
		util_extract_correct_value,
		select_result
	)
	if the_value is None:
		if verbose:
			print(
				f"{db_custom.__name__}[{key_ready}]",
				"the extracted value is corrupt"
			)
		if isolated:
			await cur.close()

		return None

	if isolated and res_write:
		await cur.execute(_SQL_TX_BEGIN)

	func_result:Optional[Any]=None
	has_args=(custom_func_params is not None)

	if custom_func_runtype==_RUN_NORMAL:
		if has_args:
			func_result=custom_func(
				the_value,
				custom_func_params
			)
		if not has_args:
			func_result=custom_func(the_value)

	if custom_func_runtype==_RUN_AWAITABLE:
		if has_args:
			func_result=await custom_func(
				the_value,
				custom_func_params
			)
		if not has_args:
			func_result=await custom_func(the_value)

	if custom_func_runtype==_RUN_TOTHREAD:
		if has_args:
			func_result=await to_thread(
				custom_func,
				the_value,custom_func_params
			)
		if not has_args:
			func_result=await to_thread(
				custom_func,
				the_value,
			)

	return_write_conf=(
		(res_write is True) and
		(res_return is False)
	)

	if display_result:
		print(
			f"{db_custom.__name__}[{page}]",
			f"{custom_func.__name__}({custom_func_params})",
			func_result
		)

	write_back=(
		res_write and
		(func_result is not None)
	)

	if write_back:

		dtype_new=util_get_dtype_from_value(func_result)

		exe_params:Optional[tuple]=await to_thread(
			util_bparams,
			key_ready,
			func_result,
			dtype_new
		)
		await cur.execute(
			util_bquery_insert(replace=True,page=page),
			exe_params
		)

		if isolated:
			await cur.execute(_SQL_TX_COMMIT)
			await cur.close()

		if return_write_conf:
			return True

	if not write_back:

		if return_write_conf:
			return False

	if res_return:
		return func_result

	return None


async def db_len(
		con_or_cur:Union[Connection,Cursor],
		key_name:str,
		page:int=_PAGE_DEFAULT
	)->int:

	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)

	key_ready=key_name.strip().lower()

	await cur.execute(
		f"SELECT {_SQL_COL_TYPE} FROM {_SQL_TAB_ITEMS}_{page} "
			f"""WHERE {_SQL_COL_KEY}="{key_ready}" """
	)
	result=await cur.fetchone()
	if result is None:
		if isolated:
			await cur.close()
		return -1

	if result[0] not in (_TYPE_LIST,_TYPE_HASHMAP):
		if isolated:
			await cur.close()
		return -1

	await cur.execute(
		f"SELECT {_SQL_COL_VALUE_BLOB} FROM {_SQL_TAB_ITEMS}_{page} "
			f"""WHERE {_SQL_COL_KEY}="{key_ready}" """
	)
	result=await cur.fetchone()
	if result is None:
		if isolated:
			await cur.close()
		return -1

	decoded=await data_decode(result[0])

	size=len(decoded)

	if isolated:
		await cur.close()

	return size

async def db_keys(
		con_or_cur:Union[Connection,Cursor],
		page:int=_PAGE_DEFAULT,
		qtty_only:bool=False,
		limit:int=0,
		display_results:bool=False,
	)->list:

	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)

	list_keys=[]
	qtty=0

	await cur.execute(
		f"SELECT {_SQL_COL_KEY} "
			f"FROM {_SQL_TAB_ITEMS}_{page} "
			f"""WHERE ({_SQL_COL_TYPE}={_TYPE_BOOL} OR {_SQL_COL_TYPE}>{_TYPE_BOOL}) """
			f"""AND ({_SQL_COL_TYPE}={_TYPE_ANY} OR {_SQL_COL_TYPE}<{_TYPE_ANY});"""
	)
	async for row in cur:
		if not isinstance(row,tuple):
			continue
		if not len(row)==1:
			continue
		if not qtty_only:
			list_keys.append(row[0])
		qtty=qtty+1
		if limit>0:
			if qtty==limit or qtty>limit:
				break
	if isolated:
		await cur.close()

	if display_results:
		print(
			f"{db_keys.__name__}",
			qtty,list_keys
		)

	if qtty_only:
		return qtty

	return list_keys

async def db_fz_str(
		con_or_cur:Union[Connection,Cursor],
		substring:str,
		starts_with:bool=False,
		page:int=_PAGE_DEFAULT,
		display_results:bool=False,
	)->list:

	text_ok=substring.strip()

	matches=[]
	matches_exact=[]
	matches_perfect=[]

	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)

	await cur.execute(
		f"SELECT {_SQL_COL_KEY},{_SQL_COL_VALUE_STR} "
			f"FROM {_SQL_TAB_ITEMS}_{page} "
				f"WHERE {_SQL_COL_TYPE}={_TYPE_STRING}"
	)

	for row in cur:
		res=util_fmatch(
			text_ok,
			row[1],
			starts_with
		)
		if res==0:
			continue

		if res==1:
			matches.append(row)

		if res==2:
			matches_exact.append(row)

		if res==3:
			matches_perfect.append(row)

	if isolated:
		await cur.close()

	final_list=[]

	size=len(matches_perfect)
	if not size==0:
		while True:
			final_list.append(
				matches_perfect.pop()
			)
			size=size-1
			if size==0:
				break

	size=len(matches_exact)
	if not size==0:
		while True:
			final_list.append(
				matches_exact.pop()
			)
			size=size-1
			if size==0:
				break

	size=len(matches)
	if not size==0:
		while True:
			final_list.append(
				matches.pop()
			)
			size=size-1
			if size==0:
				break

	if display_results:
		print(
			db_fz_str.__name__,
			text_ok,
			final_list
		)

	return final_list

async def db_fz_num(
		con_or_cur:Union[Connection,Cursor],
		target:Union[int,tuple],
		page:int=_PAGE_DEFAULT,
		sort_results:int=_SORT_NONE,
		display_results:bool=False
	)->Optional[list]:

	target_ok=util_extract_from_target_tuple(target)
	if target_ok is None:
		if isinstance(target,tuple):
			return []

		return None

	select_one=(target_ok[0]==_TARGET_ONE)
	select_slice=(target_ok[0]==_TARGET_SLICE)

	query=(
		f"SELECT {_SQL_COL_KEY},{_SQL_COL_VALUE_INT} "
			f"FROM {_SQL_TAB_ITEMS}_{page} "
				f"WHERE {_SQL_COL_TYPE}={_TYPE_INT}"
	)
	if select_one:
		query=f"{query} AND {_SQL_COL_VALUE_INT}={target_ok[1]}"

	if select_slice:

		idx_min_ok=target_ok[1]
		idx_max_ok=target_ok[2]
		idx_min=target_ok[3]
		idx_max=target_ok[4]

		if idx_min_ok:
			query=(
				f"{query} AND ("
					f"{_SQL_COL_VALUE_INT}={idx_min} OR "
					f"{_SQL_COL_VALUE_INT}>{idx_min}"
				")"
			)

		if idx_max_ok:
			query=(
				f"{query} AND ("
					f"{_SQL_COL_VALUE_INT}={idx_max} OR "
					f"{_SQL_COL_VALUE_INT}<{idx_max}"
				")"
			)

	if sort_results in (_SORT_LOW_TO_HI,_SORT_HI_TO_LOW):
		query=f"{query} ORDER BY {_SQL_COL_VALUE_INT}"
		if sort_results==_SORT_LOW_TO_HI:
			query=f"{query} ASC"
		if sort_results==_SORT_HI_TO_LOW:
			query=f"{query} DESC"

	isolated=isinstance(con_or_cur,Connection)
	cur=await db_getcur(con_or_cur)
	await cur.execute(query.strip())

	if display_results:
		print(
			db_fz_num.__name__,
			f"[{target}]"
		)
		for row in cur:
			print(f"\t{row}")

		return None

	results=await cur.fetchall()

	if isolated:
		await cur.close()

	return results

# Transaction functions

async def db_tx_begin(
		cur:Cursor,
		verbose:bool=False
	)->bool:

	# ok=await db_check_changes(cur,verbose=verbose)
	# if not ok:
	# 	return False

	if verbose:
		print(
			db_tx_begin.__name__,
			"begginning transaction"
		)

	await cur.execute(_SQL_TX_BEGIN)

	return True

async def db_tx_commit(
		cur:Cursor,
		close_cursor:bool=False,
		verbose:bool=False
	)->bool:

	# ok=await db_check_changes(cur,verbose=verbose)
	# if not ok:
	# 	return False

	if verbose:
		print(
			db_tx_commit.__name__,
			"committing changes"
		)

	await cur.execute(_SQL_TX_COMMIT)
	if close_cursor:
		if verbose:
			print(
				db_tx_commit.__name__,
				"closing cursor after committing"
			)
		await cur.close()

	return True

async def db_tx_rollback(
		cur:Cursor,
		close_cursor:bool=False,
		verbose:bool=False
	)->bool:

	# ok=await db_check_changes(cur,verbose=verbose)
	# if not ok:
	# 	return False

	if verbose:
		print(
			db_tx_rollback.__name__,
			"rolling back"
		)

	await cur.execute(_SQL_TX_ROLLBACK)
	if close_cursor:
		if verbose:
			print(
				db_tx_rollback.__name__,
				"closing after rolling back..."
			)
		await cur.close()

	return True
