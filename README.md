##mySerial

![captura.png](https://raw.githubusercontent.com/jorgegarciadev/mySerial/master/captura.png)

####English

mySerial is an Urwid based serial monitor tool similar to the included on Arduino IDE and Stino. It's has been thought to be used via *Secure Shell*. Supports local and remote ports using ```serial.serial_for_url```, also WebSockets.

Requires **Urwid**, **websecket-client** and **pySerial** to work.

Installing:

```pip install git+https://github.com/jorgegarciadev/mySerial.git```



If you have any problem receiving data from a socket update pySerial to the latest version.

Press ESC to exit.

#####Usage

```myserial.py [-h] port [-b baudrate] [-cr] [-lf]```

#####Example

```myserial.py /dev/ttyUSB0 -b 14400 -lf```


####Español

mySerial es un monitor de puerto serie basado en **Urwid** muy parecido al incluido en Arduino IDE and Stino. Ha sido pensado para ser usado a través de *Secure Shell*. Soporta conexiones locales y remotas, también soporta WebSockets.

Necesita **Urwid**, **websecket-client** y **pySerial** para funcionar.

Para instalarlo:

```pip install git+https://github.com/jorgegarciadev/mySerial.git```


Si tienes problemas al recibir datos desde un socket instala la versión más reciente de pySerial.

Tecla ESC para salir.

#####Modo de uso

```mySerial.py [-h] port [-b baudrate] [-cr] [-lf]```

#####Ejemplo

```~$ myserial.py /dev/ttyUSB0 -b 14400 -lf```