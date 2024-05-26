#!/usr/bin/python3.9

import asyncio
from typing import Optional,Union

_table=[
	("663","Item no 1"),
	("55g","Other thing"),
	("jj8","test Thing")
]

def table_display():
	for row in _table:
		print(row)

def table_find_id_using_text_in_row(text:str,row:tuple)->Optional[str]:

	row_text=row[1].strip().lower()
	if row_text.find(text)==-1:
		return None

	return row[0]

def table_find_id_using_text(text:str)->list:
	text_ok=text.strip().lower()
	if len(text_ok)<4:
		return []

	matches=[]
	for row in _table:
		res=table_find_id_using_text_in_row(text_ok,row)
		if not isinstance(res,str):
			continue
		matches.append(res)

	return matches

async def myloop():
	return [1,2,3,4,5]

async def main():
	async for item in myloop():
		print(item)

if __name__=="__main__":

	import asyncio

	asyncio.run(
		main()
	)

	#from sys import argv as sys_argv
	#from sys import exit as sys_exit

	#if len(sys_argv)==1:
	#	table_display()
	#	sys_exit(0)

	#print(
	#	table_find_id_using_text(
	#		sys_argv[1]
	#	)
	#)
