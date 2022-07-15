NODE_ALTERNATIVE_CLASSNAME = "node_alternative"

function show_label_alternatives(node_object, label_alternatives, canvas) {
    canvas.append("rect")
        .attr("x", node_object.getX() + 50)
        .attr("y", node_object.getY())
        .attr("width", 50)
        .attr("height", 50)
        .attr("class", NODE_ALTERNATIVE_CLASSNAME)
    console.log(label_alternatives)
}

function hide_label_alternatives(canvas) {
    canvas.selectAll("."+NODE_ALTERNATIVE_CLASSNAME).remove()
}