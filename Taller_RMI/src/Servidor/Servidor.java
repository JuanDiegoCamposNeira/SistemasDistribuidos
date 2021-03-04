package Servidor;

import java.rmi.*;
import java.rmi.server.*;


public class Servidor {
	public static void main(String args[]) {
		try {
			ObjetoRemoto micomparador = new ObjetoRemoto("rmi://localhost:1099" + "/MiComparador");
		} catch (Exception e) {
			System.err.println("System exception" + e);
		}
	}
}
