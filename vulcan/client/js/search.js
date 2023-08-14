

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
const FILTER_SELECTOR_BUFFER = 15

const SELECTOR_MASK_MARGIN = 10
const SELECTOR_MASK_ROUNDING = 10
const SELECTOR_MASK_CLASSNAME = "searchSelectorMask"

let searchFilters
let searchFilterRects


function initializeSearchFilters() {
    searchFilters = [new FilterInfo(null, null, [])]
}

function addEmptySearchFilter() {
    searchFilters.push(new FilterInfo(null, null, []))
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

function drawFilterSelectorMask(activeFilterSelectorRect) {
    let indentedLeftBoundary = parseFloat(activeFilterSelectorRect.attr("x"))
        + FILTER_SELECTOR_SIZE + SELECTOR_MASK_MARGIN
    let selectorRectBottomWithMargin = parseFloat(activeFilterSelectorRect.attr("y")) + FILTER_SELECTOR_SIZE + 5
    let selectorRectTopWithMargin = parseFloat(activeFilterSelectorRect.attr("y")) - 5
    let bottom = SEARCH_WINDOW_HEIGHT - SELECTOR_MASK_MARGIN
    let right = SEARCH_WINDOW_WIDTH - SELECTOR_MASK_MARGIN
    let top = SELECTOR_MASK_MARGIN
    let left = SELECTOR_MASK_MARGIN


    // should be able to generalize the below, by setting it up for a middle one, and not drawing a line if its length is negative.
    drawXLine(indentedLeftBoundary, right, top)
    drawCornerTopRight(right, top)
    drawYLine(right, top, bottom)
    drawCornerBottomRight(right, bottom)
    drawXLine(indentedLeftBoundary, right, bottom)
    if (selectorRectBottomWithMargin < bottom - 2*SELECTOR_MASK_ROUNDING) {
        drawCornerBottomLeft(indentedLeftBoundary, bottom)
        drawYLine(indentedLeftBoundary, selectorRectBottomWithMargin, bottom)
        drawCornerTopRight(indentedLeftBoundary, selectorRectBottomWithMargin)
    } else {
        drawLine(indentedLeftBoundary, bottom, indentedLeftBoundary, selectorRectBottomWithMargin, SELECTOR_MASK_ROUNDING, 0)
    }
    drawXLine(left, indentedLeftBoundary, selectorRectBottomWithMargin)
    drawCornerBottomLeft(left, selectorRectBottomWithMargin)
    drawYLine(left, selectorRectTopWithMargin, selectorRectBottomWithMargin)
    drawCornerTopLeft(left, selectorRectTopWithMargin)
    drawXLine(left, indentedLeftBoundary, selectorRectTopWithMargin)
    if (selectorRectTopWithMargin > top + 2*SELECTOR_MASK_ROUNDING) {
        drawCornerBottomRight(indentedLeftBoundary, selectorRectTopWithMargin)
        drawYLine(indentedLeftBoundary, top, selectorRectTopWithMargin)
        drawCornerTopLeft(indentedLeftBoundary, top)
    } else {
        drawLine(indentedLeftBoundary, selectorRectTopWithMargin, indentedLeftBoundary, top, SELECTOR_MASK_ROUNDING, 0)
    }

}

function createFilterSelectorRect(filterSelectorIndex) {
    let y = 15 + filterSelectorIndex * (FILTER_SELECTOR_SIZE + FILTER_SELECTOR_BUFFER)
    let activeFilterSelector = searchWindowCanvas.append("g")
        .attr("id", "activeFilterSelector")
        .attr("transform", "translate(0, 0)")
    return activeFilterSelector.append("rect")
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("x", 15)
        .attr("y", y)
        .attr("width", FILTER_SELECTOR_SIZE)
        .attr("height", FILTER_SELECTOR_SIZE)
        .attr("fill", FILTER_COLORS[filterSelectorIndex])
        .attr("stroke", BORDER_COLOR)
        .attr("stroke-width", 2)
        .on("click", function () {
            selectSelectorRect(d3.select(this))
        })
}

function selectSelectorRect(selectorRect) {
    selectorRect.style("opacity", "1")
    for (let i = 0; i < searchFilterRects.length; i++) {
        if (searchFilterRects[i].node() !== selectorRect.node()) {
            searchFilterRects[i].style("opacity", "0.5")
        }
    }
    // select all objects of class SELECTOR_MASK_CLASSNAME and remove them
    d3.selectAll("." + SELECTOR_MASK_CLASSNAME).remove()
    drawFilterSelectorMask(selectorRect)

}

function onSearchIconClick() {
    if (!searchWindowVisible) {
        createSearchWindowContainer();

        createSearchWindowCanvas();

        // create visuals for active filter
        // let activeFilter = searchFilters[0]
        searchFilterRects = []
        for (let i = 0; i < FILTER_COLORS.length; i++) {
            searchFilterRects.push(createFilterSelectorRect(i));
        }

        drawFilterSelectorMask(searchFilterRects[3]);


    } else {
        searchWindowVisible = false
        searchWindowContainer.remove()
    }
}

function drawXLine(x1, x2, y) {
    if (x1 < x2) {
        drawLine(x1, y, x2, y, SELECTOR_MASK_ROUNDING, 0)
    }
    // else the line has "negative length" and we don't draw it.
}

function drawYLine(x, y1, y2) {
    if (y1 < y2) {
        drawLine(x, y1, x, y2, 0, SELECTOR_MASK_ROUNDING)
    }
    // else the line has "negative length" and we don't draw it.
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
        .attr("class", SELECTOR_MASK_CLASSNAME)
}


function drawCornerTopRight(xCorner, yCorner) {
    drawCorner(xCorner, yCorner, -SELECTOR_MASK_ROUNDING, 0, 0, SELECTOR_MASK_ROUNDING)
}

function drawCornerBottomRight(xCorner, yCorner) {
    drawCorner(xCorner, yCorner, 0, -SELECTOR_MASK_ROUNDING, -SELECTOR_MASK_ROUNDING, 0)
}

function drawCornerBottomLeft(xCorner, yCorner) {
    drawCorner(xCorner, yCorner, SELECTOR_MASK_ROUNDING, 0, 0, -SELECTOR_MASK_ROUNDING)
}

function drawCornerTopLeft(xCorner, yCorner) {
    drawCorner(xCorner, yCorner, 0, SELECTOR_MASK_ROUNDING, SELECTOR_MASK_ROUNDING, 0)
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
        .attr("class", SELECTOR_MASK_CLASSNAME)
}

class FilterInfo {
    constructor(slice_name, outer_layer_id, inner_layer_ids) {
        this.slice_name = slice_name
        this.outer_layer_id = outer_layer_id
        this.inner_layer_ids = inner_layer_ids
    }
}