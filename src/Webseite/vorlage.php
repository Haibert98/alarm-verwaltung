<?php
  if(!file_exists('/tmp/counter{{ token }}.txt')){
    file_put_contents('/tmp/counter{{ token }}.txt', '0');
  }
  else{
    if(((int) file_get_contents('/tmp/counter{{ token }}.txt')) < 4){
      file_put_contents('/tmp/counter{{ token }}.txt', ((int) file_get_contents('/tmp/counter{{ token }}.txt')) + 1);
    }
    else{
      echo "Ungültiger Link!";
      return;
    }
  }
  if(checkPermission()){
    echoContent();
  }
  else{
    echo "Ungültiger Link!";
    return;
  }

function checkPermission()
{
  if($_GET["token"] == "{{ token }}"){
    return true;
  }
}

function echoContent()
{
  echo "<h2 style=\"color: red;\">Hinweise zum Zutritt zur Wohnung</h2>
        <strong><p> Der Wohnungszutritt ist gewährleistet über die Eingabe eines Morsecodes an der Wohnungstür. <br>
        Dieser wird an einer Klingel rechts neben der Tür neben(?) dem Tablet eingegeben.<br>
        Es sind zwei Codes bereitgestellt:<br>
        Der erste lautet: \"{{tuerCode1}}\" und ist für die schnelle Eingabe geeignet, wird aber nach mehrmaliger Falscheingabe gesperrt.<br>
        Der zweite lautet: \"{{tuerCode2}}\" und kann beliebig oft falsch eingegeben werden. Beide Codes werden nach 30 Minuten automatisch gesperrt.<br>
        Punkt bedeutet hierbei die Klingel soll kurz gedrückt werden (maximal 0,5 Sekunden).<br>
        Strich bedeutet die Klingel lang drücken (0,5 bis maximal 3 Sekunden).<br>
        Nach Eingabe des Codes sollte die Leuchte grün leuchten und die Tür ist damit entriegelt. Ist dies nicht der Fall, wurde der Code falsch eingegeben. Nun muss die Klingeltaste mindestens 3 Sekunden lang gedrückt werden, um den Eingabevorgang neu zu starten. War der Resett erfolgreich leuchtet die Klingel rot und der code kann erneut eingegeben werden </strong><br>
        </p>
        <h2>Personen Daten</h2>
        {{vorname}} {{nachname}}, {{geburtsdatum}}, {{krankenkasse}} Vers.Nr. {{verischertennummer}}<br>
        {{strasse}} {{hausnummer}}, {{plz}} {{ortsteil}} {{ort}} <br>
        Stockwerk: {{stockwerk}} <br>
        Fahrstuhl vorhanden: {{fahrstuhl}}
        <h2>Weitere Daten:</h2>
        Gewicht: {{gewicht}}
        Größe: {{groesse}}
        <h2>Vorerkrankungen</h2>
        {% for krankheit in vorerkrankungen -%}
            {{ krankheit }}<br>
        {%- endfor %}
        <h2>Allergien</h2>
        {% for allergie in allergien -%}
            {{ allergie }}<br>
        {%- endfor %}
        <h2>Medikationsplan</h2>
        {% for medikament in medikation -%}
            {{ medikament }}<br>
        {%- endfor %}
        <h2>Bild des Unfalls</h2>
        {% for b in bilder -%}
            <img src={{b}} alt= \"b\"width=\"600\" height=\"400\"><br>
        {%- endfor %}

        <h2>Lageplan - Position der Person</h2>
        {% for p in positionbilder -%}
            <img src={{p}} alt= \"Positions Bild\" width=\"600\" height=\"400\"><br>
        {%- endfor %}

        <h2>Anleitung zur Benutzung des Türcodes</h2>
        Zugangscode Tür: {{TUERCODE}}<br>
        
        <h2>Herzfrequenz</h2>
        <img src=/res/heartbeat.png alt=\"Herzfrequen Werte fehlen\"width=\"600\" height=\"400\"><br>";
}
?>
