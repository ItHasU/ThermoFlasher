import esptool
from urllib.request import urlopen, urlretrieve
import json, os, re, tempfile, zipfile

def start(msg):
    print(msg, end=" ", flush=True)

def done(msg="done"):
    print(f"\033[92m{msg}\033[0m")

def error(e, msg="failed!"):
    print(f"\033[91m{msg}\033[0m")
    if e: print(e)
    cleanup()
    input("Press [enter] to exit")
    exit(1)

def cleanup():
    try:
        global tmpdirname
        os.rmdir(tmpdirname)
    except:
        pass

# Create a temporary file
tmpdirname = tempfile.mkdtemp()

release_url = None
release_version = None
start("Fetching latest release...")
try:
    with urlopen("https://api.github.com/repos/ItHasU/WirelessThermometer/releases/latest") as fp:
        release = json.load(fp)
        release_version = release["name"]
        release_url = release["assets"][0]["browser_download_url"]
except Exception as e:
    error(e)
done(release_version)

start(f"Downloading...")
zip_path = os.path.join(tmpdirname, "binairies.zip")
try:
    urlretrieve(release_url, zip_path)
except Exception as e:
    error(e)
done()

start("Listing firmwares...")
boards = []
try:
    with zipfile.ZipFile(zip_path) as zip_content:
        for path in zip_content.namelist():
            m = re.match("^binaries/(.*)/$", path)
            if m:
                boards.append(m.group(1))
except Exception as e:
    error(e)

if len(boards) == 0:
    error("No board found, sorry")
done()

boards.sort()

selected = -1
while selected < 0 or selected >= len(boards):
    for i in range(len(boards)):
        print(f"{i}. {boards[i]}")
    selected_str = input("Please select a board (just press enter to abort): ").strip()
    if selected_str == "":
        error("Hope to see you soon!")
    try:
        selected = int(selected_str)
    except:
        print("Invalid number")
        selected = -1

board_id = boards[selected]

board_path = f"binaries/{board_id}/"
base_folder = os.path.join(tmpdirname, "binaries", board_id)

start(f"Preparing files for {board_id}...")
args = []
try:
    with zipfile.ZipFile(zip_path) as zip_content:
        zip_content.extractall(tmpdirname, [f for f in zip_content.namelist() if f.startswith(board_path)])

    args_path = os.path.join(base_folder, "args.cmd")
    with open(args_path) as fp:
        args_str = fp.read()
        raw_args = args_str.strip().split()
    for arg in raw_args:
        if arg.endswith(".bin"):
            # This is a file, we need to prepend the folder
            args.append(os.path.join(base_folder, arg))
        else:
            args.append(arg)
except Exception as e:
    error(e)

done()

start(f"Flashing...")
done("starting esptool")

try:
    esptool.main(args)
except Exception as e:
    error(e)

done("Board flashed successfully!")
cleanup()
input("Press [Enter] to exit")