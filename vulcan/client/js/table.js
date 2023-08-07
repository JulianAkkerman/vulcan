TOKEN_CLASSNAME = "token_obj"
TOKEN_DISTANCE = 5



class Table {
    constructor(top_left_x, top_left_y, content, canvas, label_alternatives, highlights) {
        this.top_left_x = top_left_x
        this.top_left_y = top_left_y
        this.tokens = []
        this.canvas = canvas
        this.label_alternatives = label_alternatives
        this.highlights = highlights
        this.create_tokens(content)
    }

    create_tokens(content) {
        let current_x = this.top_left_x
        let current_y = this.top_left_y
        // We do the rows such that the first row is at the bottom, because this is more intuitive for the tagging
        //  scenario
        for (let c = 0; c < content.length; c++) {
            let column = content[c]
            let max_width = 0
            let cells_here = []
            for (let r = column.length-1; r >= 0 ; r--) {
                let cell_here = this.create_cell_node(column[r], current_x, current_y, [c, r])
                cells_here.push(cell_here)
                current_y = current_y + parseFloat(cell_here.getHeight()) + TOKEN_DISTANCE
                let width_here = parseFloat(cell_here.getWidth())
                max_width = Math.max(max_width, width_here)
                this.tokens.push(cell_here)
            }
            // set all widths to max_width
            for (let i = 0; i < cells_here.length; i++) {
                cells_here[i].setWidth(max_width)
            }
            current_y = this.top_left_y
            current_x = current_x + max_width + TOKEN_DISTANCE
        }
    }

    create_cell_node(token, pos_x, pos_y, node_name) {
        let do_highlight = this.highlights != null && this.highlights.includes(node_name)
        let node = createCell(pos_x, pos_y, token, "STRING", this.canvas, false, do_highlight,
            false, TOKEN_CLASSNAME)
        this.register_mouseover_highlighting(node)
        if (this.label_alternatives != null) {
            this.registerNodeAlternativeMouseover(node, this.label_alternatives[node_name])
        }
        return node
    }

    register_mouseover_highlighting(node_object) {
        let current_stroke_width = parseInt(node_object.rectangle.style("stroke-width"))
        let bold_stroke_width = current_stroke_width + 2
        node_object.rectangle.on("mouseover", function() {
                node_object.rectangle.style("stroke-width", bold_stroke_width)
            })
            .on("mouseout", function() {
                node_object.rectangle.style("stroke-width", current_stroke_width)
            })
    }

    registerNodesGlobally(canvas_name) {
        let dict_here = {}
        for (let i = 0; i < this.tokens.length; i++) {
            dict_here[i] = this.tokens[i]
        }
        canvas_name_to_node_name_to_node_dict[canvas_name] = dict_here
    }

    registerNodeAlternativeMouseover(node_object, node_label_alternatives) {
        let strings_object = this

        node_object.rectangle.on("mouseover.node_alternative", function() {
                current_mouseover_node = node_object
                current_mouseover_canvas = strings_object.canvas
                current_mouseover_label_alternatives = node_label_alternatives
            // check if alt key is currently pressed
                if (d3.event.ctrlKey) {
                    show_label_alternatives(node_object, node_label_alternatives, strings_object.canvas)
                }
            })
            .on("mouseout.node_alternative", function() {
                current_mouseover_node = null
                current_mouseover_canvas = null
                current_mouseover_label_alternatives = null
                if (d3.event.ctrlKey) {
                    hide_label_alternatives(strings_object.canvas)
                }
            })
        // this below does not seem to be working
            // .on("keydown.node_alternative", function() {
            //     if (d3.event.keyCode == 18) {
            //         show_label_alternatives(node_object, null, graph_object.canvas)
            //     }
            // })
            // .on("keyup.node_alternative", function() {
            //     if (d3.event.keyCode == 18) {
            //         hide_label_alternatives(graph_object.canvas)
            //     }
            // })
    }
}