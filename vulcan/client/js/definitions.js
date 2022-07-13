// define arrow shape
arrowLength = 7
arrowWidth = 7
refX = -1
refY = 0

visualization_types = ["STRING", "TREE", "GRAPH"]

centerThickness = 5
arrowPoints = [[0, 0],  //tip
            [-arrowLength, -arrowWidth/2],
            [-centerThickness, 0],
            [-arrowLength, arrowWidth/2],
        ]

// old convoluted shape (but nice try!)
// centerWidthFactor = 0.3
// frontStrokeWidthFactor = 0.3
// frontSideLiftFactor = 0.6
// backDentFactor = 0.7
// offCenterFrontBackoff = frontStrokeWidthFactor+(centerWidthFactor*2)*frontSideLiftFactor
// arrowPoints = [[0, 0],//tip
//     [-arrowLength*frontSideLiftFactor, -arrowWidth/2],
//     [-arrowLength*(frontSideLiftFactor+frontStrokeWidthFactor), -arrowWidth/2],
//     [-arrowLength*offCenterFrontBackoff, -arrowWidth*centerWidthFactor],
//     [-arrowLength, -arrowWidth*centerWidthFactor],
//     [-arrowLength*backDentFactor, 0],
//     [-arrowLength, arrowWidth*centerWidthFactor],
//     [-arrowLength*offCenterFrontBackoff, arrowWidth*centerWidthFactor],
//     [-arrowLength*(frontSideLiftFactor+frontStrokeWidthFactor), arrowWidth/2],
//     [-arrowLength*frontSideLiftFactor, arrowWidth/2]]

function marker(color) {
        let id = "arrowhead"+color.replace("#", "")
        canvas
            .append('marker')
            .attr("id", id)
            .attr('viewBox', [-arrowLength, -arrowWidth/2, arrowLength, arrowWidth])
            .attr('markerWidth', arrowWidth)
            .attr('markerHeight', arrowLength)
            .attr('refX', refX)
            .attr('refY', refY)
            .attr('orient', 'auto-start-reverse')
            .append('path')
            .attr("shape-rendering", "geometricPrecision")
            .attr("d", d3.line()(arrowPoints))
            .style("fill", color);

        return "url(#" + id + ")";
      }