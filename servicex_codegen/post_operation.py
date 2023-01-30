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
import os
import zipfile
from tempfile import TemporaryDirectory

from flask import Response, request
from flask_restful import Resource
from requests_toolbelt import MultipartEncoder

from servicex_codegen.code_generator import CodeGenerator, GeneratedFileResult


class GeneratedCode(Resource):
    @classmethod
    def make_api(cls, code_generator: CodeGenerator):
        cls.code_generator = code_generator
        return cls

    def zipdir(self, path: str, zip_handle: zipfile.ZipFile) -> None:
        """Given a `path` to a directory, zip up its contents into a zip file.

        Arguments:
            path        Path to a local directory. The contents will be put into the zip file
            zip_handle  The zip file handle to write into.
        """
        for root, _, files in os.walk(path):
            for file in files:
                zip_handle.write(os.path.join(root, file), file)

    def stream_generated_code(self, generated_code_result: GeneratedFileResult) -> bytes:
        """Translate a text ast into a zip file as a memory stream

        Arguments:
            code            Text `qastle` version of the input ast generated by func_adl

        Returns
            bytes       Data that if written as a binary output would be a zip file.
        """

        # Generate the python code
        with TemporaryDirectory() as tempdir:

            # Zip up everything in the directory - we are going to ship it as back as part
            # of the message.
            z_filename = os.path.join(str(tempdir), 'joined.zip')
            zip_h = zipfile.ZipFile(z_filename, 'w', zipfile.ZIP_DEFLATED)
            self.zipdir(generated_code_result.output_dir, zip_h)
            zip_h.close()

            with open(z_filename, 'rb') as b_in:
                return b_in.read()

    def post(self):
        try:
            with TemporaryDirectory() as tempdir:
                body = request.get_json()
                generated_code_result = self.code_generator.generate_code(
                    body["code"], cache_path=tempdir)

                zip_data = self.stream_generated_code(generated_code_result)
                # code gen transformer returns the default transformer image mentioned in
                # the config file
                transformer_image = os.environ.get("TRANSFORMER_SCIENCE_IMAGE")

                # MultipartEncoder library takes multiple types of data fields and merge
                # them into a multipart mime data type
                m = MultipartEncoder(
                    fields={'transformer_image': transformer_image,
                            'zip_data': zip_data}
                )

                response = Response(
                    response=m.to_string(),
                    status=200, mimetype=m.content_type)
                return response

        except BaseException as e:
            print(str(e))
            import sys
            import traceback
            traceback.print_exc(file=sys.stdout)
            return {'Message': str(e)}, 500
