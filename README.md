# vulcan
 Visualizations for Understanding Language Corpora and model predictioNs

## Setup

```
pip install python-socketio eventlet penman
```

## Run

First, `cd` into the `vulcan` subfolder (where the `vulcan.py` file is located). To visualize a pickle file, then run

```
python3 vulcan.py path/to/pickle-file
```

This will start the server on [127.0.0.1:5050](127.0.0.1:5050). Open that website in a browser and you can look at the examples in the file.

## Use

Use the previous/next buttons to cycle through the corpus. You can zoom and drag each graph/tree/sentence. Hovering over a node will highlight adjacent edges; hovering over an edge will highlight the edge.
