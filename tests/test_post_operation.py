# Copyright (c) 2019, IRIS-HEP
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import io
import os
import zipfile
from tempfile import TemporaryDirectory

from requests_toolbelt.multipart import decoder

from servicex_codegen import create_app
from servicex_codegen.code_generator import (GenerateCodeException,
                                             GeneratedFileResult)


def get_zipfile_data(zip_data: bytes):
    with zipfile.ZipFile(io.BytesIO(zip_data)) as thezip:
        for zipinfo in thezip.infolist():
            with thezip.open(zipinfo) as thefile:
                yield zipinfo.filename, thefile


def check_zip_file(zip_data: bytes, expected_file_count):
    names = []
    for name, data in get_zipfile_data(zip_data):
        names.append(name)
        print(name)
    assert len(names) == expected_file_count


class TestPostOperation:
    def test_post_good_query_with_params(self, mocker):
        """Produce code for a simple good query"""

        with TemporaryDirectory() as tempdir, \
                open(os.path.join(tempdir, "baz.txt"), 'w'),\
                open(os.path.join(tempdir, "foo.txt"), 'w'):

            mock_ast_translator = mocker.Mock()
            mock_ast_translator.generate_code = mocker.Mock(
                return_value=GeneratedFileResult(hash="1234", output_dir=tempdir)
            )

            config = {
                'TARGET_BACKEND': 'uproot',
                'TRANSFORMER_SCIENCE_IMAGE': "foo/bar:latest"
            }
            app = create_app(config, provided_translator=mock_ast_translator)
            client = app.test_client()

            print(app.config)

            select_stmt = "(call ResultTTree (call Select (call SelectMany (call EventDataset (list 'localds://did_01')"  # noqa: E501

            response = client.post("/servicex/generated-code", json={
                "transformer_image": "sslhep/servicex_func_adl_xaod_transformer:develop",
                "code": select_stmt
            })

        boundary = response.data[2:34].decode('utf-8')
        content_type = f"multipart/form-data; boundary={boundary}"
        decoder_parts = decoder.MultipartDecoder(response.data, content_type)

        transformer_image = str(decoder_parts.parts[0].content, 'utf-8')
        zip_file = decoder_parts.parts[1].content

        print("Transformer Image: ", transformer_image)
        print("Zip File: ", zip_file)

        assert response.status_code == 200
        check_zip_file(zip_file, 2)
        # Capture the temporary directory that was generated
        cache_dir = mock_ast_translator.generate_code.call_args[1]['cache_path']
        mock_ast_translator.generate_code.assert_called_with(select_stmt,
                                                             cache_path=cache_dir)

    def test_post_good_query_without_params(self, mocker):
        """Produce code for a simple good query"""

        with TemporaryDirectory() as tempdir, \
                open(os.path.join(tempdir, "baz.txt"), 'w'),\
                open(os.path.join(tempdir, "foo.txt"), 'w'):

            mock_ast_translator = mocker.Mock()
            mock_ast_translator.generate_code = mocker.Mock(
                return_value=GeneratedFileResult(hash="1234", output_dir=tempdir)
            )

            config = {
                'TARGET_BACKEND': 'uproot',
                'TRANSFORMER_SCIENCE_IMAGE': 'sslhep/servicex_func_adl_xaod_transformer:develop',
            }

            app = create_app(config, provided_translator=mock_ast_translator)
            client = app.test_client()

            print(app.config)

            select_stmt = "(call ResultTTree (call Select (call SelectMany (call EventDataset (list 'localds://did_01')"  # noqa: E501

            response = client.post("/servicex/generated-code", json={
                "code": select_stmt
            })

            boundary = str(response.data[2:34], 'utf-8')
            content_type = f"multipart/form-data; boundary={boundary}"
            decoder_parts = decoder.MultipartDecoder(response.data, content_type)

            transformer_image = str(decoder_parts.parts[0].content, 'utf-8')
            zip_file = decoder_parts.parts[1].content

            print("Transformer Image: ", transformer_image)
            print("Zip File: ", zip_file)

        assert response.status_code == 200
        check_zip_file(zip_file, 2)
        # Capture the temporary directory that was generated
        cache_dir = mock_ast_translator.generate_code.call_args[1]['cache_path']
        mock_ast_translator.generate_code.assert_called_with(select_stmt,
                                                             cache_path=cache_dir)

    def test_post_codegen_error_query(self, mocker):
        """Post a query with a code-gen level error"""
        mock_ast_translator = mocker.Mock()
        mock_ast_translator.generate_code = \
            mocker.Mock(side_effect=GenerateCodeException("This is an expected exception"))

        config = {
            'TARGET_BACKEND': 'uproot'
        }
        app = create_app(config, provided_translator=mock_ast_translator)
        client = app.test_client()
        select_stmt = "(call ResultTTree (call Select (call SelectMany (call EventDataset (list 'localds://did_01')"  # noqa: E501

        response = client.post("/servicex/generated-code", data=select_stmt)

        assert response.status_code == 500
        assert 'Message' in response.json
