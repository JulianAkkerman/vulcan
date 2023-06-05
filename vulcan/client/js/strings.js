TOKEN_CLASSNAME = "token_obj"
TOKEN_DISTANCE = 10



class Strings {
    constructor(top_left_x, top_left_y, tokens, canvas, label_alternatives, highlights) {
        this.top_left_x = top_left_x
        this.top_left_y = top_left_y
        this.tokens = []
        this.canvas = canvas
        this.label_alternatives = label_alternatives
        this.highlights = highlights
        this.create_tokens(tokens)
    }

    create_tokens(tokens) {
        let current_x = this.top_left_x
        for (let i = 0; i < tokens.length; i++) {
            let token_here = this.create_token_node(tokens[i], current_x, i)
            current_x = current_x + parseFloat(token_here.getWidth()) + TOKEN_DISTANCE
            this.tokens.push(token_here)
        }
    }

    create_token_node(token, pos_x, i) {
        let do_highlight = this.highlights != null && this.highlights.includes(i)
        let node = createNode(pos_x, this.top_left_y, token, "STRING", this.canvas, false, do_highlight,
            false, TOKEN_CLASSNAME)
        this.register_mouseover_highlighting(node)
        if (this.label_alternatives != null) {
            this.registerNodeAlternativeMouseover(node, this.label_alternatives[i])
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