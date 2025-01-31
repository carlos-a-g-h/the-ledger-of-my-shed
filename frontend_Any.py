#!/usr/bin/python3.9

from asyncio import to_thread as async_run_blk
from pathlib import Path
from typing import Any,Optional,Union

from symbols_Any import (
	_LANG_EN,_LANG_ES,
	_ONE_MB,
	_DIR_TEMP,
	_DIR_SOURCES,
)

_ID_NAVIGATION="navigation"
_ID_MAIN="main"
_ID_MAIN_MENU="main-menu"
_ID_MAIN_ONE="main-1"
_ID_MAIN_TWO="main-2"
_ID_NAV_ONE="nav-1"
_ID_NAV_ONE_OPTS="nav-1-opts"
_ID_NAV_TWO="nav-2"
_ID_NAV_TWO_OPTS="nav-2-opts"
_ID_MESSAGES="messages"

_CSS_CLASS_TITLE_UNIQUE="title-uniq"
_CSS_CLASS_TITLE="title"

_CSS_CLASS_NAV="nav"
_CSS_CLASS_CONTAINER="container"
_CSS_CLASS_CONTENT="content"

_CSS_CLASS_IG_CHECKBOXES="ig-checkboxes"
_CSS_CLASS_IG_FIELDS="ig-fields"

_CSS_CLASS_ASSET_HISTORY="asset-history"

_CSS_CLASS_ANCHOR_AS_BUTTON="anchor-as-button"

_CSS_CLASS_INPUT_CHECKBOX="input-checkbox"
_CSS_CLASS_INPUT_RADIO="input-radio"
_CSS_CLASS_INPUT_FIELD="input-field"
_CSS_CLASS_INPUT_TEXTBOX="input-textbox"
_CSS_CLASS_INPUT_GUARDED="input-guarded"

_CSS_CLASS_COMMON="common"
_CSS_CLASS_HORIZONTAL="horizontal"
_CSS_CLASS_CONTROLS="controls"
_CSS_CLASS_VER="vertical"
# _CSS_CLASS_VDOWN="vertical-2"

_CSS_CLASS_ASSET_IN_ORDER="asset-in-order"

_CSS_CLASS_BTN_MENU="main-menu-button"

_CSS_CLASS_DANGER="danger"
_CSS_CLASS_FOCUSED="focused"

_SCRIPT_HTMX="""<script src="/src/local/htmx.min.js"></script>"""
_SCRIPT_HYPERSCRIPT="""<script src="/src/local/hyperscript.js"></script>"""

_STYLE_CUSTOM="""<link rel="stylesheet" href="/src/special/custom.css">"""
# _STYLE_CUSTOM="""<link rel="stylesheet" href="/src/local/custom.css">"""
# _STYLE_POPUP="""<link rel="stylesheet" href="/src/baked/popup.css">"""

_STYLE_TALIGN_R="text-align:right;"

_DETAILS={
	_LANG_EN:"Details",
	_LANG_ES:"Detalles"
}

# CSS functions

def write_link_stylesheet(filename:str)->str:
	return f"""<link rel="stylesheet" href="/src/styles/{filename}">"""

def util_css_gather(path_base:Path)->list:

	path_sources:Path=path_base.joinpath(_DIR_SOURCES)
	if not path_sources.is_dir():
		return []

	detected=list(path_sources.glob("*.css"))
	detected.sort()

	styles=[]

	for fse in detected:
		if not fse.is_file():
			continue
		if not fse.stat().st_size<_ONE_MB:
			continue
		styles.append(
			write_link_stylesheet(
				fse.name
			)
		)

	return styles

def util_css_bake(
		path_base:Path,
		confirm_only:bool=False
	)->Union[bool,Optional[Path]]:

	path_sources:Path=path_base.joinpath(_DIR_SOURCES)
	if not path_sources.is_dir():
		if confirm_only:
			return False
		return None

	fse_new=path_base.joinpath(
		_DIR_TEMP
	).joinpath(
		"custom.css"
	)
	fse_new.parent.mkdir(exist_ok=True,parents=True)

	print("\nWriting custom.css...")


	detected=list(path_sources.glob("*.css"))
	detected.sort()

	with open(fse_new,"wt") as target:

		for fse in detected:
			if "*" in fse.name:
				continue

			if not fse.is_file():
				continue

			if not fse.stat().st_size<_ONE_MB:
				continue

			try:
				target.write(
					f"/* |{fse.name}| */\n"
					f"{fse.read_text()}\n"
				)
			except Exception as exc:
				print(
					f"Baking failed on file:\n\t{fse}\n"
					f"\tReason: {exc}"
				)
				continue

			print("\tAdding to custom.css:",fse.name)

	if confirm_only:
		return True

	return fse_new

async def util_css_pull(path_base:Path)->Optional[Path]:

	path_file:Optional[Path]=path_base.joinpath(
		_DIR_TEMP
	).joinpath(
		"custom.css"
	)

	if not path_file.is_file():
		path_file=await async_run_blk(
			util_css_bake,
			path_base
		)
		if not isinstance(path_file,Path):
			return None

	if not path_file.is_file():
		return None

	return path_file

# Components... ?

def write_button_submit(
		label:str,
		classes:bool=[
			_CSS_CLASS_COMMON
		],
		hxinc=""
	)->str:

	attr_class=""
	if not len(classes)==0:
		for c in classes:
			attr_class=f"{attr_class} {c}"

		attr_class=f"""class="{attr_class.strip()}" """

	attr_hxinc=""
	if not len(hxinc)==0:
		attr_hxinc=f"""hx-include="{hxinc}" """

	return (
		f"""<button {attr_class}{attr_hxinc}type=submit>"""
			f"{label}"
		"</button>"
	)

def write_html_input_checkbox(
		name:str,label:str,
		checked:bool=False,
		full:bool=True
	)->str:

	# Input checkbox with a label next to it

	tl=""
	if checked:
		tl="checked"

	html_text=(
		f"""<input name="{name}" type=checkbox {tl}>""" "\n"
		f"""<label for="{name}" class="{_CSS_CLASS_COMMON}">{label}</label>"""
	)

	if full:
		html_text=(
			f"""<div class="{_CSS_CLASS_INPUT_CHECKBOX}">""" "\n"
				f"{html_text}\n"
			"</div>"
		)

	return html_text

def write_html_input_radio(
		name:str,
		options:list=[("value","Label")],
		check:int=0
	)->str:

	# Pairs: Tubple( value , label )

	html_text=f"""<div class="{_CSS_CLASS_INPUT_RADIO}">"""

	check_ok=check
	if check_ok<0:
		check_ok=0

	count=-1

	for pair in options:

		count=count+1

		tail=""
		if (count==check_ok):
			tail="checked"

		value,label=pair

		unique_id=f"{name}-radio-{count}"
		html_text=(
			f"{html_text}\n"

			"<div>\n"
				f"""<input type=radio id="{unique_id}" """
					f"""name="{name}" """
					f"""value="{value}" """
					f"{tail}>\n"

				f"""<label for="{unique_id}">{label}</label>""" "\n"
			"</div>"
		)

	html_text=(
			f"{html_text}\n"
		"</div>"
	)

	return html_text

def write_html_input_string(
		name:str,label:Optional[str]=None,
		value:Optional[str]=None,
		input_type:int=0,
		maxlen:int=64,
		required:bool=False,
	)->str:

	# A label next to an input (single line) text box

	tl="text"
	if input_type==1:
		tl="email"
	html_text=(
		f"""<input class="{_CSS_CLASS_COMMON}" """
			f"""name="{name}" """
			f"""type="{tl}" """
	)
	if value is not None:
		html_text=(
			f"{html_text}"
				f"""value="{value}" """
		)
	if maxlen>0:
		html_text=(
			f"{html_text}"
				f"""max-length={maxlen} """
		)
	if required:
		html_text=f"{html_text} required"

	html_text=f"{html_text}>"

	if not isinstance(label,str):
		return html_text

	html_text=(
		f"""<div class="{_CSS_CLASS_INPUT_FIELD}">""" "\n"
			f"""<label for="{name}" class="{_CSS_CLASS_COMMON}">{label}</label>""" "\n"
			f"{html_text}\n"
		"</div>"
	)

	return html_text

def write_html_input_number(
		name:str,label:Optional[str]=None,
		value:Optional[int]=None,
		minimum:Optional[int]=None,
		maximum:Optional[int]=None,
		required:bool=False,
	)->str:

	# A label next to an input for a number

	html_text=(
		f"""<input class="{_CSS_CLASS_COMMON}" """
			f"""name="{name}" """
			f"""type="number" """
	)
	if value is not None:
		html_text=(
			f"{html_text}"
				f"value={value} "
		)

	if minimum is not None:
		html_text=(
			f"{html_text}"
				f"min={minimum} "
		)
	if maximum is not None:
		html_text=(
			f"{html_text}"
				f"max={maximum} "
		)
	if required:
		html_text=f"{html_text} required"

	html_text=f"{html_text}>"

	if not isinstance(label,str):
		return html_text

	html_text=(
		f"""<div class="{_CSS_CLASS_INPUT_FIELD}">""" "\n"
			f"""<label for="{name}" class="{_CSS_CLASS_COMMON}">{label}</label>""" "\n"
			f"{html_text}\n"
		"</div>"
	)

	return html_text

def write_html_input_textbox(
		name:str,label:Optional[str]=None,
		maxlen:int=256,
	)->str:

	html_text=(
		f"""<textarea class="{_CSS_CLASS_COMMON}" """
			f"""name="{name}" """
	)
	if maxlen>0:
		html_text=(
			f"{html_text}"
				f"""max-length={maxlen} """
		)
	html_text=f"{html_text}></textarea>"

	if not isinstance(label,str):
		return html_text

	html_text=(
		f"""<div class="{_CSS_CLASS_INPUT_TEXTBOX}">""" "\n"
			f"""<label for="{name}" class="{_CSS_CLASS_COMMON}">{label}</label>""" "\n"
			f"{html_text}\n"
		"</div>"
	)

	return html_text

def write_button_anchor(
		label:str,link:str,
		classes:list=[],
		disabled:bool=False,
	)->str:

	classes_str=""
	for the_class in classes:
		classes_str=f"{classes_str} {the_class}"

	tag_end=""
	if disabled:
		tag_end=" disabled"

	return (
		f"""<button class="{classes_str.strip()}" """
			f"""onclick="location.href='{link}'" """
			f"{tag_end}>"
	
			f"{label}"

		"</button>\n"
	)

def write_html_nav_pages(lang:str,current:int=-1)->str:

	# 3, 2, 1, 0

	pages=[
		(
			{
			_LANG_EN:"Configuration",
			_LANG_ES:"Configuración"
			}[lang],"/page/admin"),
		(
			{
			_LANG_EN:"Account",
			_LANG_ES:"Cuenta"
			}[lang],"/page/accounts"),
		(
			{
			_LANG_EN:"Orders",
			_LANG_ES:"Órdenes"
			}[lang],"/page/orders"),
		(
			{
			_LANG_EN:"Assets",
			_LANG_ES:"Activos"
			}[lang],"/page/assets"),
	]

	the_buttons=[]
	disable_a_page=(current>-1)
	while True:
		if len(pages)==0:
			break

		page_name,link=pages.pop()

		disabled=False
		if disable_a_page:
			disabled=(
				len(the_buttons)==current
			)

		the_buttons.append(
			write_button_anchor(
				page_name,link,
				classes=[_CSS_CLASS_NAV],
				disabled=disabled
			)
		)

	return write_ul(
		the_buttons,
		ul_id=_ID_NAV_ONE_OPTS,
		ul_classes=[_CSS_CLASS_NAV]
	)


def write_link_homepage(lang:str)->str:

	tl={
		_LANG_EN:"Homepage",
		_LANG_ES:"Pág. principal"
	}[lang]

	return write_button_anchor(tl,"/")

def write_popupmsg_closemsg(okbtn:bool=False)->str:

	classes="popup-button"
	if not okbtn:
		classes=f"{classes} danger"

	label={
		True:"OK",
		False:"×"
	}[okbtn]

	return (
		"""<button class="popup-button" """
			"""onclick="document.getElementById('messages').children[0].outerHTML='<\!-- MESSAGE BOX CLOSED -->'">""" "\n"
				f"{label}\n"
		"""</button>"""
	)

def write_popupmsg(html_content:str)->str:
	return (
		"""<div class="popup-background">""" "\n"
			"""<div class="popup-area">""" "\n"
				"""<div class="popup-body">""" "\n"
					"""<div class="popup-content">""" "\n"
						f"{html_content}\n"
					"</div>\n"
					f"""<div class="popup-button-area">""" "\n"
						f"{write_popupmsg_closemsg(True)}\n"
						# """<button class="popup-button" onclick="this.parentElement.parentElement.parentElement.parentElement.style.display='none';">""" "\n"
						# "<!-- × -->"
							# "<strong>OK</strong>"
						# "</button>\n"
					"</div>\n"
				"</div>\n"
			"</div>\n"
		"</div>"
	)

def write_fullpage(
		lang:str,
		html_title:str,
		html_body_inner:str,
		html_header_extra:list=[],
	)->str:

	html_page=(
		"<!DOCTYPE html>\n"
			f"""<html lang="{lang}">""" "\n"
				"<head>\n"
					"""<meta charset="UTF-8" />""" "\n"
						"""<meta name="viewport" content="width=device-width,initial-scale=1.0" />""" "\n"
	)

	for thing in html_header_extra:
		html_page=f"{html_page}\n{thing}"

	return (
					f"{html_page}\n"
				f"<title>{html_title}</title>\n"
			"</head>\n"
			"<body>\n"
				f"{html_body_inner}\n"
			"</body>\n"
		"</html>"
	)

def write_ul(
		list_of_things:list,
		ul_id:Optional[str]=None,
		ul_classes:list=[],
		full:bool=True,
	)->str:

	if len(list_of_things)==0:
		return ""

	html_text=""
	for thing in list_of_things:
		html_text=(
			f"{html_text}\n"
			"<li>\n"
				f"{thing}\n"
			"</li>\n"
		)

	if full:

		tl_id=""
		if ul_id is not None:
			tl_id=f"""id="{ul_id}" """

		tl_classes=""
		if not len(ul_classes)==0:
			for c in ul_classes:
				tl_classes=f"{tl_classes} {c}"

		tl_classes=f"""class="{tl_classes.strip()}" """

		html_text=(
			f"<ul {tl_id} {tl_classes}>\n"
				f"{html_text}\n"
			"</ul>"
		)

	return html_text

def write_div_display_error(lang:str,data:Optional[Any]=None)->str:

	tl={
		_LANG_EN:"Display error",
		_LANG_ES:"Error al mostrar"
	}[lang]
	html_text=(
		"<div>\n"
			f"<div>{tl}:</div>"
	)
	if data is not None:
		html_text=(
			f"{html_text}\n"
			f"<pre>{data}</pre>"
		)

	return (
			f"{html_text}\n"
		"</div>"
	)
