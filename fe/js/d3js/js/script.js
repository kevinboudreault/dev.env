const svg = d3.select("#viz")
    .append("svg")
    .attr("width", 400)
    .attr("height", 200);

svg.append("text")
    .attr("x", 20)
    .attr("y", 100)
    .text("D3 is running in Docker!")
    .style("fill", "orange")
    .style("font-size", "24px")
    .style("font-family", "sans-serif");
