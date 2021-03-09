/*
Autores : 
- Simón Dávila Saravia
- Jose Mario Arias Acevedo
- Juan Diego Campos Neira
*/
import java.rmi.*;
import java.rmi.server.UnicastRemoteObject;

public class ObjetoRemoto extends UnicastRemoteObject implements Interfaz{
	
	public ObjetoRemoto(String name) throws RemoteException {
		super();
		try {
			System.out.println("Rebind Object " + name);
			Naming.rebind(name, this);
		} catch (Exception e) {
			System.out.println("Exception: " + e.getMessage());
			e.printStackTrace();
		}
	}

	@Override
	public boolean comparaCadenas(String a, String b) throws RemoteException {
		// Comparar las cadenas y retorna true si son iguales, si son diferentes retorna falso
		return a.equals(b);
	}

	@Override
	public String concatenCadenas(String a, String b, String buffer) throws RemoteException {
		// Concatena dos candenas las cuales son a y b, retorna buffer que es la cadena concatenada
		
		buffer= a+b;
		
		
		return buffer;
	}
	@Override
	public String copiaCadena(String a, String buffer) throws RemoteException {
		// Toma la cadena a y la copia en el buffer
		buffer=a;
		return buffer;
	}
	@Override
	public int cuentaCaracteresCadena(String a) throws RemoteException {
		// Cuenta el total de caracteres de a
	
		return a.length();
	}
}
