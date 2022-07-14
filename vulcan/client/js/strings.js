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
        return createNode(x, this.top_left_y, token, "STRING", canvas, false, TOKEN_CLASSNAME)
    }
}