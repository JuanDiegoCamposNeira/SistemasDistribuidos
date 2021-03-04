package Cliente;

public interface Interfaz extends java.rmi.Remote{
	public boolean comparaCadenas(String a, String b) throws java.rmi.RemoteException;
	public String concatenCadenas(String a, String b, String c) throws java.rmi.RemoteException;
	public String copiaCadena(String a, String b) throws java.rmi.RemoteException;
	public int cuentaCaracteresCadena(String a) throws java.rmi.RemoteException;
}
