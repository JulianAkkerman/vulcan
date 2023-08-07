const NODE_CLASSNAME = "node"
const GRAPH_LABEL_MARGIN = 20

const SHADOW_OVERSIZE = 2

const ALL_NODES = []

class Node {
    constructor(node_position, group, rectangle, content, shadow=null) {
        this.position = node_position[0]
        this.group = group
        this.rectangle = rectangle
        this.content = content
        this.shadow = shadow
        this.registeredEdges = []
    }

    translate(x, y) {
        // this.group.attr("transform", "translate(" + x + "," + y + ")")
        this.position.x = x
        this.position.y = y
        this.group.attr("transform", "translate(" + this.position.x + "," + this.position.y + ")")
    }

    getWidth() {
        return this.content.getWidth()
    }

    setWidth(width) {
        this.rectangle.attr("width", width)
        this.content.recenter(width)
        if (this.shadow != null) {
            this.shadow.attr("width", width + 2*SHADOW_OVERSIZE)
        }
    }

    static get_hypothetical_node_width(node_label) {
        return node_label.length*6.5 + 22
    }

    getHeight() {
        return this.content.getHeight()
    }

    getX() {
        return this.position.x
    }

    getY() {
        return this.position.y
    }

    registerEdge(edge, edge_label, edge_position_data, graph) {
        this.registeredEdges.push([edge, edge_label, edge_position_data, graph])
    }

}

function create_and_register_node_object(node_position, node_group, rect, content_object, draggable, shadow=null) {
    let node_object = new Node(node_position, node_group, rect, content_object, shadow)

    ALL_NODES.push(node_object)

    if (draggable) {
        let nodeDragHandler = d3.drag().on('drag', nodeDragged);
        nodeDragHandler(node_group);
    }
    return node_object;
}

function getNodePosition(x, y) {
    return [{x: x, y: y, id: ALL_NODES.length}];
}

function makeNodeGroup(canvas, node_position, classname) {
    return canvas.data(node_position).append("g")
        .attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        })
        .attr("class", classname);
}

function makeNodeRectangle(is_bold, do_highlight, node_group, content_object, classname) {
    let stroke_width = is_bold ? "4" : "2"

    let fill = "white"
    if (do_highlight) {
        fill = "#56e37c"
    }

    return node_group.append("rect")
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", content_object.getWidth())
        .attr("height", content_object.getHeight())
        .attr("fill", fill)
        .attr("stroke", "black")
        .attr("stroke-width", stroke_width)
        .attr("class", classname)
        .lower();
}

function makeCellRectangle(is_bold, do_highlight, node_group, content_object, classname) {
    if (is_bold) {
        console.log("Warning: Cell was marked as bold, but this is currently not possible.")
    }

    let stroke_width = "0"

    let fill = "white"
    if (do_highlight) {
        fill = "#56e37c"
    }

    return node_group.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", content_object.getWidth())
        .attr("height", content_object.getHeight())
        .attr("fill", fill)
        .attr("stroke", "black")
        .attr("stroke-width", stroke_width)
        .attr("class", classname)
        .lower();
}

function makeCellShadow(node_group, content_object, classname) {

    return node_group.append("rect")
        .attr("x", -SHADOW_OVERSIZE)
        .attr("y", -SHADOW_OVERSIZE)
        .attr("width", content_object.getWidth() + 2 * SHADOW_OVERSIZE)
        .attr("height", content_object.getHeight() + 2 * SHADOW_OVERSIZE)
        .attr("fill", "#cccccc")
        .attr("stroke-width", "0")
        .attr("class", classname)
        // blur
        .attr("filter", "url(#white-border-inset)")
        .lower();
}


function createNode(x, y, content_data, content_type, canvas, is_bold, do_highlight,
                    draggable=true, classname=NODE_CLASSNAME) {

    let node_position = getNodePosition(x, y);

    let node_group = makeNodeGroup(canvas, node_position, classname)

    let content_object = createNodeContent(content_data, content_type, node_group, classname)

    let rect = makeNodeRectangle(is_bold, do_highlight, node_group, content_object, classname);

    return create_and_register_node_object(node_position, node_group, rect, content_object, draggable);

}

function createCell(x, y, content_data, content_type, canvas, is_bold, do_highlight,
                    draggable=true, classname=NODE_CLASSNAME) {

    let node_position = getNodePosition(x, y);

    let node_group = makeNodeGroup(canvas, node_position, classname)

    let content_object = createNodeContent(content_data, content_type, node_group, classname)

    let rect = makeCellRectangle(is_bold, do_highlight, node_group, content_object, classname)

    let shadow = makeCellShadow(node_group, content_object, classname)

    return create_and_register_node_object(node_position, node_group, rect, content_object, draggable, shadow)

}

function nodeDragged(d) {
    // console.log(node_object.registeredEdges.length)
    d.x += d3.event.dx;
    d.y += d3.event.dy;
    let registeredEdges = ALL_NODES[d3.select(this).data()[0].id].registeredEdges
    for (let i = 0; i < registeredEdges.length; i++) {
        let edge = registeredEdges[i][0]
        let edge_label = registeredEdges[i][1]
        let edge_position_data = registeredEdges[i][2]
        let graph = registeredEdges[i][3]
        edge.attr("d", d => graph.getEdgePathFromData(edge_position_data))
        edge_label.attr("x", d => graph.getEdgeLabelXFromData(edge_position_data))
                  .attr("y", d => graph.getEdgeLabelYFromData(edge_position_data))
    }
    console.log(registeredEdges.length)
    d3.select(this).attr("transform", "translate(" + d.x + "," + d.y + ")");
}


function createNodeContent(content_data, content_type, append_to_this_object, classname) {

    if (content_type == "STRING") {
        let rect_width = Node.get_hypothetical_node_width(content_data);
        let rect_height = 30;
        let text_object = append_to_this_object.append("text")
            .attr("text-anchor", "middle")
            .attr("x", rect_width/2)
            .attr("y", rect_height/2)
            .attr("dy", ".3em")
            .style("pointer-events", "none")
            .attr("class", classname)
            .text(content_data)
        return new NodeStringContent(text_object, rect_width, rect_height)
    } else if (content_type == "GRAPH" || content_type == "TREE") {
        return new Graph(0, 0, content_data, append_to_this_object, false,
            GRAPH_LABEL_MARGIN)
    }

}

class NodeStringContent {
    constructor(text_object, width, height) {
        this.text_object = text_object
        this.width = width
        this.height = height
    }

    recenter(new_width) {
        this.width = new_width
        this.text_object.attr("x", new_width/2)
    }

    getWidth() {
        return this.width
    }

    getHeight() {
        return this.height
    }
}
