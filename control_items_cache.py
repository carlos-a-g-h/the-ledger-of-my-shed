#!/usr/bin/python3.9

from typing import Any,Mapping,Optional,Union

from internals import util_valid_str
from aiohttp.web import Application
from dbi import dbi_inv_ItemQuery

_CACHE_ITEMS="cache_items"

def util_items_cache_name_lookup(
		app:Application,
		text_raw:str,
		find_exact_only:bool=False,
	)->Union[list,Mapping]:

	text=text_raw.lower().strip()
	if len(text)==0:
		return []

	lookup_result:Union[list,Mapping]={
		True:{},
		False:[]
	}[find_exact_only]

	for item_id in app[_CACHE_ITEMS]:
		item_name=app[_CACHE_ITEMS][item_id]
		row=item_name.lower().strip()
		if row.find(text)<0:
			continue

		exact=(row==text)

		if find_exact_only:
			if exact:
				lookup_result.update({
					"id":item_id,
					"name":item_name,
				})
				break

			continue

		lookup_result.append(
			{
				"id":item_id,
				"name":item_name,
				"exact":exact,
			}
		)

	return lookup_result

def util_convert_item_to_kv(
		data:Optional[Any]
	)->Mapping:

	if not isinstance(data,Mapping):
		return {}

	item_id=util_valid_str(
		data.get("id")
	)
	if not isinstance(item_id,str):
		return {}

	item_name=util_valid_str(
		data.get("name")
	)
	if not isinstance(item_name,str):
		return {}

	return {item_id:item_name}

async def init(app:Application):

	dbi_result=await dbi_inv_ItemQuery(
		app["rdbc"],app["rdbn"]
	)

	size=len(dbi_result)

	while True:
		size=size-1
		if size<0:
			break

		app[_CACHE_ITEMS].update(
			util_convert_item_to_kv(
				dbi_result.pop()
			)
		)