meta:
  id: roh
  file-extension: roh
  endian: le
seq:
  - id: header
    type: header
  - id: payload
    type: payload
types:
  header:
    seq:
      - id: rawheader
        type: u2
        repeat: expr
        repeat-expr: 44
  payload:
    seq:
      - id: spectrum
        type: f4
        repeat: expr
        repeat-expr: 1000
