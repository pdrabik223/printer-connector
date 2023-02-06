// USE to compile mkoctfile  -v -Wl,/home/mntmnt/Projects/projectadc/device-api/libPocketVnaApi_x64.so pocketvna-octave.cc
#include <octave/oct.h>
#include <octave/ov-struct.h>
#include <octave/parse.h>
#include <octave/dRowVector.h>
#include <octave/Range.h>
#include <octave/uint64NDArray.h>
#include <octave/CNDArray.h>
#include <octave/CRowVector.h>

#include <string>

#include "pocketvna.h"

std::string res2str(PVNA_Res r) {
    return pocketvna_result_string(r);
}

octave_value_list driverVersion() {
  uint16_t version = 0.;
  double info      = 0.;
  PVNA_Res r = pocketvna_driver_version(&version, &info);

  if ( r != PVNA_Res_Ok ) {
     octave_stdout << "\n=========================\npocketvna_driver_version returned non-OK result\n";
  }

  octave_scalar_map st;

  st.assign ("VERSION",  version);
  st.assign ("PI",       info);

  return octave_value (st);
}

octave_value_list listDevices() {
     PVNA_DeviceDesc * list = 0;
     uint16_t sz = 0;
     PVNA_Res r = pocketvna_list_devices(&list, &sz);

     octave_value_list retval;

     if ( r != PVNA_Res_Ok && r != PVNA_Res_NoDevice ) {
        octave_stdout << "driver_version returned non-OK status: " << res2str(r) << "\n";

        return retval;
     }     

     if ( r == PVNA_Res_NoDevice )  {
        octave_stdout << "\nThere is No device available\n";
        return retval;
     }

     retval.resize (sz);

     for ( size_t i = 0; i < sz; ++i ) {
         octave_scalar_map st;
         std::wstring sn = list[i].serial_number; 
         std::wstring ven= list[i].manufacturer_string;
         std::wstring nm = list[i].product_string;
         st.assign ("index",      i);
         st.assign ("path",       list[i].path);
         st.assign ("SN",         std::string(sn.begin(), sn.end()) );
         st.assign ("vendor",     std::string(ven.begin(),ven.end()) );
         st.assign ("name",       std::string(nm.begin(), nm.end()) );
         st.assign ("version",    list[i].release_number);
         st.assign ("permissions",list[i].access);
         st.assign ("VID",        list[i].vid );
         st.assign ("PID",        list[i].pid );

         retval(i) = st;
     }

     pocketvna_free_list(&list);

     return retval;
}
const auto ResultField = "RESULT";
const auto ErrorMsgField = "error";
const auto DeviceHandlerField = "DEVICE_HANDLE";

octave_value openDevice(const octave_scalar_map & mp) {
//    const int index       = mp.getfield("index").int_value();
    const std::string pth = mp.getfield("path").string_value();
    std::string tmp = mp.getfield("SN").string_value();
    const std::wstring sn(tmp.begin(), tmp.end());

    tmp = mp.getfield("vendor").string_value();
    const std::wstring vendor(tmp.begin(), tmp.end());
    tmp = mp.getfield("name").string_value();
    const std::wstring  name(tmp.begin(), tmp.end());

    const uint16_t vers = mp.getfield("version").uint_value();

    const uint16_t vid  = mp.getfield("VID").uint_value();
    const uint16_t pid  = mp.getfield("PID").uint_value();

    PVNA_DeviceDesc desc;
    desc.path = pth.c_str();
    desc.manufacturer_string = vendor.c_str();
    desc.pid = pid;
    desc.vid = vid;
    desc.product_string = name.c_str();
    desc.release_number = vers;
    desc.serial_number  = sn.c_str();
    desc.next= 0;

    PVNA_DeviceHandler handle;
    PVNA_Res r = pocketvna_get_device_handle_for(&desc, &handle);

    octave_scalar_map st;

    st.assign (ResultField,    r == PVNA_Res_Ok);
    st.assign (ErrorMsgField,  r == PVNA_Res_Ok ? "OK" : "FAILED");
    st.assign ("RESULT_EXPLAIN",    "not implemented yet");
    st.assign (DeviceHandlerField,     (uint64_t)handle);

    return octave_value(st);
}

octave_value deviceVersion( const octave_value & l ) {
    static_assert(sizeof(PVNA_DeviceHandler) <= sizeof(uint64_t), "SHOULD be compatible with uint64");

    PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(l.uint64_value());
    uint16_t ver = 0;

    PVNA_Res r = pocketvna_version(handle, &ver);
    
    octave_scalar_map st;

    if ( r != PVNA_Res_Ok ) {
        octave_stdout << "Getting version failed: " << res2str(r) << "\n";        
        st.assign (ResultField, false);
        return octave_value(st);
    }

    st.assign (ResultField, true);
    st.assign ("VERSION",    ver);

    return octave_value(st);
}

octave_value closeDevice( const octave_value & l ) {
    PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(l.uint64_value());

    PVNA_Res r = pocketvna_release_handle(&handle);
    if ( r != PVNA_Res_Ok ) {
        octave_stdout << "Closing device failed: " << res2str(r) << "\n";
        return octave_value(false);
    }

    return octave_value(true);
}

octave_value getSettings(const octave_value & l ) {
    PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(l.uint64_value());

    octave_scalar_map st;
    st.assign("RESULT", false);

    octave_value_list retval;
    retval.resize(4);

    //PVNA_Res_InvalidHandle;PVNA_Res_Ok;PVNA_Res_UnsupportedTransmission

    // S11?
    PVNA_Res r = pocketvna_is_transmission_supported(handle, PVNA_S11);
    if ( r == PVNA_Res_InvalidHandle ) {
        octave_stdout << "Handler is invalid\n";
        st.assign("error", "Handler is invalid");
        return octave_value(st);
    }

    if ( r == PVNA_Res_Ok ) retval = retval.append(11);

    // S21?
    r = pocketvna_is_transmission_supported(handle, PVNA_S21);
    if ( r == PVNA_Res_InvalidHandle ) {
        octave_stdout << "Handler is invalid\n";
        st.assign("error", "Handler is invalid");
        return octave_value(st);
    }
    if ( r == PVNA_Res_Ok ) retval = retval.append(21);

    // S12?
    r = pocketvna_is_transmission_supported(handle, PVNA_S12);
    if ( r == PVNA_Res_InvalidHandle ) {
        octave_stdout << "Handler is invalid\n";
        st.assign("error", "Handler is invalid");
        return octave_value(st);
    }
    if ( r == PVNA_Res_Ok ) retval = retval.append(12);

    // S22?
    r = pocketvna_is_transmission_supported(handle, PVNA_S22);
    if ( r == PVNA_Res_InvalidHandle ) {
        octave_stdout << "Handler is invalid\n";
        st.assign("error", "Handler is invalid");
        return octave_value(st);
    }
    if ( r == PVNA_Res_Ok ) retval = retval.append(22);

    //--------------------------------------------------


    double z0 = 0.;
    r = pocketvna_get_characteristic_impedance(handle, &z0);
    if ( r == PVNA_Res_InvalidHandle ) {
        octave_stdout << "Handler is invalid\n";
        st.assign("error", "Handler is invalid");
        return octave_value(st);
    }
    if ( r != PVNA_Res_Ok ) {
        octave_stdout << "Failed to get Z0 (Characteristic Impedance): " << res2str(r) << "\n";

        st.assign("error", "z0 is failed is invalid");
        return octave_value(st);
    }

    PVNA_Frequency valid_from = 0, valid_to = 0;
    r = pocketvna_get_valid_frequency_range(handle, &valid_from, &valid_to);
    if ( r == PVNA_Res_InvalidHandle ) {
        octave_stdout << "Handler is invalid\n";
        st.assign("error", "Handler is invalid");
        return octave_value(st);
    }
    if ( r != PVNA_Res_Ok ) {
        octave_stdout << "Failed to get Valid frequency range: " << res2str(r) << "\n";
        st.assign("error", "valid frequency is failed");
        return octave_value(st);
    }


    PVNA_Frequency rsnbl_from = 0, rsnbl_to = 0;
    r = pocketvna_get_reasonable_frequency_range(handle, &rsnbl_from, &rsnbl_to);
    if ( r == PVNA_Res_InvalidHandle ) {
        octave_stdout << "Handler is invalid\n";
        st.assign("error", "Handler is invalid");
        return octave_value(st);
    }

    if ( r != PVNA_Res_Ok ) {
        octave_stdout << "Failed to get Reasonable frequency range: " << res2str(r) << "\n";
        st.assign("error", "reasonable frequency is failed");
        return octave_value(st);
    }


    RowVector vld;
    vld.resize(2);
    vld(0) = (valid_from);
    vld(1) = (valid_to);

    RowVector rsnbl;
    rsnbl.resize(2);
    rsnbl(0) = (rsnbl_from);
    rsnbl(1) = (rsnbl_to);

    st.assign("RESULT", true);
    st.assign("MODES", retval);
    st.assign("VALID_FREQUENCY", vld);
    st.assign("REASONABLE_FREQUENCY", rsnbl);
    st.assign("Z0", z0);

    return octave_value( st );
}

octave_value isConnectionValid(const octave_value & l) {
     PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(l.uint64_value());

     if (! handle ) return octave_value(false);

     PVNA_Res r = pocketvna_is_valid(handle);

     return octave_value(r == PVNA_Res_Ok);
}


octave_value scanData(const octave_value  & hc,
                      const NDArray & freq,
                      const unsigned avg) {

     PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(hc.uint64_value());

     if (! handle ) {
         octave_stdout << "bad handle\n";
         return octave_value(ComplexNDArray res(dim_vector(0, 2, 2)));
     }

     int length = freq.length();

     std::vector<uint64_t> fa(length, 0);
     for ( int i = 0; i < length; ++i ) {
         fa[i] = freq.elem(i, 0, 0);
     }

     size_t sz = fa.size();

     std::vector<PVNA_Sparam> s11(sz, {0., .0}), s21(sz, {0., .0}),
                              s12(sz, {0., .0}), s22(sz, {0., .0});

     PVNA_Res r = pocketvna_multi_query( handle, fa.data(), sz, avg,
                            (PVNA_NetworkParam)(PVNA_S11|PVNA_S21|PVNA_S12|PVNA_S22),
                            &s11[0], &s21[0],
                            &s12[0], &s22[0], NULL );

     if ( r != PVNA_Res_Ok ) {
        octave_stdout << "scan error: " << res2str(r) << "\n";
        return octave_value(ComplexNDArray res(dim_vector(0, 2, 2)));
     }

     octave_idx_type szi = sz;
     ComplexNDArray res(dim_vector(szi, 2, 2));

     for ( size_t i = 0; i < sz; ++i ) {
         res(i, 0, 0) = std::complex<double>(s11[i].real, s11[i].imag);
         res(i, 1, 0) = std::complex<double>(s21[i].real, s21[i].imag);
         res(i, 0, 1) = std::complex<double>(s12[i].real, s12[i].imag);
         res(i, 1, 1) = std::complex<double>(s22[i].real, s22[i].imag);
     }

     return octave_value(res);
}

octave_value enterDFUMode(const octave_value & hc) {
    PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(hc.uint64_value());

    if (! handle ) {
        octave_stdout << "bad handle\n";
        return octave_value(false);
    }

    PVNA_Res r = pocketvna_enter_dfu_mode(handle);

    if ( r != PVNA_Res_Ok ) {
        octave_stdout << "ERROR entering DFU: " << res2str(r) << "\n";
        return octave_value(false);
    }

    octave_stdout << "Entered into DFU Mode. Your handle is not valid anymore. "
                  << "Use dfu-programm command or flip software to update firmware\n";
    return true;
}

DEFUN_DLD (pocketvna_octave, args, , "'Interrogate'  pocketVNA device.\n"
                                     "\t driver_version -- driver version\n"
                                     "\t list    -- enumerate available devices\n"
                                     "\t open    -- opens device by its description received by 'list'. Returns a handle\n"
                                     "\t version -- device version, accepts handle\n"
                                     "\t close   -- closes device by handle\n"
                                     "\t settings-- returns hashmap with device settings like frequency range, Z0, supported modes. Accepts handle \n"
                                     "\t valid?  -- checks whether a handle is valid\n"
                                     "\t scan    -- accepts handle, frequency (range or vector) and Average factor. Returns array of 2x2 matrices\n"
                                     "\t DFU     -- turns a device into Device Firmware Update mode. Ex >> pocketvna_octave(\"DFU!\", handle); # => true/false\n"
                                     "") {
  if ( args.length() > 0 && args(0).is_string() ) {
       std::string fcn = args(0).string_value ();

       if ( fcn == "driver_version" ) {
           return driverVersion();
       } else if ( fcn == "list" ) {
           return listDevices();
       } else if ( fcn == "open" ) {
           return openDevice(args(1).scalar_map_value());
       } else if ( fcn == "version" ) {
           return deviceVersion(args(1));
       } else if ( fcn == "close" ) {
           return closeDevice(args(1));
       } else if ( fcn == "settings" ) {
           //pocketvna_get_characteristic_impedance
           //pocketvna_get_valid_frequency_range
           //pocketvna_get_reasonable_frequency_range
           return getSettings(args(1));
       } else if ( fcn == "valid?" ) {
           return isConnectionValid(args(1));
       } else if ( fcn == "scan" ) {
           octave_value h  = args(1);
           NDArray f  = args(2).array_value();
           unsigned avg= args(3).uint_value();

           if ( f.dim2() > f.dim1() ) f = f.transpose();

           return scanData(h, f, avg);
       } else if ( fcn == "DFU!" ) {
           return enterDFUMode(args(1));
       }
  }

  print_usage();

  return octave_value(false);
}

