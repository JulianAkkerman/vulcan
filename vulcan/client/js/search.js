

const SEARCH_PATTERNS = {
    "Sentence": [
         {
             "id": "OuterTableCellsLayer",
             "innerLayers": [
                 {
                     "id": "CellContentEquals",
                     "label": ["Cell content equals", ""],
                     "description": "This checks if the cell content equals the given string (modulo casing and outer whitespace)."
                 }
             ],
             "label": "Any cell in the table matches:",
             "description": "This layer checks if any cell in a table matches the given criteria, and highlights the cells that do."
         },
        {
             "id": "OuterTableAsAWholeLayer",
             "innerLayers": [
                 {
                     "id": "ColumnCountAtLeast",
                     "label": ["The sentence has at least length ", " (or the table has at least this many columns)"],
                     "description": "Checks minimum sentence length / table width."
                 }
             ],
             "label": "The sentence/table as a whole matches:",
             "description": "This layer checks if the sentence (or table) itself matches a given criterion."
         }
    ],
    "Tree": [
         {
             "id": "OuterGraphNodeLayer",
             "innerLayers": [
                 {
                     "id": "NodeContentEquals",
                     "label": ["Node has label", ""],
                     "description": "This checks if a node is labeled with the given string (modulo casing and outer whitespace)."
                 }
             ],
             "label": "Any node in the graph matches:",
             "description": "This layer checks if any node in a graph matches the given criteria, and highlights the nodes that do."
         }
    ]
}

var searchWindowVisible = false
var searchWindowContainer = null
var searchWindowCanvas = null


function onSearchIconClick() {
    if (!searchWindowVisible) {

        // get the position of the search icon
        let searchButtonPosition = d3.select("#searchButton").node().getBoundingClientRect()
        let searchButtonWidth = searchButtonPosition.width
        let searchButtonHeight = searchButtonPosition.height
        let searchButtonX = searchButtonPosition.x
        let searchButtonY = searchButtonPosition.y

        console.log(searchButtonY + searchButtonHeight + 10)
        console.log(searchButtonX)

        let width = 500
        let height = 400

        searchWindowVisible = true
        searchWindowContainer = d3.select("div#chartId")
            .append("div")
            .style("position", "absolute")
            // the positioning of the canvas seems to add a bit of a buffer; counteracting some of that here.
            .style("top", (searchButtonY + searchButtonHeight - 5).toString() + "px")
            .style("left", searchButtonX.toString() + "px")
            // .style("border", "3px solid black")

        searchWindowCanvas = searchWindowContainer.append("svg")
            .attr("preserveAspectRatio", "xMinYMin meet")
            .attr("viewBox", "0 0 " + 100 + " " + 50)
            .attr("width", 500)  // that's 3 + 3 for the borders, I think, but I don't know where the 10 come from
            .attr("height", 400)
            .classed("svg-content-responsive", true)
            .style("background-color", "white")
            .style("border", "2px solid #444444")
            .style("position", "relative")
    } else {
        searchWindowVisible = false
        searchWindowContainer.remove()
    }
}