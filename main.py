# coding=utf-8
from tokenizer import get_token
from pascal_loader.main_io import PascalFile

get_token(PascalFile(input_file_location='hello_world.pas', output_location=''))
