const sio = io();

console.log(d3)

// https://stackoverflow.com/questions/16265123/resize-svg-when-window-is-resized-in-d3-js
// let canvas = create_canvas(100, 10)
// let canvas2 = create_canvas(30, 10)
// let canvas3 = create_canvas(30, 10)

const canvas_dict = {}

let current_corpus_position = 0
let corpus_length = 0

const window_width  = window.innerWidth || document.documentElement.clientWidth ||
document.body.clientWidth;
const window_height = window.innerHeight|| document.documentElement.clientHeight||
document.body.clientHeight;

var current_mouseover_node = null
var current_mouseover_canvas = null
var current_mouseover_label_alternatives = null

function create_canvas(width_percent, height_percent) {
    let canvas_width = width_percent*window_width/100
    let canvas_height = canvas_width * height_percent/100
    return d3.select("div#chartId")
                   .append("div")
        .style("width", width_percent + "%")
        .style("padding-bottom", height_percent + "%")
                   .classed("svg-container", true)
                   .append("svg")
                   .attr("preserveAspectRatio", "xMinYMin meet")
                   .attr("viewBox", "0 0 "+canvas_width+" "+ canvas_height)
    .attr("width", "98%")
    .attr("height", "100%")
                   .classed("svg-content-responsive", true)
                    .style("background-color", '#eeeeee')
        .call(d3.zoom().on("zoom", function () {
            // as per "update vor v4" in https://coderwall.com/p/psogia/simplest-way-to-add-zoom-pan-on-d3-js
    d3.select(this).select("g").attr("transform", d3.event.transform)
 }))
        // .call(zoom)
        .append("g");
}


d3.select("#previousButton")
    .on("click", function() {
        if (current_corpus_position > 0) {
            current_corpus_position -= 1
        }
      console.log("previous_button_clicked");
      sio.emit("instance_requested", current_corpus_position);
      set_corpus_position()
        });

d3.select("#nextButton")
    .on("click", function() {
        if (current_corpus_position < corpus_length-1) {
            current_corpus_position += 1
        }
      console.log("next_button_clicked");
      sio.emit("instance_requested", current_corpus_position);
      set_corpus_position()
        });

sio.on('connect', () => {
    console.log('connected');
});

sio.on('disconnect', () => {
  console.log('disconnected');
});


sio.on("set_graph", (data) => {
    console.log("set_graph")
    console.log(data)
    let canvas = canvas_dict[data["canvas_name"]]
    remove_graphs_from_canvas(canvas)
    let label_alternatives = null
    // check if "label_alternatives_by_nodename" is a key in the dictionary
    if ("label_alternatives_by_node_name" in data) {
        label_alternatives = data["label_alternatives_by_node_name"]
    }
    new Graph(20, 20, data["graph"], canvas, true, 0, label_alternatives)
})

sio.on("set_string", (data) => {
    let canvas = canvas_dict[data["canvas_name"]]
    remove_strings_from_canvas(canvas)
    new Strings(20, 20, data["tokens"], canvas)
})

sio.on("set_layout", (layout) => {
    corpus_length = layout[0][0].length
    let canvas_heights = []
    layout.forEach(row => {
        let height_here = 0
        row.forEach(slice => {
            let vis_type = slice["visualization_type"]
            if (vis_type == "STRING") {
                height_here = Math.max(height_here, 10)
            } else {
                height_here = Math.max(height_here, 99/row.length)
            }
        })
        canvas_heights.push(height_here)
    })
    // normalize the heights
    let total_height = canvas_heights.reduce((a, b) => a + b, 0)
    for (let i = 0; i < canvas_heights.length; i++) {
        canvas_heights[i] = 40 * canvas_heights[i] / total_height
    }
    for (let i = 0; i < layout.length; i++) {
        let row = layout[i]
        let height = canvas_heights[i]
        row.forEach(slice => {
            canvas_dict[slice["name"]] = create_canvas(99/row.length, height)
        })
    }
})

sio.on("set_corpus_length", (data) => {
    corpus_length = data;
    set_corpus_position()
})

function remove_graphs_from_canvas(canvas) {
    canvas.selectAll("."+NODE_CLASSNAME+", ."+BACKGROUND_CLASSNAME+", ."+EDGE_CLASSNAME).remove()
}

function remove_strings_from_canvas(canvas) {
    canvas.selectAll("."+TOKEN_CLASSNAME).remove()
}

function set_corpus_position() {
    d3.select("#corpusPositionText").text((current_corpus_position+1)+"/"+corpus_length)
}

d3.select("body").on("keydown", function () {
    // keyCode of alt key is 18
    if (d3.event.keyCode == 17) {
        if (current_mouseover_node != null) {
            show_label_alternatives(current_mouseover_node,
                current_mouseover_label_alternatives,
                current_mouseover_canvas)
        }
    }
});

d3.select("body").on("keyup", function () {
    // keyCode of alt key is 18
    if (d3.event.keyCode == 17) {
        if (current_mouseover_node != null) {
            hide_label_alternatives(current_mouseover_canvas)
        }
    }
});