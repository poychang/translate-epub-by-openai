# Translate ePub by OpenAI API

Using OpenAI's technology to translate epub books to Traditional Chinese.

## Prepare

1. Azure OpenAI Service API key
2. epub books
3. python3.8+

## How to use

1. `pip install -r requirements.txt`
2. `python translate.py --book_name ${book_name} --openai_key ${openai_key} --openai_api_base ${openai_api_base} --openai_api_version ${openai_api_version}`

## Attention

The key is not free. If you're interested in trying out Azure services, you can sign up for a free trial on the [official website](https://azure.microsoft.com/free/).

## Thanks

This project is based on lots of open source contributors. he yihong's projects and I change it for myself. Batch translation is faster and less fee , suitable for those who do not pursue the perfect format .Delete the function which is not used. It is geared more toward programmers now than everyone else.

- [zengzzzzz/translate-epub-book-by-openai](https://github.com/zengzzzzz/translate-epub-book-by-openai)
- [yichen0831/opencc-python](https://github.com/yichen0831/opencc-python)
