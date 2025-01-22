#!/usr/bin/python3.9

_ROUTE_PAGE="/page/assets"

_COL_ASSETS="assets"

_KEY_NAME="name"
_KEY_ASSET="asset_id"
_KEY_SUPPLY="supply"
_KEY_VALUE="value"

_KEY_HISTORY="history"
_KEY_RECORD_UID="record_id"
_KEY_RECORD_MOD="mod"

_ID_FORM_AE="form-asset-editor"

_ID_FORM_NEW_ASSET="form-new-asset"
_ID_RESULT_NEW_ASSET="result-new-asset"

_ID_FORM_SEARCH_ASSETS="form-search-assets"
_ID_RESULT_SEARCH_ASSETS="result-search-assets"

def html_id_asset(
		asset_id:str,
		suply:bool=False,
		info:bool=False,
		editor:bool=False,
		controls:bool=False,
		history:bool=False,
	)->str:

	html_text=f"asset-{asset_id}"

	if suply:
		return f"{html_text}-suply"
	if info:
		return f"{html_text}-info"
	if editor:
		return f"{html_text}-editor"

	if history and controls:
		return f"{html_text}-history-controls"
	if history:
		return f"{html_text}-history"
	if controls:
		return f"{html_text}-controls"

	return html_text
