const btn = document.querySelector ('#pedido');
function creapedido()
	{	
		var table = document.getElementById("myTable");
		var cadena = "";
		for (var i = 1, row; row = table.rows[i]; i++) {

	   		var check = document.getElementById("np"+row.id);
	//se guarda el valor del id de paquete y si el checkbox correspondiente está 
	//seleccionado: "true" o no: "false"
	   		cadena += ' ' + row.id + '-' + check.checked;
		}
		alert(cadena);
	}        
btn.addEventListener('click', creapedido);

