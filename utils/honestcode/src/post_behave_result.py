import sys
import os
import subprocess
from urllib import request


def format_json(json_path, upload_path):
    command = "cat " + json_path + " | jq '.' > " + upload_path
    res = None

    try:
        res = subprocess.Popen(command, stdin=subprocess.PIPE, shell=True)
    except OSError:
        print("Error opening result of behave file.")
        exit(-1)

    res.wait()
    if res.returncode != 0:
        print("Error formatting results of behave file")
        exit(-1)


def upload_to_honestcode(json_path, test_hook_key):
    with open(json_path, 'rb') as f:
        data = f.read()
    url = 'https://pro.honestcode.io/api/hooks/tr/{}'.format(test_hook_key)
    response = request.urlopen(url, data=data)
    if response.getcode() != 200:
        print("Error uploading results to honestcode.")
        exit(-1)
    else:
        print("Behave results successfully uploaded to honestcode.")


def remove_process_files(src_path, out_path):
    if os.path.exists(src_path):
        os.remove(src_path)
    else:
        print("Could not remove behave results file.")

    if os.path.exists(out_path):
        os.remove(out_path)
    else:
        print("Could not remove formatted behave results file.")


if __name__ == '__main__':
    if len(sys.argv) > 2:
        src_file = sys.argv[1]
        test_hook_key = sys.argv[2]
        output_path = "file_to_upload.json"

        format_json(src_file, output_path)
        upload_to_honestcode(output_path, test_hook_key)
        remove_process_files(src_file, output_path)
    else:
        print("Not enough args.")
        exit(-1)
