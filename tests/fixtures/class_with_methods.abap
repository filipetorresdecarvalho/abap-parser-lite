CLASS zcl_handler DEFINITION PUBLIC.
  PUBLIC SECTION.
    METHODS: constructor,
             process_data IMPORTING iv_id TYPE i,
             cleanup.
ENDCLASS.

CLASS zcl_handler IMPLEMENTATION.

  METHOD constructor.
    DATA: lv_init TYPE abap_bool.
    lv_init = abap_true.
    " Initialize handler
    WRITE: / 'Handler initialized'.
  ENDMETHOD.

  METHOD process_data.
    DATA: lv_result TYPE i.

    SELECT * FROM zdata INTO TABLE @DATA(lt_data).
    CALL FUNCTION 'Z_PROCESS_ENTRY'
      EXPORTING
        iv_id = iv_id.

    DELETE FROM zcache WHERE id = iv_id.
  ENDMETHOD.

  METHOD cleanup.
    MODIFY zstatus SET active = abap_false.
    " Cleanup complete
  ENDMETHOD.

ENDCLASS.
