/*
Autores : 
- Simón Dávila Saravia
- Jose Mario Arias Acevedo
- Juan Diego Campos Neira
*/
import java.rmi.*;
import java.rmi.server.*;

public class Servidor {
	public static void main(String args[]) {

		try {
			System.setProperty("java.rmi.server.hostname","25.33.101.216");
			ObjetoRemoto micomparador = new ObjetoRemoto("rmi://25.33.101.216:1099" + "/MiComparador");
		} catch (Exception e) {
			System.err.println("System exception" + e);
		}
	}
}
