#!/usr/bin/python3.9

_ROUTE_PAGE="/page/orders"

_COL_ORDERS="orders"
_KEY_ORDER="order_id"
_KEY_ORDER_VALUE="order_value"
_KEY_ORDER_IS_FLIPPED="order_is_flipped"

_KEY_LOCKED_BY="locked_by"

_KEY_ORDER_KEEP="order-keep"
_KEY_ORDER_DROP="order-drop"
_KEY_ALGSUM="algsum"
_KEY_COPY_VALUE="copy-value"

_ID_FORM_NEW_ORDER="form-new-order"
_ID_RESULT_NEW_ORDER="result-new-order"

_ID_LAYOUT_ASSETS_SEARCH="layout-assets-search"

_ID_ALL_ORDERS="all-orders"
_ID_ORDER_ASSET_TOOLS="order-asset-tools"
_ID_FORM_ADD_ASSET_BNQ="form-asset-to-order-bnq"
_ID_FORM_RUN_OR_REVERT_ORDER="form-run-or-revert-order"
_ID_ORDER_ASSETS="order-assets"

_ID_FORM_RUN_OR_REV_ORDERS="form-run-or-rev-orders"

_CSS_CLASS_ITEM_ORDER="item-order"

_ID_ORDER_DASHBOARD="order-dashboard"
_ID_ORDER_INFO="order-info"
_ID_ORDER_VALUE="order-value"
# _CSS_CLASS_ORDER_INFO="order-info"

def html_id_order(
		order_id:str,
		info:bool=False,
		value:bool=False,
		assets:bool=False
	)->str:

	html_text=f"order-{order_id}"
	if info:
		return f"{html_text}-info"
	if value:
		return f"{html_text}-value"
	if assets:
		return f"{html_text}-assets"
	return html_text

def html_id_order_asset(asset_id:str,info:bool=False)->str:
	html_text=f"order-asset-{asset_id}"
	if info:
		html_text=f"{html_text}-info"
	return html_text
