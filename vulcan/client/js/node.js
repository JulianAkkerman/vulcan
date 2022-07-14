NODE_CLASSNAME = "node"

class Node {
    constructor(node_position, group, rectangle, content) {
        this.position = node_position[0]
        this.group = group
        this.rectangle = rectangle
        this.content = content
    }

    getWidth() {
        return this.rectangle.attr("width")
    }

    static get_hypothetical_node_width(node_label) {
        return node_label.length*6.5 + 22
    }

    getHeight() {
        try {
            return content.getHeight()
        } catch (e) {
            return 30
        }
    }

    getX() {
        return this.position.x
    }

    getY() {
        return this.position.y
    }

}


function createNode(x, y, content_data, content_type, canvas, classname=NODE_CLASSNAME) {
    var node_position = [{ x: x, y: y }];

    let node_group = canvas.data(node_position).append("g")
        .attr("transform", function (d) { return "translate(" + d.x + "," + d.y + ")"; })
        .attr("class", classname)

    let content_object = create_node_content(content_data, content_type, node_group, classname)

    let rect = node_group.append("rect")
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", rect_width)
        .attr("height", rect_height)
        .attr("fill", "white")
        .attr("stroke", "black")
        .attr("stroke-width", "2")
        .attr("class", classname)

    // var nodeDragHandler = d3.drag()
    //     .on('drag', nodeDragged);

    // nodeDragHandler(node_group);

    let node_object = new Node(node_position, node_group, rect, content_object)


    return node_object
}

function nodeDragged(d) {
    d.x += d3.event.dx;
    d.y += d3.event.dy;
    d3.select(this).attr("transform", "translate(" + d.x + "," + d.y + ")");
}


function create_node_content(content_data, content_type, append_to_this_object, classname) {



    if (content_type == "STRING") {
        var rect_width = Node.get_hypothetical_node_width(text);
        var rect_height = 30;
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
        return createGraph(0, 0, content_data, append_to_this_object)
    }

}

class NodeStringContent {
    constructor(text_object, width, height) {
        this.text_object = text_object
        this.width = width
        this.height = height
    }

    getWidth() {
        return this.width
    }

    getHeight() {
        return this.height
    }
}
