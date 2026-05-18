*&---------------------------------------------------------------------*
*& Function Group: Z_FG_EXAMPLE
*&---------------------------------------------------------------------*
FUNCTION z_get_customer.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(IV_KUNNR) TYPE KUNNR
*"  EXPORTING
*"     VALUE(EV_NAME)  TYPE NAME1
*"  TABLES
*"      ET_RETURN STRUCTURE BAPIRET2
*"----------------------------------------------------------------------

  DATA: lv_kunnr TYPE kunnr,
        lv_name  TYPE name1.

  SELECT SINGLE name1 FROM kna1
    INTO @lv_name
    WHERE kunnnr = @iv_kunnr.

  CALL FUNCTION 'BAPI_CUSTOMER_GETDETAIL'
    EXPORTING
      customerno = iv_kunnr
    IMPORTING
      customername = ev_name
    TABLES
      return = et_return[].

  INSERT INTO zcust_log VALUES ls_log.

ENDFUNCTION.

FUNCTION z_create_order.
  DATA: lv_order TYPE vbeln.

  CALL FUNCTION 'BAPI_SALESORDER_CREATE'
    EXPORTING
      order_header_in = ls_header
    IMPORTING
      salesdocument = lv_order.

  DELETE FROM ztemp_orders WHERE order_id = lv_order.

ENDFUNCTION.
