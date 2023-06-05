const sio = io();

console.log(d3)

// https://stackoverflow.com/questions/16265123/resize-svg-when-window-is-resized-in-d3-js
// let canvas = create_canvas(100, 10)
// let canvas2 = create_canvas(30, 10)
// let canvas3 = create_canvas(30, 10)

const canvas_dict = {}
const canvas_name_to_node_name_to_node_dict = {}

let current_corpus_position = 0
let corpus_length = 0

const window_width  = window.innerWidth || document.documentElement.clientWidth ||
document.body.clientWidth;
const window_height = window.innerHeight|| document.documentElement.clientHeight||
document.body.clientHeight;

var current_mouseover_node = null
var current_mouseover_canvas = null
var current_mouseover_label_alternatives = null

function create_canvas(width_percent, height_percent, name="") {
    let canvas_width = width_percent*window_width/100
    let canvas_height = canvas_width * height_percent/100

    let container = d3.select("div#chartId")
      .append("div")
      .style("width", width_percent + "%")
      .style("padding-bottom", height_percent + "%")
      .classed("svg-container", true)
      .style("position", "relative") // Add position property to the container div
      // .style("padding-bottom", "3px") // Add padding to the bottom to make room for the border

    let canvas = container.append("svg")
      .attr("preserveAspectRatio", "xMinYMin meet")
      .attr("viewBox", "0 0 " + canvas_width + " " + canvas_height)
      .attr("width", "calc(100% - 16px)")  // that's 3 + 3 for the borders, I think, but I don't know where the 10 come from
      .attr("height", "calc(100% - 16px)")
      .classed("svg-content-responsive", true)
      .style("background-color", "#eeeeee")
      .style("border", "3px solid black")
      //   .style("box-shadow", "0px 0px 0px 10px black inset")
      .call(d3.zoom().on("zoom", function ()
      {
        // Transform the 'g' element when zooming
        // as per "update vor v4" in https://coderwall.com/p/psogia/simplest-way-to-add-zoom-pan-on-d3-js
        d3.select(this).select("g").attr("transform", d3.event.transform);
      }))

    let g = canvas.append("g")

    if (name !== "") {
        let text_div = container.append("div")
            .style("position", "absolute") // Add position property to the text div
            // .style("top", "10px") // Set position relative to the container div
            // .style("right", "10px") // Set position relative to the container div
            .style("color", "black")
            .style("font-size", "20px")
            .style("background-color", "#FFFFFF")
            .style("border", "3px solid black")
            // add margin
            .style("padding", "10px")
        let text = text_div.text(name);

        // Position the text relative to the SVG element
        let svgRect = canvas.node().getBoundingClientRect(); // Get the bounding box of the SVG element
        // use the -100 for a placeholder of the name for now.
        // get width of the text_div
        let text_div_width = text_div.node().getBoundingClientRect().width
        let dx = svgRect.width - text_div_width; // Calculate the distance from the right edge of the SVG element
        let dy = 10; // Calculate the distance from the top edge of the SVG element
        text.style("top", dy + "px") // Set the position of the text element
            .style("left", dx + "px") // Set the position of the text element


        // // Append a new 'rect' element to the SVG element
        // let rect = text_div.append("rect")
        // .attr("rx", 10)
        // .attr("ry", 10)
        // .attr("x", 0)
        // .attr("y", 0)
        // .attr("width", 100)
        // .attr("height", 20)
        // .attr("fill", "white")
        // .attr("stroke", "black")
        // .attr("stroke-width", 2)
    }

    return g
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
    let canvas = canvas_dict[data["canvas_name"]]
    remove_graphs_from_canvas(canvas)
    let label_alternatives = null
    if ("label_alternatives_by_node_name" in data) {
        label_alternatives = data["label_alternatives_by_node_name"]
    }
    let highlights = null
    if ("highlights" in data) {
        highlights = data["highlights"]
    }
    let mouseover_texts = null
    if ("mouseover_texts" in data) {
        mouseover_texts = data["mouseover_texts"]
    }
    let graph = new Graph(20, 20, data["graph"], canvas, true, 0,
        label_alternatives, highlights, mouseover_texts)
    graph.registerNodesGlobally(data["canvas_name"])
})

sio.on("set_string", (data) => {
    let canvas = canvas_dict[data["canvas_name"]]
    remove_strings_from_canvas(canvas)
    let label_alternatives = null
    if ("label_alternatives_by_node_name" in data) {
        label_alternatives = data["label_alternatives_by_node_name"]
    }
    let highlights = null
    if ("highlights" in data) {
        highlights = data["highlights"]
    }
    let strings = new Strings(20, 20, data["tokens"], canvas, label_alternatives, highlights)
    strings.registerNodesGlobally(data["canvas_name"])
})

var alignment_color_scale = d3.scaleLinear().range(['white','#0742ac']);  // just kinda experimenting

sio.on("set_linker", (data) => {
    let canvas_name1 = data["name1"]
    let canvas_name2 = data["name2"]
    for (let node_name1 in data["scores"]) {
        for (let node_name2 in data["scores"][node_name1]) {
            let score = data["scores"][node_name1][node_name2]
            let node1 = canvas_name_to_node_name_to_node_dict[canvas_name1][node_name1]
            let node2 = canvas_name_to_node_name_to_node_dict[canvas_name2][node_name2]
            register_mousover_alignment(node1, node2, score, canvas_name1+"_"+canvas_name2)
            register_mousover_alignment(node2, node1, score, canvas_name1+"_"+canvas_name2)
        }
    }
})

function register_mousover_alignment(mouseover_node, aligned_node, score, linker_id) {
    mouseover_node.rectangle.on("mouseover.align_"+linker_id, function() {
                aligned_node.rectangle.style("fill", alignment_color_scale(Math.pow(score, 0.75)))  // just kinda experimenting
            })
            .on("mouseout.align_"+linker_id, function() {
                aligned_node.rectangle.style("fill", "white")
            })
}

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
            canvas_dict[slice["name"]] = create_canvas(99/row.length, height, name=slice["name"])

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
    // (current_corpus_position+1)+
    document.getElementById("corpusPositionInput").value = current_corpus_position+1
    d3.select("#corpusPositionText").text("/"+corpus_length)
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

d3.select("#corpusPositionInput").on("keypress", function() {
    if (d3.event.keyCode == 13) {
        let new_position = parseInt(d3.select("#corpusPositionInput").property("value")) - 1
        if (new_position >= 0 && new_position < corpus_length) {
            current_corpus_position = new_position
            set_corpus_position()
            sio.emit("instance_requested", current_corpus_position)
        } else {
            d3.select("#corpusPositionText").text("/" + corpus_length + " Error: invalid position requested")
        }
        return true
    }
})
