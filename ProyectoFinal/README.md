## Sistema de biblioteca

### Video de explicación
Se puede observar el video de explicación de funcionamiento del sistema, los protocolos empleados, el algorítmo empleado para
el manejo de réplicas y la tolerancia a fallas <a href='https://youtu.be/PxDwbMG6J9A'> acá </a>

### Distribución de procesos

#### Máquina 1 
  - Tendrá todos los procesos correspondientes a una sede.
  - Adicinionalmente contará con el proceso registrador y el coordinador cuyo propósito es coordinar el acceso a la base de datos.
#### Máquina 2
  - Tendrá todos los procesos correspondientes a otra sede.
#### Máquina 3 
  - Tendrá todos los procesos correspondientes a los clientes de la biblioteca.

## Ejecución de los proceos
  Nota : se debe remplazar "\<sede\>" con la dirección IPv4 de la máquina en donde se está corriendo el proceso
#### Gestor de carga (Principal)
  - <code> python3 GestorDeCarga.py \<sede\>:3000 \<sede\>:5551 \<sede\> </code> 
#### Gestor de carga (Respaldo en caso que el principal falle)
  - <code> python3 GestorDeCarga.py \<sede\>:2999 \<sede\>:5550 \<sede\> </code> 
#### Coordinador
  - <code> python3 Coordinador.py </code> 
#### Registrador
  - <code> python3 Registrador.py </code> 
#### Proceso de devolución 
  - <code> python3 Proceso_Devolucion \<sede\>:1001 \<sede\>:3001 \<número_sede\> </code> 
#### Proceso de renovación 
  - <code> python3 Proceso_RenovacionPrestamo \<sede\>:1002 \<sede\>:3002 \<número_sede\> </code> 
#### Proceso de solicitud 
  - <code> python3 Proceso_SolicitudPrestamo \<sede\>:1003 \<sede\>:3003 \<número_sede\> </code> 
