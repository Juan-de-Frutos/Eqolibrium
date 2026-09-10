document.getElementById("BotonAlimentacion").onclick = alimentacion;
document.getElementById("BotonTransporte").onclick = transporte;
document.getElementById("BotonEnergia").onclick = energia;
document.getElementById("BotonAgua").onclick = agua;
document.getElementById("BotonResiduos").onclick = residuos;
var huella = 0.00;
var huellaAlimentacion =0;
var huellaTransporte =0;
var huellaEnergia =0;
var huellaAgua=0;
var huellaResiduos=0;
function alimentacion(){
	//alert(`Pelotudo`);
	let listabotones=['Fruta','Verdura', 'Pan', 'CarneVacuno', 'CarnePollo','CarneCerdo', 'Pescado', 'Leche', 'Refresco', 'Cigarros', 'Alcohol' ];
	for (let step = 0; step < listabotones.length; step++) {
		const indice = document.getElementById(listabotones[parseInt(step, 10)]).selectedIndex;
		const opcionSeleccionada = document.getElementById(listabotones[parseInt(step, 10)]).options[indice];
		huella+= parseFloat(opcionSeleccionada.value, 10);
		huellaAlimentacion+=parseFloat(opcionSeleccionada.value, 10);
	}
	//alert(`Huella ecológica total: ${huella} \nHuella ecológica de este apartado: ${huellaAlimentacion}.`);
	};
function transporte(){
	//alert(`Pelotudo`);
	let listabotones=['t1','t2','t3'];
	for (let step = 0; step < listabotones.length; step++) {
		const indice = document.getElementById(listabotones[parseInt(step, 10)]).selectedIndex;
		const opcionSeleccionada = document.getElementById(listabotones[parseInt(step, 10)]).options[indice];
		huella+= parseFloat(opcionSeleccionada.value, 10);
		huellaTransporte+=parseFloat(opcionSeleccionada.value, 10);
	}
	//alert(`Huella ecológica total: ${huella} \nHuella ecológica de este apartado: ${huellaTransporte}.`);
	};
function energia(){
	//alert(`Pelotudo`);
	let listabotones=['e1','e2','e3','e4','e5', 'e6'];
	for (let step = 0; step < listabotones.length; step++) {
		const indice = document.getElementById(listabotones[parseInt(step, 10)]).selectedIndex;
		const opcionSeleccionada = document.getElementById(listabotones[parseInt(step, 10)]).options[indice];
		huella+= parseFloat(opcionSeleccionada.value, 10);
		huellaEnergia+= parseFloat(opcionSeleccionada.value, 10);
	}
	//alert(`Huella ecológica total: ${huella} \nHuella ecológica de este apartado: ${huellaEnergia}.`);
	};
function agua(){
	//alert(`Pelotudo`);
	let listabotones=['a1','a2','a3'];
	for (let step = 0; step < listabotones.length; step++) {
		const indice = document.getElementById(listabotones[parseInt(step, 10)]).selectedIndex;
		const opcionSeleccionada = document.getElementById(listabotones[parseInt(step, 10)]).options[indice];
		huella+= parseFloat(opcionSeleccionada.value, 10);
		huellaAgua+= parseFloat(opcionSeleccionada.value, 10);
	}
	//alert(`Huella ecológica total: ${huella} \nHuella ecológica de este apartado: ${huellaAgua}.`);
	};
function residuos(){
	//alert(`Pelotudo`);
	let listabotones=['r1','r2','r3','r4'];
	for (let step = 0; step < listabotones.length; step++) {
		const indice = document.getElementById(listabotones[parseInt(step, 10)]).selectedIndex;
		const opcionSeleccionada = document.getElementById(listabotones[parseInt(step, 10)]).options[indice];
		huella+= parseFloat(opcionSeleccionada.value, 10);
		huellaResiduos+= parseFloat(opcionSeleccionada.value, 10);
	}
	//alert(`Huella ecológica total: ${huella} \nHuella ecológica de este apartado: ${huellaResiduos}.`);
	};

function mostrarresultados(){
	huella=huella.toFixed(5);
	huellaResiduos=huellaResiduos.toFixed(5);
	huellaAlimentacion=huellaAlimentacion.toFixed(5);
	huellaAgua=huellaAgua.toFixed(5);
	huellaEnergia=huellaEnergia.toFixed(5);
	huellaTransporte=huellaTransporte.toFixed(5);
	var xValues = ["Alimentación", "Transporte", "Energía", "Agua", "Residuos"];
	var yValues = [huellaAlimentacion, huellaTransporte, huellaEnergia, huellaAgua, huellaResiduos];
	//var yValues = [1,2,3,4,5];
	var barColors = [
	  "#b91d47",
	  "#2E7D3D",
	  "#FFC300 ",
	  "#0604FB",
	  "#625C7C"
	];

	new Chart("myChart", {
	  type: "pie",
	  data: {
	    labels: xValues,
	    datasets: [{
	      backgroundColor: barColors,
	      data: yValues
	    }]
	  },
	  options: {
	    title: {
	      display: true,
	      text: "Tu huella ecológica"
	    }
	  }
	});
	document.getElementById('Resultados').innerHTML=`<br><h4> Huella Ecológica sostenible: 0.513 ha/persona. <br> Huella Ecológica Media: 2.9 ha/persona. 
	</h4><br><h3> Tu Huella ecológica total: <br> <font color=oleole>${huella} hectáreas de bosque.</font></h3> <br> 
	<ol> 
	<li> <h4> Huella Alimentación:  ${huellaAlimentacion}. </h4></li> 
	<li> <h4> Huella Transporte:  ${huellaTransporte}. </h4></li> 
	<li> <h4> Huella Energía:  ${huellaEnergia}. </h4></li> 
	<li> <h4> Huella Agua:  ${huellaAgua}. </h4></li> 
	<li> <h4> Huella Residuos:  ${huellaResiduos}. </h4></li> </ol><br><h2>HUELLA POR APARTADOS:</h2>`;
}
