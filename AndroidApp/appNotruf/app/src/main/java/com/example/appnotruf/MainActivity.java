package com.example.appnotruf;

import android.content.pm.PackageManager;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.telephony.SubscriptionManager;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Enumeration;

public class MainActivity extends AppCompatActivity {

    private final static String TAG = MainActivity.class.getSimpleName();

    TextView infoIp, infoPort, textViewState, textViewPrompt;
    Button button_phonenumber, button_close;

    static final int serverPORT = 4445;

    //UdpServerThread udpServerThread;
    TcpServerThread tcpServerThread;
    String phonenumber = null;

    //<----------------- APP STATES ----------------->

    /*////////////////////////////////////
    /App initialisierung
    /*/////////////////////////////////////
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        infoIp = (TextView) findViewById(R.id.infoip);
        infoPort = (TextView) findViewById(R.id.infoport);
        textViewState = (TextView)findViewById(R.id.state);
        textViewPrompt = (TextView)findViewById(R.id.prompt);
        button_phonenumber = (Button)findViewById(R.id.buttonPhonenumber);
        button_close = (Button)findViewById(R.id.button_exit);
        infoIp.setText(getIpAddress());
        infoPort.setText(String.valueOf(serverPORT));

        // Andorid Permissons abfragen
        String[] permissions = new String[]{
                android.Manifest.permission.SEND_SMS,
                android.Manifest.permission.RECEIVE_SMS,
                android.Manifest.permission.WAKE_LOCK,
                android.Manifest.permission.INTERNET,
                android.Manifest.permission.ACCESS_NETWORK_STATE,
                android.Manifest.permission.READ_PHONE_STATE,
                android.Manifest.permission.FOREGROUND_SERVICE
        };
        int permissonfailed = 0;
        for(String p:permissions){
            if(this.checkCallingOrSelfPermission(p) == PackageManager.PERMISSION_DENIED){
                permissonfailed++;
            }
        }
        if(permissonfailed > 0){
            updatePrompt("ACHTUNG: Berechtigungen nicht gesetzt!\n");
        }
    }

    /*////////////////////////////////////
    /Was Passiert, nachdem die App initialisiert wurde
    /*/////////////////////////////////////
    @Override
    protected void onStart() {
        //udpServerThread = new UdpServerThread(UdpServerPORT);
        tcpServerThread = new TcpServerThread(serverPORT);

        // Telefonnummer einlesen, wenn Button geklickt wird
        button_phonenumber.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                EditText mEdit = (EditText)findViewById(R.id.editTextPhone);
                phonenumber =  mEdit.getText().toString();
                //udpServerThread.start();
                tcpServerThread.start();
            }
        });

        // Server Stoppen und App schließen
        button_close.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

        super.onStart();
    }

    /*////////////////////////////////////
    /Was Passiert, wenn die App minimiert wird
    /*/////////////////////////////////////
    @Override
    protected void onStop() {
        updatePrompt("Onstop called" + "\n");
        super.onStop();
    }

    /*////////////////////////////////////
    /Was Passiert, wenn die App geschlossen wird
    /*/////////////////////////////////////
    @Override
    protected void onDestroy(){
        //if(udpServerThread != null){
        //    udpServerThread.setRunning(false);
        //    udpServerThread = null;
        //}
        if(tcpServerThread != null) {
            tcpServerThread.setRunning(false);
            tcpServerThread = null;
        }
        super.onDestroy();
    }

    //<--^^^^^^^^^^^^^^^ APP STATES ^^^^^^^^^^^^^^^-->

    // <----------------- MAIN Activity ----------------->

    /*////////////////////////////////////
    /GUI Textview Updates
    /*/////////////////////////////////////
    private void updateState(final String state){
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                textViewState.setText(state);
            }
        });
    }
    private void updatePrompt(final String prompt){
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                textViewPrompt.append(prompt);
            }
        });
    }
    private void clearPrompt(){
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                textViewPrompt.setText("");
            }
        });
    }

    /*////////////////////////////////////
    /TCP Server Thread Class
    /*/////////////////////////////////////
    private class TcpServerThread extends Thread{
        public InetAddress clientAddress;
        public int clientPort;
        int serverPort;
        boolean running;
        ServerSocket serverSocket;

        public TcpServerThread(int serverport){
            super();
            this.serverPort = serverport;
        }
        public void setRunning(boolean running){
            this.running = running;
        }

        @Override
        public void run(){

            running = true;
            byte[] readBuf = new byte[200];
            String nachricht = "";
            try {
                updateState("Starting TCP Server");
                serverSocket = new ServerSocket(serverPORT);
                updateState("Warte auf TCP Connection...");
                while (running) {
                    Socket clientSocket = serverSocket.accept();

                    updateState("TCP Server gestartet.");
                    clearPrompt();

                    clientAddress = clientSocket.getInetAddress();
                    clientPort = clientSocket.getPort();
                    updatePrompt("Client connected: " + clientAddress + ":" + clientPort + "\n");


                    InputStream input = clientSocket.getInputStream();
                    int r = 0;

                    do {
                        r = input.read(readBuf);
                        //String nachricht = reader.readLine();    // reads a line of text
                        updatePrompt("Request from: " + clientAddress + ":" + clientPort + "\n");
                        //updatePrompt(nachricht + "\n");
                        nachricht += new String(readBuf, StandardCharsets.UTF_8);

//                        if(clientSocket.isClosed()){
//                            updateState("Warte auf TCP Connection...");
//                            clientSocket = serverSocket.accept();
//                            updateState("TCP Server gestartet.");
//                        }
                    } while (readBuf[r - 1] != 0x05);

                    updatePrompt(nachricht + "\n");
                    sendSMS(phonenumber, nachricht);
                    OutputStream output = clientSocket.getOutputStream();
                    PrintWriter writer = new PrintWriter(output, true);
                    writer.print("sms gesendet" + 0x05);
                    writer.flush();
                    nachricht = "";
                    clientSocket.close();
                }
            }catch (Exception ex){
                updatePrompt(String.valueOf(ex.getStackTrace()));
            }
        }

    }


    /*////////////////////////////////////
    /IP Adresse Abfragen
    /*/////////////////////////////////////
    private String getIpAddress() {
        String ip = "";
        try {
            Enumeration<NetworkInterface> enumNetworkInterfaces = NetworkInterface
                    .getNetworkInterfaces();
            while (enumNetworkInterfaces.hasMoreElements()) {
                NetworkInterface networkInterface = enumNetworkInterfaces
                        .nextElement();
                Enumeration<InetAddress> enumInetAddress = networkInterface
                        .getInetAddresses();
                while (enumInetAddress.hasMoreElements()) {
                    InetAddress inetAddress = enumInetAddress.nextElement();

                    if (inetAddress.isSiteLocalAddress()) {
                        ip += "SiteLocalAddress: "
                                + inetAddress.getHostAddress() + "\n";
                    }
                }
            }
        } catch (SocketException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
            ip += "Something Wrong! " + e.toString() + "\n";
        }
        return ip;
    }

    /*////////////////////////////////////
    /send SMS to phonenumber
    /*/////////////////////////////////////
    private void sendSMS(String phoneNumber, String message){
        //SmsManager sms = SmsManager.getDefault();
        // Dies bei Multi-SIM Handys
        SmsManager sms = SmsManager.getSmsManagerForSubscriptionId(SubscriptionManager.getDefaultSubscriptionId());
        // Nachricht teilen in SMS größe
        ArrayList<String> messages = sms.divideMessage(message);

        // Jetzt SMS senden
        sms.sendMultipartTextMessage(phoneNumber, null, messages, null, null);
        updatePrompt("SMS gesendet." + "\n");
    }

    // <--^^^^^^^^^^^^^^^ MAIN Activity ^^^^^^^^^^^^^^^-->



    // <----------------- NO LONGER IN USE ----------------->
    static final int UdpClientRequestPORT = 4446; // no longer in use
    /*////////////////////////////////////
    /UDP Server Thread Class
    /---> no longer in use <---
    /*/////////////////////////////////////
    private class UdpServerThread extends Thread{
        public InetAddress clientAddress;
        public int clientPort;
        int serverPort;
        public DatagramSocket socket;
        boolean running;

        public UdpServerThread(int serverPort) {
            super();
            this.serverPort = serverPort;
        }

        public void setRunning(boolean running){
            this.running = running;
        }

        @Override
        public void run() {
            running = true;
            try {
                updateState("Starting UDP Server");
                socket = new DatagramSocket(serverPort);

                updateState("UDP Server is running");
                Log.e(TAG, "UDP Server is running");

                while(running){
                    byte[] buf = new byte[256];

                    // receive request
                    DatagramPacket packet = new DatagramPacket(buf, buf.length);
                    socket.receive(packet);     //this code block the program flow

                    // send the response to the client at "address" and "port"
                    clientAddress = packet.getAddress();
                    clientPort = packet.getPort();

                    updatePrompt("Request from: " + clientAddress + ":" + clientPort + "\n");
                    String nachricht = new String(packet.getData(), StandardCharsets.UTF_8 );
                    updatePrompt(nachricht + "\n");
                    // Antwort an Server, dass Datagram gesendet
                    sendUDPDatagram("datagram ok", socket, clientAddress,UdpClientRequestPORT);

                    // SMS mit nachricht Senden
                    // Beispiel 4915xxxxxxxx5

                    sendSMS(phonenumber, nachricht);
                    sendUDPDatagram("sms ok", socket, clientAddress,UdpClientRequestPORT);
                }
                Log.e(TAG, "UDP Server ended");
            } catch (SocketException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            } finally {
                if(socket != null){
                    socket.close();
                    Log.e(TAG, "socket.close()");
                }
            }
        }
    }

    /*////////////////////////////////////
    /UDP Datagram senden
    /---> no longer in use <---
    /*/////////////////////////////////////
    private void sendUDPDatagram (String nachricht, DatagramSocket socket, InetAddress clientAddress, int clientPort) {
        byte[] buf = new byte[256];
        buf = nachricht.getBytes();
        DatagramPacket packet = new DatagramPacket(buf, buf.length, clientAddress, clientPort);
        try {
            socket.send(packet);
        } catch (IOException e) {
            updatePrompt("Failed to send UDP Datagram\n");
        }
    }

}