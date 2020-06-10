var mood = function(e){
  var weeksInMonth = function(month){
    var m = d3.timeMonth.floor(month)
    return d3.timeWeeks(d3.timeWeek.floor(m), d3.timeMonth.offset(m,1)).length;
  };

  var minDate = minDate = new Date(yr, mo - 1, 1);
  var maxDate = maxDate = new Date(yr, mo - 1, 2);
  var colors = ['#ffb6e6', '#a3dbff', '#71ffda', '#feffb2', '#ffd177', '#ff5b5b'];
  var moods = {0: 'happy/joyful/content/relax', 1: 'sad/lonely/depressed/insecure',
               2: 'productive/motivated/alive/excited', 3: 'sick/tired/bored/lazy',
               4: 'average/normal/fine/OK', 5: 'angry/anxious/fustrated/annoyed'};


  var cellMargin = 2,
      cellSize = 30;

  var day = d3.timeFormat("%w"),
      week = d3.timeFormat("%U"),
      format = d3.timeFormat("%Y-%m-%d"),
      titleFormat = d3.utcFormat("%B %d, %Y");
      monthName = d3.timeFormat("%B"),
      months = d3.timeMonth.range(minDate, maxDate),
      height = ((cellSize * 7) + (cellMargin * 8) + 20);

  var svg = d3.select("#calendar").selectAll("svg")
    .data(months)
    .enter().append("svg")
    .attr("class", "month")
    .attr("height", ((cellSize * 7) + (cellMargin * 8) + 10) ) // the 20 is for the month labels
    .attr("width", function(d) {
      var columns = weeksInMonth(d);
      return 91 + ((cellSize * columns) + (cellMargin * (columns + 1)));
    })
    .append("g")
      .attr("transform", (d, i) => `translate(40.5,0)`);

  var rect = svg.selectAll("rect.day")
    .data(function(d, i) { return d3.timeDays(d, new Date(d.getFullYear(), d.getMonth()+1, 1)); })
    .enter().append("rect")
    .attr("class", "day")
    .attr("width", cellSize)
    .attr("height", cellSize)
    .attr("rx", 3).attr("ry", 3) // rounded corners
    .attr("fill", '#eaeaea') // default light grey fill
    .attr("y", function(d) { return (day(d) * cellSize) + (day(d) * cellMargin) + cellMargin; })
    .attr("x", function(d) { return ((week(d) - week(new Date(d.getFullYear(),d.getMonth(),1))) * cellSize) + ((week(d) - week(new Date(d.getFullYear(),d.getMonth(),1))) * cellMargin) + cellMargin ; })
    .on("mouseover", function(d) {
      d3.select(this).classed('hover', true);
    })
    .on("mouseout", function(d) {
      d3.select(this).classed('hover', false);
    })
    .datum(format);

  rect.append("title")
    .text(function(d) { return titleFormat(new Date(d)); });

  svg.append("g")
        .attr("text-anchor", "end")
      .selectAll("text")
      .data((d3.range(7)).map(i => new Date(1995, 0, i)))
      .join("text")
        .attr("x", -5)
        .attr("y", d => (d.getUTCDay() + 0.5) * (cellMargin + cellSize))
        .attr("dy", "0.31em")
        .text(d => "SMTWTFS"[d.getUTCDay()]);

  var lookup = d3.nest()
    .key(function(d) { return d.date; })
    .rollup(function(leaves) {
      return d3.sum(leaves, function(d){ return parseInt(d.mood); });
    })
    .object(mood_data);

  var leg = d3.select("#legend")

  // create a list of keys
  var keys = ['happy/joyful/content/relax', 'sad/lonely/depressed/insecure',
              'productive/motivated/alive/excited', 'sick/tired/bored/lazy',
              'average/normal/fine/OK', 'angry/anxious/fustrated/annoyed']

  // Usually you have a color scale in your chart already
  var color = d3.scaleOrdinal()
    .domain(keys)
    .range(colors);

  // Add one dot in the legend for each name.
  var size = 20
  leg.selectAll("mydots")
    .data(keys)
    .enter()
    .append("rect")
      .attr("x", 100)
      .attr("y", function(d,i){ return i*(size+5)}) // 100 is where the first dot appears. 25 is the distance between dots
      .attr("width", size)
      .attr("height", size)
      .style("fill", function(d){ return color(d)})

  // Add one dot in the legend for each name.
  leg.selectAll("mylabels")
    .data(keys)
    .enter()
    .append("text")
      .attr("x", 100 + size*1.2)
      .attr("y", function(d,i){ return 5 + i*(size+5) + (size/2)}) // 100 is where the first dot appears. 25 is the distance between dots
      .text(function(d){ return d})
      .attr("text-anchor", "left")
      .style("alignment-baseline", "middle")

  var scale = d3.scaleLinear()
    .domain([0,5])
    .range([0,5]); // the interpolate used for color expects a number in the range [0,1] but i don't want the lightest part of the color scheme

  rect.filter(function(d) { return d in lookup; })
    .style("fill", function(d) {
      return colors[lookup[d]]})
    .select("title")
    .text(function(d) { return titleFormat(new Date(d)) + " : " + moods[lookup[d]]; });
}

var sleep = function(e){
  var weeksInMonth = function(month){
    var m = d3.timeMonth.floor(month)
    return d3.timeWeeks(d3.timeWeek.floor(m), d3.timeMonth.offset(m,1)).length;
  };

  var minDate = new Date(yr, mo - 1, 1);
  var maxDate = new Date(yr, mo - 1, 2);

  if (minDate === undefined || minDate.getTime() == maxDate.getTime()){
    minDate = new Date(yr, mo - 1, 1);
    maxDate = new Date(yr, mo - 1, 2);
  };

  var cellMargin = 2,
      cellSize = 30;

  var day = d3.timeFormat("%w"),
      week = d3.timeFormat("%U"),
      format = d3.timeFormat("%Y-%m-%d"),
      titleFormat = d3.utcFormat("%B %d, %Y");
      monthName = d3.timeFormat("%B"),
      months = d3.timeMonth.range(minDate, maxDate),
      height = ((cellSize * 7) + (cellMargin * 8) + 20);

  var svg = d3.select("#sleeps").selectAll("svg")
    .data(months)
    .enter().append("svg")
    .attr("class", "month")
    .attr("height", ((cellSize * 7) + (cellMargin * 8) + 10) ) // the 20 is for the month labels
    .attr("width", function(d) {
      var columns = weeksInMonth(d);
      return 91 + ((cellSize * columns) + (cellMargin * (columns + 1)));
    })
    .append("g")
      .attr("transform", (d, i) => `translate(40.5,0)`);

  var rect = svg.selectAll("rect.day")
    .data(function(d, i) { return d3.timeDays(d, new Date(d.getFullYear(), d.getMonth()+1, 1)); })
    .enter().append("rect")
    .attr("class", "day")
    .attr("width", cellSize)
    .attr("height", cellSize)
    .attr("rx", 3).attr("ry", 3) // rounded corners
    .attr("fill", '#eaeaea') // default light grey fill
    .attr("y", function(d) { return (day(d) * cellSize) + (day(d) * cellMargin) + cellMargin; })
    .attr("x", function(d) { return ((week(d) - week(new Date(d.getFullYear(),d.getMonth(),1))) * cellSize) + ((week(d) - week(new Date(d.getFullYear(),d.getMonth(),1))) * cellMargin) + cellMargin ; })
    .on("mouseover", function(d) {
      d3.select(this).classed('hover', true);
    })
    .on("mouseout", function(d) {
      d3.select(this).classed('hover', false);
    })
    .datum(format);

  rect.append("title")
    .text(function(d) { return titleFormat(new Date(d)); });

  svg.append("g")
        .attr("text-anchor", "end")
      .selectAll("text")
      .data((d3.range(7)).map(i => new Date(1995, 0, i)))
      .join("text")
        .attr("x", -5)
        .attr("y", d => (d.getUTCDay() + 0.5) * (cellMargin + cellSize))
        .attr("dy", "0.31em")
        .text(d => "SMTWTFS"[d.getUTCDay()]);

  var lookup = d3.nest()
    .key(function(d) { return d.date; })
    .rollup(function(leaves) {
      return d3.sum(leaves, function(d){ return parseInt(d.sleep); });
    })
    .object(sleep_data);

  var scale = d3.scaleLinear()
    .domain([0, d3.max(sleep_data, function(d) { return d.sleep; })])
    .range(['white','darkSlateBlue']);

  rect.filter(function(d) { return d in lookup; })
      .style("fill", function(d) { return scale(lookup[d]); })
      .select("title")
      .text(function(d) { return titleFormat(new Date(d)) + " : " + lookup[d] + " hours"; });

}
mood();
sleep();
