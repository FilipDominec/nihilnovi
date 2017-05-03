meta:
  id: roh
  file-extension: roh
  endian: le
seq:
  - id: header
    type: header
types:
  header:
    seq:
      - id: unknown1
        type: f4
      - id: wlintercept
        type: f4
      - id: wlx1
        type: f4
      - id: wlx2
        type: f4
      - id: wlx3
        type: f4
      - id: wlx4
        type: f4
      - id: unknown2
        type: f4
        repeat: expr
        repeat-expr: 9
      - id: ipixfirst
        type: f4
      - id: ipixlast
        type: f4
      - id: unknown3
        type: f4
        repeat: expr
        repeat-expr: 4
      - id: spectrum
        type: f4
        repeat: expr
        repeat-expr: ipixlast.to_i - ipixfirst.to_i - 1
      - id: unknown4
        type: f4
        repeat: expr
        repeat-expr: 3
