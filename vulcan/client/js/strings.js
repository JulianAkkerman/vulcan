TOKEN_CLASSNAME = "token_obj"
TOKEN_DISTANCE = 10



class Strings {
    constructor(top_left_x, top_left_y, tokens, canvas) {
        this.top_left_x = top_left_x
        this.top_left_y = top_left_y
        this.tokens = []
        this.create_tokens(tokens, canvas)
    }

    create_tokens(tokens, canvas) {
        let current_x = this.top_left_x
        for (let i = 0; i < tokens.length; i++) {
            let token_here = this.create_token_node(tokens[i], current_x, canvas)
            current_x = current_x + parseFloat(token_here.getWidth()) + TOKEN_DISTANCE
            this.tokens.push(token_here)
        }
    }

    create_token_node(token, x, canvas) {
        let node = createNode(x, this.top_left_y, token, "STRING", canvas, false, TOKEN_CLASSNAME)
        this.register_mouseover_highlighting(node)
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
}