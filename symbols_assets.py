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

_KEY_INC_HISTORY="include_history"
_KEY_INC_SUPPLY="include_supply"
_KEY_INC_VALUE="include_value"

_ID_LAYOUT_ASSETS_SEARCH="layout-assets-search"

_ID_FORM_ASSETS_TO_SPREADSHEET="form-assets-to-spreadsheet"
_ID_FORM_NEW_ASSET="form-new-asset"
_ID_RESULT_NEW_ASSET="result-new-asset"
_ID_FORM_SEARCH_ASSETS="form-search-assets"
_ID_RESULT_SEARCH_ASSETS="result-search-assets"
_ID_FORM_ASSET_EMATCH="form-asset-ematch"

_ID_FORM_ASSET_EDITOR="form-asset-editor"
_ID_FORM_ASSET_HISTORY="form-asset-history"
_ID_ASSET_HISTORY="asset-history"
_ID_ASSET_INFO="asset-info"
_ID_ASSET_SUPPLY="asset-supply"

_CSS_CLASS_ITEM_ASSET="item-asset"

def html_id_asset(asset_id:str)->str:

	return f"asset-{asset_id}"

