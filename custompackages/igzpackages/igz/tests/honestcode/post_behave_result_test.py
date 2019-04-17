import sys
import subprocess

from unittest import TestCase, mock

from igz.packages.honestcode.post_behave_result import main, format_json, remove_process_files, upload_to_honestcode


class TestPostBehaveResult(TestCase):

    @mock.patch("igz.packages.honestcode.post_behave_result.format_json")
    @mock.patch("igz.packages.honestcode.post_behave_result.upload_to_honestcode")
    @mock.patch("igz.packages.honestcode.post_behave_result.remove_process_files")
    @mock.patch('builtins.exit')
    @mock.patch('builtins.print')
    def test_main(self, mock_print, mock_exit, mock_remove_process_files, mock_upload_to_honestcode, mock_format_json):
        test_args = ["script", "src_file", "blueprint"]
        with mock.patch.object(sys, 'argv', test_args):
            main()
            mock_format_json.assert_called_once()
            mock_upload_to_honestcode.assert_called_once()
            mock_remove_process_files.assert_called_once()

        test_args = ["script", "src_file"]
        with mock.patch.object(sys, 'argv', test_args):
            main()
            mock_print.assert_called_with('Not enough args. Arg 1: behave output json path formatted by jq. '
                                          'Arg 2: HonestCode blueprint key,')
            mock_exit.assert_called_with(-1)

    @mock.patch('igz.packages.honestcode.post_behave_result.os.remove')
    @mock.patch('igz.packages.honestcode.post_behave_result.os.path')
    @mock.patch('builtins.print')
    def test_remove_process_files(self, mock_print, mock_path, mock_remove):
        # Test that first file does not exist
        mock_path.exists.side_effect = [False, True]
        remove_process_files("src path", "out_path")
        mock_remove.assert_called_once()
        mock_print.assert_called_with('Could not remove behave results file.')

        # Test that second file does not exist
        mock_remove.reset_mock()
        mock_path.exists.side_effect = [True, False]
        remove_process_files("src path", "out_path")
        mock_remove.assert_called_once()
        mock_print.assert_called_with('Could not remove formatted behave results file.')

        # Test that the files both exist
        mock_remove.reset_mock()
        mock_path.exists.side_effect = [True, True]
        remove_process_files("src path", "out_path")
        assert 2 == mock_remove.call_count

    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="data")
    @mock.patch('builtins.print')
    @mock.patch('urllib.request.urlopen')
    @mock.patch('builtins.exit')
    def test_upload_to_honestcode(self, mock_exit, mock_urlopen, mock_print, mock_file):
        cm = mock.MagicMock()
        cm.getcode.return_value = 200
        mock_urlopen.return_value = cm
        upload_to_honestcode("path", "key")

        assert open("path/to/open").read() == "data"
        mock_file.assert_called_with("path/to/open")
        mock_urlopen.assert_called_with('https://pro.honestcode.io/api/hooks/tr/{}'.format("key"), data="data")
        mock_print.assert_called_with('Behave results successfully uploaded to honestcode.')

        cm = mock.MagicMock()
        cm.getcode.return_value = 400
        mock_urlopen.return_value = cm
        upload_to_honestcode("path", "key")
        mock_print.assert_called_with('Error uploading results to honestcode.')
        mock_exit.assert_called_with(-1)

    @mock.patch('subprocess.Popen')
    def test_format_json(self, mock_call):
        json_path = "path_to_json"
        upload_path = "path_upload"

        mock_call.return_value.returncode = 0
        format_json(json_path, upload_path)
        command = "cat " + json_path + " | jq '.' > " + upload_path
        mock_call.assert_called_once_with(command, stdin=subprocess.PIPE, shell=True)
