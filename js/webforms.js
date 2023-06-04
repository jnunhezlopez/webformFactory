function cargapaquetes()
{
    console.log("Dentro de consultapaquetes.")
    if (!$('#estado').val()){
        alert("Debe seleccionarse un estado del paquete (1:en stock, 2: en producción).");
        return false;
    }
    //if (!$('#texto').val()){
    //    alert("Debe limitarse la búsqueda de paquete indicando un texto en la descripción.");
    //    return false;
    //}
    var url = '/cargapaquetes?estado=' + $('#estado').val() + '&texto=' +$('#texto').val();
    // var selectControl = document.getElementById('optionList');
    var x = document.getElementById("myTable");
    //truco para borrar la tabla por si se pulsa el botón varias veces
    x.innerHTML = "";
    var y = document.createElement("TR");
    y.setAttribute("id", "myTr");
    document.getElementById("myTable").appendChild(y);
    var x = document.createElement("TH");
    var t = document.createTextNode("Id");
    x.appendChild(t);
    var x = document.createElement("TH");
    var t = document.createTextNode("codigo");
    x.appendChild(t);
    var campos = ['Artículo', 'Largo','Ancho','Grueso','Cálculo','UN',''];
    for (const campo of campos){
	    document.getElementById("myTr").appendChild(x);
	    var x = document.createElement("TH");
	    var t = document.createTextNode(campo);
    	x.appendChild(t);
    }
         
    // x.deleteRow(0);
    $.get(url, function(data) {
        for (var key in data){
            // selectControl.options[key] = new Option(data[key].nombre);
            //se crea la fila de la tabla
            document.getElementById("myTr").appendChild(x);
            var y = document.createElement("TR");
            var cadena1 = "id";
            //cadena1.concat(String(key));
            //var cadena2 = "myTr" + String(key);
            var cadena2 = String(data[key].id);
            // ********IMPORTANTE******* se guarda el id de paquete como el id de TR
            // de ese modo se puede obtener el id para crear un pedido a partir de los
            // paquetes seleccionados
            y.setAttribute(cadena1, cadena2);
            document.getElementById("myTable").appendChild(y);
            //se inserta la columna codigo
            var campos = ['codigo','descripcion','largo','ancho','grueso','calculo','UN'];
            for (const campo of campos){
            	var z = document.createElement("TD");
	            var t = document.createTextNode(data[key][campo]);
    	        z.appendChild(t);
    	        document.getElementById(cadena2).appendChild(z);            
            }
            //se inserta un checkbox
            var z = document.createElement("TD");
            var t = document.createElement("INPUT");
            t.name="np"+String(data[key].id);
            t.id="np"+String(data[key].id);                        
            t.setAttribute("type", "checkbox");
            z.appendChild(t);
            // alert(t.name);
            document.getElementById(cadena2).appendChild(z);
        }
        // $('#quote').html(cadena);
        // $('#symbol').val('');
    });
}
/*
function creapedido()
{
    //alert("Pendiente de programar");
	var table = document.getElementById("myTable");
	var cadena = "";
	//var check = document.getElementById("np1");
	//alert(check.checked);
	for (var i = 1, row; row = table.rows[i]; i++) {
   //iterate through rows
   		var check = document.getElementById("np"+row.id);
   		//se guarda el valor del id de paquete y si el checkbox correspondiente está 
   		//seleccionado: "true" o no: "false"
   		cadena += ' ' + row.id + '-' + check.checked;
   //rows would be accessed using the "row" variable assigned in the for loop
//	   for (var j = 0, col; col = row.cells[j]; j++) {
 //iterate through columns
 //columns would be accessed using the "col" variable assigned in the for loop
//	   }  
	}
	alert(cadena);
}
*/
