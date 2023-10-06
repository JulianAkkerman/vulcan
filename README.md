# vulcan
 Visualizations for Understanding Language Corpora and model predictioNs

## Setup

Vulcan requires several packages that can all be installed with pip:

```
pip install python-socketio eventlet penman amconll wikipedia nltk conllu
```

You may want to do this within a virtual environment like a conda environment, as per your preference.

## Run

To visualize a pickle file, from the main directory of this repository run

```
PYTHONPATH=./ python3 vulcan/launch_vulcan.py path/to/pickle-file.pickle
```

To visualize a JSON file, from the main directory of this repository run

```
PYTHONPATH=./ python3 vulcan/launch_vulcan.py path/to/json-file.json --json
```

To visualise an AMR corpus file (in the standard format, e.g. the official AMR corpus), run

```
PYTHONPATH=./ python3 vulcan/visualize_amr_corpus.py path/to/corpus/file.txt
```

This will start the server on `127.0.0.1:5050`. Open that website in a browser and you can look at the examples in the file. If you want to run multiple visualizations at once, you have to specify a different port for each of them, using the `-p` argument. The port is the last bit of `127.0.0.1:5050`, i.e. by default it is `5050`. Some ports are reserved by the system, but usually the range between `5050` and `5059` works well. So for example, if you run  

```
PYTHONPATH=./ python3 vulcan/visualize_amr_corpus.py path/to/corpus/file.txt -p 5051
```

then the visualization can be accessed at `127.0.0.1:5051` in your browser.

### Windows users

In Windows, you cannot specify the PYTHONPATH inline as done here. Instead, you must set the PYTHONPATH system variable in the system settings, and then use the command starting from `python3 ...`.

### Options

Run with `-h` to show full documentation. Options include:

* Specify a port with the `-p` argument (see the "Run" section above).
* Showing propbank frame information on mouseover for nodes in AMR graphs. E.g. if you mouseover a node labeled `run-03`, a little box will appear that shows the propbank definition of `run-03`, including the role information and other senses of `run`. To use this, use the `-pf` option and specify the path to the folder containing the propbank frame files (e.g. `-pf ../amr3.0/data/frames/propbank-amr-frames-xml-2018-01-25/`). Loading all the propbank frames takes a minute or two.
* Showing Wikipedia article summaries on mouseover for wiki-nodes in AMR graphs. This shows the first two sentences of the Wikipedia article specified by the node. Use the `-wiki` flag to activate this. Note that when using this option, Vulcan gathers the wiki information for all graphs in the pickle at the beginning; this is rather slow. So if you use this option, just let it run in the background and come back to it later.
* Showing node names in graphs: use the `--show-node-names` option. A node with name `n` and label `label` will be shown as `n / label` (per default, only `label` is shown).

## Use

Use the previous/next buttons to cycle through the corpus. You can zoom (mousewheel) and drag each graph/tree/sentence. Hovering over a node will highlight adjacent edges; hovering over an edge will highlight the edge.
