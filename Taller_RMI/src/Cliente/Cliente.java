package Cliente;

import java.rmi.registry.*;
import java.rmi.server.*;
import java.rmi.*;

public class Cliente {
	public static void main(String args[]) {
		//Las palabras asignadas son hola y mundo
		String a = "hola";
		String b = "mundo";
		String buffer = null;
		try {
			System.out.println("Buscando Objeto ");
			
			Interfaz micomparador = (Interfaz) Naming.lookup("rmi://"+ args[0]+"/" + "MiComparador");
			//Imprime los resultados de cada metodo, se les llama y le pasamos como parametros las palabras anteriormente asignadas
			System.out.println(micomparador.comparaCadenas(a, b));
			System.out.println(micomparador.concatenCadenas(a, b, buffer));
			System.out.println(micomparador.copiaCadena(a, buffer));
			System.out.println(micomparador.cuentaCaracteresCadena(a));
			
		} catch (Exception e) {
			e.printStackTrace();
		}
		System.exit(0);
	}
}
