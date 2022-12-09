# General Information

We know you're a professional, but here is some information you might find useful.

1. Use a virtual environment (venv) and the packages specified in the requirements.txt file.
2. Use the [lm-dataformat library](https://github.com/leogao2/lm_dataformat) to create the resulting jsonl.zst file
3. Don't forget the metadata for each document(characters, sentences, words, verbs, nouns, punctuations, symbols) and manifest file (the most important source of data and rights). If in doubt, ask on the [SpeakLeash discord](https://discord.com/invite/V9rW8nbq).
4. The data must be shuffled.
5. In the README.md file, always add a Usage section and a few sentences on how to use the tool.
6. For processing large files, we recommend using tqdm, threading, and saving state (for the resume function).
7. Have fun!

# Usage

Run example:

```
python main.py
```
