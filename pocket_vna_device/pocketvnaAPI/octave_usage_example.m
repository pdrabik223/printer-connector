clear pocketvna_octave

res = pocketvna_octave("list");
if length(res) > 0
    printf("Devices: ");
    disp(res)
else
    printf("No Device connected");
    return;
end

device = pocketvna_octave("open", res(1));
if device.RESULT
    printf("DEVICE CONNECTED\n");
else
    printf("CAN NOT OPEN DEVICE");
    return;
end

handle = device.DEVICE_HANDLE;

devver = pocketvna_octave("version",  handle);
if devver.RESULT
   printf("DEVICE VERSION: 0x%x\n", devver.VERSION);
else
   printf("Getting Device version is failed\n")
   return;   
end

settings = pocketvna_octave("settings", handle);
if settings.RESULT
   printf("VALID FREQUENCY RANGE: [%f; %f]\n",      settings.VALID_FREQUENCY(1),      settings.VALID_FREQUENCY(2));
   printf("REASONABLE FREQUENCY RANGE: [%f; %f]\n", settings.REASONABLE_FREQUENCY(1), settings.REASONABLE_FREQUENCY(2));
   printf("ALLOWED MODES: \n", settings.MODES);
else
   printf("settings failed");
   return;
end

is_valid = pocketvna_octave("valid?", handle);
if is_valid
   printf("Connection is valid\n");
else 
   printf("Connection is INVALID\n");
   return;
end

freq = 100000:100005;
freq2=[100000, 2000000, 4000000000];
net  = pocketvna_octave("scan", handle, freq, 10);
if net != false
    printf("NETWORK IS SCANNED\n");
    disp(net);
else
    printf("Network scan failed");
endif

xxx= pocketvna_octave("close", handle);
