const sio = io();

console.log(d3)

let canvas = d3.select("body").append("svg")
                    .attr("width", 2000)
                    .attr("height", 1000)
                    .style("background-color", '#eeeeee');


d3.select("#previousButton")
    .on("click", function() {
      console.log("previous_button_clicked");
      sio.emit("previous_button_clicked");
      });

d3.select("#nextButton")
    .on("click", function() {
      console.log("next_button_clicked");
      sio.emit("next_button_clicked");
        });

sio.on('connect', () => {
  console.log('connected');
});

sio.on('disconnect', () => {
  console.log('disconnected');
});


sio.on("make_graph", (data) => {
    remove_all_graphs()
    createGraph(100, 100, data, canvas)
})

function remove_all_graphs() {
    d3.selectAll("."+NODE_CLASSNAME+", ."+BACKGROUND_CLASSNAME+", ."+EDGE_CLASSNAME).remove()
}

sio.on("set_corpus_position", (data) => {
    d3.select("#corpusPositionText").text((data.current+1)+"/"+data.total)
})