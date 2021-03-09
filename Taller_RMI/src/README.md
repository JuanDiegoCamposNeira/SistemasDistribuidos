1) Se inicia hamachi para poder tener la conexion entre los pc, la conexion usada se llama IntroDistribuidosPUJ

2) En ambos pc se compilan los archivos de la carpeta src por consola con el comando <javac *.java> 

3) En el primer pc, se ejecuta por consola el comando <rmiregistry> dentro de la carpeta src

4) En el primer pc, dentro de la carpeta src se ejecuta el archivo main de la clase Servidor con el comando <java Servidor>

5) En el segundo, dentro de la carpeta src se ejecuta el archivo main de la clase Cliente con el comando <java Cliente 25.33.101.216>
