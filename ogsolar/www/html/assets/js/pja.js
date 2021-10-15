
/**
 * @brief Update the contents of the table from the above json file.
 * @param tableID The html table id tag. If a table header is defined
 *                it must have an html id starting with the table id 
 *                and finished with the Header text.
 *                The file on the http server containing the 
 *                table contents is <tableID>.json. This is a json file 
 *                may 
 *                - Optionally have a HEADER key which defines 
 *                the table columns. The value is this key is a list of 
 *                text strings (one for each column title).
 *                It must have the key = 0 of which the value is a 
 *                list, one element for each column value.
 *                other keys 1,2,3 etc (must be incrementing integer 
 *                values) contain lists of values of other rows in 
 *                the table.
 **/
function updateTable(tableId) {
    var tableSrcFile = tableId+".json";
    console.log('PJA: updateTable()');
    
    $.getJSON(tableSrcFile, function(json) {
        intKeys = [];
        for (k in json) {
          if (json.hasOwnProperty(k)) {
            intKeys.push(k);
          }
        }
        intKeys.sort();
        tableRows='';
        
        tableHeaderId = tableId+'Header';
        //If a table header is defined
        if( json.hasOwnProperty('HEADER') ) {
            var tableHeader = document.getElementById(tableHeaderId);
            headerValueList = json['HEADER'];
            
            tableRows = tableRows + '<tr>';            
            for( colIndex in headerValueList ) {
                tableRows = tableRows + '<th>';
                tableRows = tableRows + headerValueList[colIndex];
                tableRows = tableRows + '</th>';
            }
            tableRows = tableRows + '</tr>';
        }
        
        var table = document.getElementById(tableId);
        for (var intKey in intKeys ) {
            colValueList = json[intKey];

            tableRows = tableRows + '<tr>';            
            for( colIndex in colValueList) {
                tableRows = tableRows + '<td>';
                tableRows = tableRows + colValueList[colIndex];
                tableRows = tableRows + '</td>';
            }
            tableRows = tableRows + '</tr>';
            
        }
        $('#' + tableId).html(tableRows);
    });
}

/**
 * @brief Update checkbox listener disables the update button if the auto update checkbox
 *        is checked.
 **/
function autoUpdateCBListener() {
    var cb1Checked = document.getElementById("autoUpdateCB1").checked;
    var cb2Checked = document.getElementById("autoUpdateCB2").checked;
    
    document.getElementById("updateButton1").disabled = cb1Checked;
    document.getElementById("updateButton2").disabled = cb1Checked;
}

/**
 * @brief Called at intervals to update the table if required.
 **/
setInterval(function() {
    var cbChecked1 = document.getElementById("autoUpdateCB1").checked;
    var cbChecked2 = document.getElementById("autoUpdateCB2").checked;
    
    if( cbChecked1 ) {
        updateTable('table1');
    }
    
    if( cbChecked2 ) {
        updateTable('table2');
    }

}, 2500);

//When the page first appears set the update
document.getElementById("autoUpdateCB1").checked = true;
document.getElementById("autoUpdateCB2").checked = true;
document.getElementById("updateButton1").disabled = true;
document.getElementById("updateButton2").disabled = true;

//When the page is loaded call the updateTable1() function.
document.getElementById("theBody").onload = function() {updateTable('table1')};
document.getElementById("theBody").onload = function() {updateTable('table2')};
//When the update button is selected update the table
document.getElementById("updateButton1").onclick = function() {updateTable('table1')};
document.getElementById("updateButton2").onclick = function() {updateTable('table2')};
//Add checkbox listener to auto update the checkbox.
document.getElementById("autoUpdateCB1").addEventListener("change", autoUpdateCBListener);
document.getElementById("autoUpdateCB2").addEventListener("change", autoUpdateCBListener);
