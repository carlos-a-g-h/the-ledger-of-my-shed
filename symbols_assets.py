#!/usr/bin/python3.9

_ROUTE_PAGE="/page/assets"

_SQL_FILE_ASSETS="assets.cache"
_SQL_TABLE_ASSETS="Assets"

_FILE_ASSETS="assets.db"

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

_ID_ASSETS_TO_SPREADSHEET="assets-to-spreadsheet"

_ID_NEW_ASSET="new-asset"
_ID_NEW_ASSET_FORM="new-asset-form"

_ID_ASSETS_SEARCH="assets-search"
_ID_ASSETS_SEARCH_FORM="assets-search-form"
_ID_ASSETS_SEARCH_RESULT="assets-search-result"

_ID_ASSET_EMATCH="asset-ematch"
_ID_ASSET_EMATCH_FORM="asset-ematch-form"

_ID_ASSET_EDITOR="asset-editor"
_ID_ASSET_EDITOR_FORM="asset-editor-form"

_ID_ASSET_HISTORY="asset-history"
_ID_ASSET_HISTORY_FORM="asset-history-form"
_ID_ASSET_HISTORY_RECORDS="asset-history-records"

_ID_ASSET_INFO="asset-info"
_ID_ASSET_SUPPLY="asset-supply"

_CSS_CLASS_ITEM_ASSET="item-asset"

def html_id_asset(asset_id:str)->str:

	return f"asset-{asset_id}"

