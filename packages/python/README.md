# Diagraph

Diagraph represents Large Language Model (LLM) interactions as a graph, which makes it easy to build, edit, and re-execute a chain of structured dialogues.

<a href="https://colab.research.google.com/github/ambient-labs/Diagraph/blob/master/docs/usage.ipynb" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab" title="Open In Colab" /></a>

Key features:

- **Cache & Replay:** Rerun starting from specific interactions. Save time and money.
- **Edits:** Edit interactions - prompts, results, functions - on the fly.
- **Dependencies:** Specify a function's dependencies as parameters for clean, readable, refactorable code.
- **Functions:** Use any LLM or set of tools you want. Diagraph operates on top of plain Python functions.
- **Visualizations:** Get a straightforward view of your graph with a built-in Jupyter visualization tool.
- **Concurrency:** Diagraph takes care of deciding when to run your functions so that all dependencies are satisfied. Get concurrency for free.

## Requirements

Python 3.10+

## Installation

```bash
pip install diagraph
```

## Quickstart

```python
from diagraph import Diagraph, Depends, prompt, llm

openai.api_key = 'sk-<OPENAI_TOKEN>'

@prompt
def tell_me_a_joke():
  return 'Computer! Tell me a joke about tomatoes.'

@prompt
def explanation(joke: str = Depends(tell_me_a_joke)) -> str:
  return f'Explain why the joke "{joke}" is funny.'

dg = Diagraph(explanation).run()
print(dg.result) # 'The joke is a play on words and concepts. There are two main ideas that make it humorous...
dg
```

![Quickstart visualization](https://raw.githubusercontent.com/ambient-labs/Diagraph/main/assets/quickstart.png)

## Usage

[See the usage guide](https://github.com/ambient-labs/Diagraph/blob/main/docs/usage.ipynb).

## License

[MIT](https://github.com/ambient-labs/Diagraph/blob/main/LICENSE)
