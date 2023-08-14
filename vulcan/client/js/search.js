

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

let searchWindowVisible = false
let searchWindowContainer = null
let searchWindowCanvas = null

// pastel green, pastel blue, pastel yellow, pastel orange, pastel red, pastel purple
const FILTER_COLORS = ["#b3ffb3", "#b3ffff", "#ffffb3", "#ffb366", "#ff9999", "#e6ccff"]
const BORDER_COLOR = "#444444"
const SEARCH_WINDOW_WIDTH = 500
const SEARCH_WINDOW_HEIGHT = 400
const FILTER_SELECTOR_SIZE = 40

let searchFilters


function initializeSearchFilters() {
    searchFilters = [new FilterInfo(null, null, [])]
}

function createSearchWindowContainer() {
    // get the position of the search icon
    let searchButtonPosition = d3.select("#searchButton").node().getBoundingClientRect()
    let searchButtonHeight = searchButtonPosition.height
    let searchButtonX = searchButtonPosition.x
    let searchButtonY = searchButtonPosition.y

    console.log(searchButtonY + searchButtonHeight + 10)
    console.log(searchButtonX)


    searchWindowVisible = true
    searchWindowContainer = d3.select("div#chartId")
        .append("div")
        .style("position", "absolute")
        .style("top", (searchButtonY + searchButtonHeight + 5).toString() + "px")
        .style("left", searchButtonX.toString() + "px")
    // .style("border", "3px solid black")
}

function createSearchWindowCanvas() {
    searchWindowCanvas = searchWindowContainer.append("svg")
        .attr("viewBox", "0 0 " + SEARCH_WINDOW_WIDTH + " " + SEARCH_WINDOW_HEIGHT)
        .attr("width", SEARCH_WINDOW_WIDTH)  // that's 3 + 3 for the borders, I think, but I don't know where the 10 come from
        .attr("height", SEARCH_WINDOW_HEIGHT)
        .style("background-color", "white")
        .style("border", "2px solid " + BORDER_COLOR)
        .style("position", "relative")
}

function onSearchIconClick() {
    if (!searchWindowVisible) {
        createSearchWindowContainer();

        createSearchWindowCanvas();

        // create visuals for active filter
        let activeFilter = searchFilters[0]
        let activeFilterSelector = searchWindowCanvas.append("g")
            .attr("id", "activeFilterSelector")
            .attr("transform", "translate(0, 0)")
        let activeFilterSelectorRect = activeFilterSelector.append("rect")
            .attr("rx", 5)
            .attr("ry", 5)
            .attr("x", 15)
            .attr("y", 15)
            .attr("width", FILTER_SELECTOR_SIZE)
            .attr("height", FILTER_SELECTOR_SIZE)
            .attr("fill", FILTER_COLORS[0])
            .attr("stroke", BORDER_COLOR)
            .attr("stroke-width", 2)

        let m = 10
        let s = 10
        console.log(activeFilterSelectorRect.attr("x"))
        let leftBoundary = parseFloat(activeFilterSelectorRect.attr("x")) + FILTER_SELECTOR_SIZE + m
        console.log("leftBoundary: " + leftBoundary)
        let lowerCornerOfSelector = parseFloat(activeFilterSelectorRect.attr("y")) + FILTER_SELECTOR_SIZE + 5
        console.log("lowerCornerOfSelector: " + lowerCornerOfSelector)
        // should be able to generalize the below, by setting it up for a middle one, and not drawing a line if its length is negative.
        drawLine(m, m, SEARCH_WINDOW_WIDTH-m, m, s, 0)
        drawCorner(SEARCH_WINDOW_WIDTH-m, m, -s, 0, 0, s)
        drawLine(SEARCH_WINDOW_WIDTH-m, m, SEARCH_WINDOW_WIDTH-m, SEARCH_WINDOW_HEIGHT-m, 0, s)
        drawCorner(SEARCH_WINDOW_WIDTH-m, SEARCH_WINDOW_HEIGHT-m, 0, -s, -s, 0)
        drawLine(SEARCH_WINDOW_WIDTH-m, SEARCH_WINDOW_HEIGHT-m, leftBoundary, SEARCH_WINDOW_HEIGHT-m, -s, 0)
        drawCorner(leftBoundary, SEARCH_WINDOW_HEIGHT-m, s, 0, 0, -s)
        drawLine(leftBoundary, SEARCH_WINDOW_HEIGHT-m, leftBoundary, lowerCornerOfSelector, 0, -s)
        drawCorner(leftBoundary, lowerCornerOfSelector, 0, s, -s, 0)
        drawLine(leftBoundary, lowerCornerOfSelector, m, lowerCornerOfSelector, -s, 0)
        drawCorner(m, lowerCornerOfSelector, s, 0, 0, -s)
        drawLine(m, lowerCornerOfSelector, m, m, 0, -s)
        drawCorner(m, m, 0, s, s, 0)


    } else {
        searchWindowVisible = false
        searchWindowContainer.remove()
    }
}

function drawLine(x1, y1, x2, y2, xShortening, yShortening) {
    // assumes that x2 >= x1 and y2 >= y1
    x1 = x1 + xShortening
    x2 = x2 - xShortening
    y1 = y1 + yShortening
    y2 = y2 - yShortening
    searchWindowCanvas.append("line")
        .attr("x1", x1)
        .attr("y1", y1)
        .attr("x2", x2)
        .attr("y2", y2)
        .attr("stroke", BORDER_COLOR)
        .attr("stroke-width", 2)
}

function drawCorner(xCorner, yCorner, xOffsetIn, yOffsetIn, xOffsetOut, yOffsetOut) {
    let edge = d3.path()
    let x1 = xCorner + xOffsetIn
    let y1 = yCorner + yOffsetIn
    let x2 = xCorner + xOffsetOut
    let y2 = yCorner + yOffsetOut
    edge.moveTo(x1, y1)
    edge.bezierCurveTo(xCorner, yCorner, xCorner, yCorner, x2, y2)
    searchWindowCanvas.append("path")
        .attr("d", edge)
        .attr("stroke", BORDER_COLOR)
        .attr("stroke-width", 2)
        .attr("fill", "none")
}

class FilterInfo {
    constructor(slice_name, outer_layer_id, inner_layer_ids) {
        this.slice_name = slice_name
        this.outer_layer_id = outer_layer_id
        this.inner_layer_ids = inner_layer_ids
    }
}