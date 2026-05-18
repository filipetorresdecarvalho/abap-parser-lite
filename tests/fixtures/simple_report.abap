REPORT z_simple_report.

* Top include
INCLUDE z_simple_report_top.

* Data declarations
DATA: lv_matnr TYPE matnr,
      lv_werks TYPE werks_d,
      lv_name  TYPE c LENGTH 40.

* Full line comment example
DATA lv_counter TYPE i.

START-OF-SELECTION.

  PERFORM get_data USING lv_matnr.

  CALL FUNCTION 'Z_READ_MATERIAL'
    EXPORTING
      iv_matnr = lv_matnr.

  SELECT * FROM mara INTO TABLE @DATA(lt_mara).
  MODIFY ztable FROM ls_record.

  " This is an inline comment example.
  WRITE: / lv_name.

* Fetch plant data
FORM get_data USING iv_matnr.
  SELECT SINGLE * FROM mara WHERE matnr = @iv_matnr.
ENDFORM.

FORM process_data USING iv_werks.
  UPDATE zplant SET status = 'A'.
ENDFORM.
