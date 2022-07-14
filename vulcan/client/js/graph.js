NODE_BUFFER_WIDTH = 30
NODE_LEVEL_HEIGHT = 70
BACKGROUND_CLASSNAME = "backgroundbox"
EDGE_CLASSNAME = "edge"
EDGE_COLOR = "#000080"
REENTRANT_EDGE_COLOR = "#7777FF"


class Graph {
    constructor(top_left_x, top_left_y, graph_as_dict, canvas, draw_boundary_box=true, margin=0) {
        this.margin = margin
        this.node_dict = {};
        this.box_position_dict = {};
        this.graph_as_dict = graph_as_dict
        this.create_all_nodes(canvas)
        this.compute_node_positions(top_left_x, top_left_y)
        if (draw_boundary_box) {
            this.draw_boundary_box(canvas, top_left_x, top_left_y)
        }
        this.draw_graph(canvas)
    }

    compute_node_positions(top_left_x, top_left_y) {
        this.set_total_widths_bottom_up()
        this.set_positions_top_down(top_left_x, top_left_y)
    }

    draw_graph(canvas) {
        this.shift_nodes_to_their_positions()
        this.drawEdges(canvas)
    }

    static visit_graph_as_dict_bottom_up(subgraph_as_dict, visitor) {
        let results = []
        subgraph_as_dict["child_nodes"].forEach(child => {
            results.push(Graph.visit_graph_as_dict_bottom_up(child, visitor))
        })
        return visitor(subgraph_as_dict, results)
    }

    static visit_graph_as_dict_top_down(subgraph_as_dict, visitor) {
        visitor(subgraph_as_dict)
        subgraph_as_dict["child_nodes"].forEach(child => {
            Graph.visit_graph_as_dict_top_down(child, visitor)
        })
    }

    set_total_widths_bottom_up() {
        this.total_widths_dict = {};
        Graph.visit_graph_as_dict_bottom_up(this.graph_as_dict, (current_node, child_widths) => {
                if (current_node.is_reentrancy) {
                    return -NODE_BUFFER_WIDTH; // to compensate for the NODE_BUFFER_WIDTH we add for each child, could be cleaner
                } else {
                    let width_here = child_widths.reduce((a, b) => a + b, 0) + NODE_BUFFER_WIDTH * (child_widths.length - 1);
                    width_here = Math.max(width_here, this.node_dict[current_node.node_name].getWidth())
                    this.total_widths_dict[current_node.node_name] = width_here
                    return width_here
                }
            })
    }

    set_positions_top_down(top_left_x, top_left_y) {
        let root_node_name = this.graph_as_dict.node_name
        this.box_position_dict[root_node_name] = {x: top_left_x + this.margin, y: top_left_y + this.margin}
        // set values for all children
        Graph.visit_graph_as_dict_top_down(this.graph_as_dict, (current_node) => {
            if (!current_node.is_reentrancy) {
                let current_node_x = this.box_position_dict[current_node.node_name].x
                let current_node_y = this.box_position_dict[current_node.node_name].y
                let running_child_width_total = 0
                current_node["child_nodes"].forEach(child => {
                    if (!child.is_reentrancy) {
                        let child_width = this.total_widths_dict[child.node_name]
                        this.box_position_dict[child.node_name] = {
                            x: current_node_x + running_child_width_total, // left border position
                            y: current_node_y + this.node_dict[current_node.node_name].getHeight() + NODE_BUFFER_WIDTH
                        }
                        running_child_width_total += child_width + NODE_BUFFER_WIDTH
                    }
                })
            }
        })
    }

    create_all_nodes(canvas) {
        Graph.visit_graph_as_dict_top_down(this.graph_as_dict, (current_node) => {
            if (!current_node.is_reentrancy) {
                let label = current_node.node_label
                let is_bold = current_node.node_name == this.graph_as_dict.node_name
                let node_object = createNode(50, 50, label, current_node.label_type, canvas, is_bold)
                this.node_dict[current_node.node_name] = node_object
                this.registerNodeMouseoverNodeHighlighting(node_object)
            }
        })
    }

    shift_nodes_to_their_positions() {
        Graph.visit_graph_as_dict_top_down(this.graph_as_dict, (current_node) => {
            if (!current_node.is_reentrancy) {
                let y = this.box_position_dict[current_node.node_name].y
                let x = this.get_centered_left_border_for_node(current_node)
                this.node_dict[current_node.node_name].translate(x,y)
            }
        })
    }

    get_centered_left_border_for_node(node_as_dict) {
        let left_box_border = this.box_position_dict[node_as_dict.node_name].x
        let box_width= this.total_widths_dict[node_as_dict.node_name]
        let node_width = this.node_dict[node_as_dict.node_name].getWidth()
        return left_box_border + (box_width / 2) - (node_width / 2)
    }

    getWidth() {
        return this.total_widths_dict[this.graph_as_dict.node_name] + 2 * this.margin
    }

    getHeight() {
        return this.getBottomY() - this.box_position_dict[this.graph_as_dict.node_name].y + 2 * this.margin
    }

    getBottomY() {
        let allBottomYs = []
        Object.keys(this.node_dict).forEach(node_name => {
            allBottomYs.push(this.box_position_dict[node_name].y + this.node_dict[node_name].getHeight())
        })
        return Math.max(...allBottomYs)
    }

    draw_boundary_box(canvas, top_left_x, top_left_y) {
        const arr = Object.keys( this.box_position_dict )
            .map(key => this.box_position_dict[key].y + this.node_dict[key].getHeight());
        const height = Math.max.apply( null, arr ) - top_left_y;
        // draw white box around graph with NODE_BUFFER_WIDTH as margin
        canvas.append("rect")
            .attr("x", top_left_x - NODE_BUFFER_WIDTH)
            .attr("y", top_left_y - NODE_BUFFER_WIDTH)
            .attr("width", this.total_widths_dict[this.graph_as_dict.node_name] + 2 * NODE_BUFFER_WIDTH)
            .attr("height",  height + 2 * NODE_BUFFER_WIDTH)
            .attr("fill", "white")
            .attr("class", BACKGROUND_CLASSNAME)
            .lower()
        // inner box showing actual boundaries (no margin)
        // canvas.append("rect")
        //     .attr("x", top_left_x)
        //     .attr("y", top_left_y)
        //     .attr("width", this.total_widths_dict[this.graph_as_dict.node_name])
        //     .attr("height",  height)
        //     .attr("fill", '#eeeeee')
    }

    drawEdges(canvas) {
        Graph.visit_graph_as_dict_top_down(this.graph_as_dict, currentNode => {
            currentNode.child_nodes.forEach(child => {
                let edge_position_data = {
                    parentNode: this.node_dict[currentNode.node_name],
                    childNode: this.node_dict[child.node_name],
                    edge_label: child.incoming_edge,
                    is_reentrancy: child.is_reentrancy,
                    parentBoxWidth: this.total_widths_dict[currentNode.node_name],
                    childBoxWidth: this.total_widths_dict[child.node_name]
                }
                let edge_object = this.draw_edge_from_data(canvas, edge_position_data);
                let edge_label_object = this.draw_edge_label_from_data(canvas, edge_position_data);
                this.registerEdgeMouseover(edge_object, edge_label_object)
                this.registerNodeMouseoverEdgeHighlighting(this.node_dict[currentNode.node_name], edge_object, edge_label_object)
                this.registerNodeMouseoverEdgeHighlighting(this.node_dict[child.node_name], edge_object, edge_label_object)
            })
        })
    }

    draw_edge_label_from_data(canvas, edge_position_data) {
        let color = edge_position_data.is_reentrancy ? REENTRANT_EDGE_COLOR : EDGE_COLOR
        return canvas.append("text").data([edge_position_data])
            .text(d => d.edge_label)
            .attr("x", d => this.getEdgeLabelXFromData(d))
            .attr("y", d => this.getEdgeLabelYFromData(d))
            .style("font-size", "9px")
            .style('fill', color)
            // .style("pointer-events", "none")
            .style("user-select", "none")
            .attr("class", EDGE_CLASSNAME)
    }

    EDGE_LABEL_CLOSE_RANGE = 100
    EDGE_LABEL_FAR_RANGE = 350

    getEdgeLabelXFromData(edge_position_data) {
        let p = edge_position_data.parentNode
        let c = edge_position_data.childNode
        let distance = c.getX() + c.getWidth()/2 - p.getX() - p.getWidth()/2 // negative if child is to the left
        if (distance < -this.EDGE_LABEL_FAR_RANGE) {
            // child is far to the left, we put label above edge close to child
            return (c.getX() + c.getWidth()/2)
        } else if (distance < -this.EDGE_LABEL_CLOSE_RANGE) {
            //child is medium to the left, we put label below middle of edge
            return (p.getX() + p.getWidth()/2 + c.getX() + c.getWidth()/2)/2-10 // -10 compensates to quasi-center text
        } else if (distance < this.EDGE_LABEL_CLOSE_RANGE) {
            // child is nearly centered, we put label left of middle of edge
            return (p.getX() + p.getWidth()/2 + c.getX() + c.getWidth()/2)/2 + 10  + distance/3 // + 10 just to get a bit of distance
        } else if (distance < this.EDGE_LABEL_FAR_RANGE) {
            // child is medium to the right, we put label above middle of edge
            return (p.getX() + p.getWidth()/2 + c.getX() + c.getWidth()/2)/2+5
        } else {
            // child is far to the right, we put label above edge close to child
            return (c.getX() + c.getWidth()/2)-20
        }
    }

    getEdgeLabelYFromData(edge_position_data) {
        let p = edge_position_data.parentNode
        let c = edge_position_data.childNode
        let yShift = 0
        if (edge_position_data.is_reentrancy && !this.childIsBelowParent(edge_position_data)) {
            yShift = NODE_LEVEL_HEIGHT
        }
        let baseY;
        let distance = c.getX() + c.getWidth()/2 - p.getX() - p.getWidth()/2 // negative if child is to the left
        if (distance < -this.EDGE_LABEL_FAR_RANGE) {
            // child is far to the left, we put label above edge close to child
            baseY = c.getY() - 25
        } else if (distance < -this.EDGE_LABEL_CLOSE_RANGE) {
            //child is medium to the left, we put label below middle of edge
            baseY = (p.getY() + p.getHeight() + c.getY()) / 2 + 5 // +20 to be below center
        } else if (distance < this.EDGE_LABEL_CLOSE_RANGE) {
            // child is nearly centered, we put label left of middle of edge
            baseY = (p.getY() + p.getHeight() + c.getY()) / 2
        } else if (distance < this.EDGE_LABEL_FAR_RANGE) {
            // child is medium to the right, we put label above middle of edge
            baseY = (p.getY() + p.getHeight() + c.getY()) / 2 - 15 // -20 to be above center
        } else {
            // child is far to the right, we put label above edge close to child
            baseY = c.getY() - 25
        }
        return baseY + yShift
    }

    draw_edge_from_data(canvas, edge_position_data, ) {
        let color = edge_position_data.is_reentrancy ? REENTRANT_EDGE_COLOR : EDGE_COLOR
        return canvas.append("path").data([edge_position_data])
            .attr("shape-rendering", "geometricPrecision")
            .style("stroke", color)
            .style("stroke-width", 1.5)
            .style("fill", "none")
            .attr("marker-end", marker(color, canvas))
            .attr("d", d => this.getEdgePathFromData(d))
            .attr("class", EDGE_CLASSNAME)
    }

    registerEdgeMouseover(edge_object, edge_label_object) {
        this.registerEdgeHighlightingOnObjectMouseover(edge_object, edge_object, edge_label_object)
        this.registerEdgeHighlightingOnObjectMouseover(edge_label_object, edge_object, edge_label_object)
    }

    registerEdgeHighlightingOnObjectMouseover(object, edge_object, edge_label_object, stroke_width=4) {
        object.on("mouseover.edge"+create_alias(), function() {
                edge_object.style("stroke-width", stroke_width)
                edge_label_object.style("font-size", "15px")
                edge_label_object.style("font-weight", "bold")
            })
            .on("mouseout.edge"+create_alias(), function() {
                edge_object.style("stroke-width", 1.5)
                edge_label_object.style("font-size", "9px")
                edge_label_object.style("font-weight", "normal")
            })
    }

    registerNodeHighlightingOnObjectMouseover(object, node_object) {
        object.on("mouseover", function() {
                node_object.rectangle.style("stroke-width", 4)
            })
            .on("mouseout", function() {
                node_object.rectangle.style("stroke-width", 2)
            })
    }


    registerNodeMouseoverNodeHighlighting(node_object) {
        this.registerNodeHighlightingOnObjectMouseover(node_object.rectangle, node_object)
    }


    registerNodeMouseoverEdgeHighlighting(node_object, edge_object, edge_label_object) {
        this.registerEdgeHighlightingOnObjectMouseover(node_object.rectangle, edge_object, edge_label_object, 3)
    }

    getEdgePathFromData(edge_position_data) {
        if (edge_position_data.is_reentrancy) {
            let startpoint = this.getReentrancyStartPoint(edge_position_data)
            let endpoint = this.getReentrancyEndPoint(edge_position_data)
            let edge = d3.path()
            edge.moveTo(startpoint.x, startpoint.y)
            if (this.childIsBelowParent(edge_position_data)) {
                let verticalCenter = (startpoint.y+endpoint.y) / 2
                edge.bezierCurveTo(startpoint.x, verticalCenter, endpoint.x, startpoint.y, endpoint.x, endpoint.y)
            } else {
                edge.bezierCurveTo(startpoint.x, startpoint.y + NODE_LEVEL_HEIGHT / 2,
                    endpoint.x, endpoint.y + NODE_LEVEL_HEIGHT / 2,
                    endpoint.x, endpoint.y)
            }
            return edge
        } else {
            let startpoint = this.getEdgeStartPoint(edge_position_data)
            let endpoint = this.getEdgeEndPoint(edge_position_data)
            let edge = d3.path()
            edge.moveTo(startpoint.x, startpoint.y)
            let verticalCenter = (startpoint.y+endpoint.y) / 2
            edge.bezierCurveTo(startpoint.x, verticalCenter, endpoint.x, startpoint.y, endpoint.x, endpoint.y)
            return edge
        }
    }




    getEdgeStartPoint(edge_position_data) {
        let xDistRatio = this.getXDistRation(edge_position_data.parentNode, edge_position_data.childNode, edge_position_data.parentBoxWidth)
        return {
            x: edge_position_data.parentNode.getX() + edge_position_data.parentNode.getWidth() * (0.5 + xDistRatio),
            y: edge_position_data.parentNode.getY() + edge_position_data.parentNode.getHeight()
        }
    }

    getEdgeEndPoint(edge_position_data) {
        return {
            x: edge_position_data.childNode.getX() + edge_position_data.childNode.getWidth() * 0.5,
            y: edge_position_data.childNode.getY()
        }
    }


    getReentrancyStartPoint(edge_position_data) {
        let xDistRatio = this.getXDistRation(edge_position_data.parentNode, edge_position_data.childNode, this.getWidth()*2)
        return {
            x: edge_position_data.parentNode.getX() + edge_position_data.parentNode.getWidth() * (0.5 + xDistRatio),
            y: edge_position_data.parentNode.getY() + edge_position_data.parentNode.getHeight()
        }
    }

    getReentrancyEndPoint(edge_position_data) {
        let xDistRatio = this.getXDistRation(edge_position_data.childNode, edge_position_data.parentNode, this.getWidth()*2)
        let endPointX = edge_position_data.childNode.getX() + edge_position_data.childNode.getWidth() * (0.5 + xDistRatio)
        if (this.childIsBelowParent(edge_position_data)) {
            return {
                x: endPointX,
                y: edge_position_data.childNode.getY()
            }
        } else {
            return {
                x: endPointX,
                y: edge_position_data.childNode.getY() + edge_position_data.childNode.getHeight()
            }
        }
    }


    childIsBelowParent(edge_position_data) {
        return edge_position_data.childNode.getY() >
            edge_position_data.parentNode.getY()+edge_position_data.parentNode.getHeight()
    }

    getXDistRation(mainNode, referenceNode, normalizingFactor) {
        return (referenceNode.getX()+referenceNode.getWidth()/2 - mainNode.getX() - mainNode.getWidth()/2)/normalizingFactor
    }




}

let alias = 0
function create_alias() {
    alias += 1
    return alias
}


function createGraph(top_left_x, top_left_y, graph_as_dict, canvas, draw_boundary_box=true, margin=0) {

    return new Graph(top_left_x, top_left_y, graph_as_dict, canvas, draw_boundary_box, margin)


}
