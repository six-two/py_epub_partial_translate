#!/usr/bin/python3
import os
from typing import Callable
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryDirectory
# You might to install them via pip
from bs4 import BeautifulSoup

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def unzip(input_zip: str, output_dir: str) -> None:
    with ZipFile(input_zip, 'r') as zip:
        zip.extractall(output_dir)


def zip(input_dir: str, output_zip: str) -> None:
    with ZipFile(output_zip, 'w', ZIP_DEFLATED) as zip:
        for root, _dirs, files in os.walk(input_dir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(os.path.join(root, f), input_dir)
                zip.write(full_path, rel_path)


class EpubModifier:
    def __init__(self, text_transform: Callable[[str], str]):
        self.text_transform = text_transform

    def modify_epub(self, input_epub: str, output_epub: str) -> None:
        if not input_epub.endswith('.epub'):
            raise Exception(f'File needs to have a ".epub" extension: "{input_epub}"')
        
        with TemporaryDirectory() as tmp_dir:
            unzip(input_epub, tmp_dir)
            self.modify_unzipped_epub_file_inplace(tmp_dir)
            zip(tmp_dir, output_epub)

    def modify_unzipped_epub_file_inplace(self, epub_dir: str) -> None:
        for root, _dirs, files in os.walk(epub_dir):
            for f in files:
                if f.endswith(".html"):
                    # TODO read metadata files to be able to ignore the titlepage, toc, etc
                    full_path = os.path.join(root, f)
                    self.modify_html_inplace(full_path)

    def modify_html_inplace(self, html_file: str) -> None:
        html_input = open(html_file, 'r').read()
        soup = BeautifulSoup(html_input, 'html.parser')

        # Find all text nodes
        for e in soup.findAll(text=True):
            # Replace the text with the uppercase version
            original = str(e)
            modified = self.text_transform(original)
            e.replace_with(modified)

        html_output = str(soup)
        with open(html_file, "w") as f:
            f.write(html_output)


if __name__ == '__main__':
    input_epub = os.path.join(SCRIPT_DIR, "test.epub")
    output_epub = os.path.join(SCRIPT_DIR, "test.modified.epub")

    def transform_to_uppercase(text: str) -> str:
        return text.upper()

    editor = EpubModifier(transform_to_uppercase)
    editor.modify_epub(input_epub, output_epub)
