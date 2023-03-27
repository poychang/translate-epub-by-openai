import argparse
import time
import openai
import ast
import string
from bs4 import BeautifulSoup as bs
from ebooklib import epub
from rich import print
from opencc import OpenCC

class TCTranslatorGPT:
    def __init__(self, key, base, version):
        self.key = key
        self.base = base
        self.version = version

    def translate(self, text):
        if text.isspace():
            return ""
        # print(text)

        cc = OpenCC('s2tw')
        openai.api_key = self.key
        openai.api_type = "azure"
        openai.api_base = self.base
        openai.api_version = self.version
        try:
            completion = openai.ChatCompletion.create(
                engine="gpt-35-turbo",
                messages=[
                    {
                        "role": "user",
                        # english prompt here to save tokens
                        "content": f"Please help me to translate `{text}` to Traditional Chinese, please return only translated content does not include the origin text, maintain the same formatting as the original textual list individual elements, proper nouns does not be translated ",
                    }
                ],
            )
            t_text = (
                completion["choices"][0]
                .get("message")
                .get("content")
                .encode("utf8")
                .decode()
            )
            # Force to convert to Traditional Chinese
            t_text = cc.convert(t_text)

            try:
                t_text = ast.literal_eval(t_text)
            except Exception:
                # some ["\n"] not literal_eval, not influence the result
                pass
            # TIME LIMIT for Azure OpenAI API
            # ChatGPT Model：300/min
            time.sleep(1)
        except Exception as e:
            print(str(e), "will sleep 10 seconds")
            # TIME LIMIT for Azure OpenAI API
            # ChatGPT Model：300/min
            time.sleep(10)
            completion = openai.ChatCompletion.create(
                engine="gpt-35-turbo",
                messages=[
                    {
                        "role": "user",
                        # english prompt here to save tokens
                        "content": f"Please help me to translate `{text}` to Traditional Chinese, please return only translated content does not include the origin text, maintain the same formatting as the original textual list individual elements, proper nouns does not be translated ",
                    }
                ],
            )
            t_text = (
                completion["choices"][0]
                .get("message")
                .get("content")
                .encode("utf8")
                .decode()
            )
            t_text = cc.convert(t_text.strip("\n"))
            try:
                t_text = ast.literal_eval(t_text)
            except Exception:
                pass
        print(t_text)
        return t_text

class BEPUB:
    def __init__(self, epub_name, key, base, version):
        self.epub_name = epub_name
        self.translate_model = TCTranslatorGPT(key, base, version)
        self.origin_book = epub.read_epub(self.epub_name)

    def translate_book(self):
        new_book = epub.EpubBook()
        new_book.metadata = self.origin_book.metadata
        new_book.spine = self.origin_book.spine
        new_book.toc = self.origin_book.toc
        for i in self.origin_book.get_items():
            if i.get_type() == 9:
                soup = bs(i.content, "html.parser")
                p_list = soup.findAll("p")
                for p in p_list:
                    if p.text and not p.text.isdigit():
                        try:
                            # p.string = p.text + self.translate_model.translate(p.text) # Keep the original text
                            p.string = self.translate_model.translate(p.text)
                        except Exception as e:
                            print(str(e), style="bold red")
                            continue
                    # Process any remaining paragraphs in the last batch
                print("------------------------------ done with ", i)
                i.content = soup.prettify().encode()
            new_book.add_item(i)
        name = self.epub_name.split(".")[0]
        epub.write_epub(f"{name}_translated.epub", new_book, {})
        print(f"Translated book saved as '{name}_translated.epub'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--book_name",
        dest="book_name",
        type=str,
        help="your epub book name",
    )
    parser.add_argument(
        "--openai_key",
        dest="openai_key",
        type=str,
        default="",
        help="OpenAI API key",
    )
    parser.add_argument(
        "--openai_api_base",
        dest="openai_api_base",
        type=str,
        default="",
        help="Azure OpenAI API base",
    )
    parser.add_argument(
        "--openai_api_version",
        dest="openai_api_version",
        type=str,
        default="2023-03-15-preview",
        help="Azure OpenAI API version",
    )
    options = parser.parse_args()
    OPENAI_API_KEY = options.openai_key
    OPENAI_API_BASE = options.openai_api_base
    OPENAI_API_VERSION = options.openai_api_version
    if not OPENAI_API_KEY:
        raise Exception("Need Azure OpenAI API key")
    if not OPENAI_API_BASE:
        raise Exception("Need Azure OpenAI API base URL")
    if not OPENAI_API_VERSION:
        raise Exception("Need Azure OpenAI API version")
    if not options.book_name.endswith(".epub"):
        raise Exception("please use epub file")
    e = BEPUB(options.book_name, OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_API_VERSION)
    e.translate_book()
