#  Copyright (c) 2022 , IRIS-HEP
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   * Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
import io
import os
import zipfile
from tempfile import TemporaryDirectory

from servicex_codegen.code_generator import CodeGenerator, GeneratedFileResult


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


class TestCodeGenerator:
    def test_translate_query_to_zip(self, mocker):
        mocker.patch.object(CodeGenerator, "__abstractmethods__", new_callable=set)
        code_gen = CodeGenerator()

        with TemporaryDirectory() as tempdir, \
                open(os.path.join(tempdir, "baz.txt"), 'w'),\
                open(os.path.join(tempdir, "foo.txt"), 'w'):
            code_gen.generate_code = mocker.Mock(
                return_value=GeneratedFileResult(hash="31415", output_dir=tempdir)
            )

            zip_bytes = code_gen.translate_query_to_zip("select * from foo")
            check_zip_file(zip_bytes, expected_file_count=2)
