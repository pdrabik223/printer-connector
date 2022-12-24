from printer_connector.anycubic_s_device import AnycubicSDevice

if __name__ == "__main__":
    examples = ("0", "1", "2", "G1", "N1G1N1")
    for e in examples:
        print(e)
        print(AnycubicSDevice.checksum(e))

