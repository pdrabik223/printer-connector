# printer-connector

Handles connecting to different printers


Hameg driovers : **https://www.rohde-schwarz.com/cz/driver/hmp/**
also 


# TODO

## GUI

### PLOTS

- [ ] **improve highlight**, it should represent current position of en extruder.
- [ ] **improve plots**, they should not be redrawn from scratch every time
- [x] **make color-bar work**
- [ ] **improve measurements plot** by utilizing position to value mapping

### PRINTER CONTROL

- [x] **printer controlling buttons should work**
- [x] **add antenna zeroing-script**

### UX DESIGN

- [ ] **add tool pop-up** after measurement cycle is done
- [x] **add path generator options** additional pop-pup window would be grand with some
  user should be able to precisely set the measurement range
- [x] **better looking buttons** custom css for those, colors should be picked from system setting
  maybe some dark mode, but this one can be hard sometimes

## ANALYZER DEVICE

- [ ] **Investigate faster measurement performing**
- [ ] **connected devices** scanner, that detects all devices connected to the pc

## PRINTER DEVICE

- [ ] **improve send and await** it should estimate time needed for completion of requested movement
- [ ] **connected devices** scanner, that detects all devices connected to the pc
