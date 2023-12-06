# VULCAN
VULCAN (Visualizations for Understanding Language Corpora and model predictioNs) is a tool that makes it easy for you to look at your data! VULCAN visualizes linguistic objects like strings, trees and graphs as well as neural model properties like attention and alternate predictions with their likelihoods. 

## Online Demo

Have a look at the online demo here: https://vulcan-99e0.onrender.com/

This demo shows predictions of the [AM parser](https://github.com/coli-saar/am-parser) on the [Little Prince AMR dataset](https://amr.isi.edu/download.html). This visualization corresponds to the case study in Section 5 of the paper (to appear at BlackboxNLP 2023).

## Setup

Vulcan requires several packages that can all be installed with pip:

```
python3 -m pip install python-socketio eventlet penman amconll wikipedia nltk conllu
```

You may want to do this within a virtual environment like a conda environment, as per your preference.

## Running VULCAN

VULCAN has a server-client setup: the server reads in a visualization input file once, and then hosts the visualization. The client is simply a website, showing the visualization in your browser. You can run this all locally on your computer, or on a server to share with the world.

### Creating an input file

The first step in visualizing data with VULCAN is to create an input `pickle` or `json` file containing that data, in VULCAN's dictionary format. The most convenient way of building such a file is with the `vulcan.pickle_builder.PickleBuilder` class; see the documentation there. Full documentation of other options, and examples, will be added to this repo soon.

### Setting up the server

To visualize a pickle file, from the main directory of this repository run

```
python3 launch_vulcan.py path/to/pickle-file.pickle
```

To visualize a JSON file, from the main directory of this repository run

```
python3 launch_vulcan.py path/to/json-file.json --json
```

To visualise an AMR corpus file (in the standard format, e.g. the official AMR corpus), run

```
python3 visualize_amr_corpus.py path/to/corpus/file.txt
```

This will start the server on `127.0.0.1:5050`. Open that website in a browser and you can look at the examples in the file. If you want to run multiple visualizations at once, you have to specify a different port for each of them, using the `-p` argument. The port is the last bit of `127.0.0.1:5050`, i.e. by default it is `5050`. Some ports are reserved by the system, but usually the range between `5050` and `5059` works well. So for example, if you run  

```
PYTHONPATH=./ python3 vulcan/visualize_amr_corpus.py path/to/corpus/file.txt -p 5051
```

then the visualization can be accessed at `127.0.0.1:5051` in your browser.

Run with `-h` to show full documentation. Options include:

* Specify a port with the `-p` argument (see the "Run" section above).
* Specify an address with the `-a` argument. The default is `localhost`, making the visualization accessible just from the machine where the server is running. To make your visualization publicly accessible, you probably want to use `-a 0.0.0.0`. Where exactly your visualization can then be accessed depends on the setup of your machine.
* Showing propbank frame information on mouseover for nodes in AMR graphs. E.g. if you mouseover a node labeled `run-03`, a little box will appear that shows the propbank definition of `run-03`, including the role information and other senses of `run`. To use this, use the `-pf` option and specify the path to the folder containing the propbank frame files (e.g. `-pf ../amr3.0/data/frames/propbank-amr-frames-xml-2018-01-25/`). Loading all the propbank frames takes a minute or two.
* Showing Wikipedia article summaries on mouseover for wiki-nodes in AMR graphs. This shows the first two sentences of the Wikipedia article specified by the node. Use the `-wiki` flag to activate this. Note that when using this option, Vulcan gathers the wiki information for all graphs in the pickle at the beginning; this is rather slow. So if you use this option, just let it run in the background and come back to it later.
* Showing node names in graphs: use the `--show-node-names` option. A node with name `n` and label `label` will be shown as `n / label` (per default, only `label` is shown).

### Accessing the visualization

VULCAN's visualizations can be viewed in the browser. The default address, when running locally, is `127.0.0.1:5050`. If you host a VULCAN visualization on the internet, the address where your visualization can be addressed depends on the setup of your machine.

Use the previous/next buttons to cycle through the corpus. You can zoom (mousewheel) and drag each graph/tree/sentence. Hovering over a node will highlight adjacent edges; hovering over an edge will highlight the edge. The same mouseover will highlight attention and alignments if given.

Using `CTRL` + mouseover shows alternative labels with their scores, if provided.

