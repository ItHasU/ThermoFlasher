import esptool

args = []
# Args
args += ["--chip", "esp32"]
args += ["--baud", "460800"]
args += ["--before", "default_reset"]
args += ["--after", "hard_reset", "write_flash", "-z"]
args += ["--flash_mode", "dio", "--flash_freq", "40m", "--flash_size", "detect"]
# Files
args += ["0x1000", "binaries/bootloader_dio_40m.bin"]
args += ["0x8000", "binaries/partitions.bin"]
args += ["0xe000", "binaries/boot_app0.bin"]
args += ["0x10000", "binaries/firmware.bin"]
args += ["0x290000", "binaries/spiffs.bin"]

esptool.main(args)