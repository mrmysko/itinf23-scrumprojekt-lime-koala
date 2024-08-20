### Vision:
Tillhandahålla ett webbaserat övervakningsverktyg för prestandaövervakning
och administrering utav Docker-Container på flertal servrar
med ett responsivt gränssnitt som visualiserar viktiga mätvärden i realtid,
vilket gör det tillgängligt för Webadmins.

### Viktigast att färdigställa först:
Bygg en python-baserad agent som övervakar Docker-Container och kan ge distant administrering.
Dessa agenter skall även föra vidare information till databas/eller webbsida, (CPU, minne, Diskutrymme och nätverksanvändning).
Inkludera förmåga att läsa av information, samt administrera containrar.
Prioritera enkel driftsättning av containrar.

- Sätta Upp Docker-Servrar
- Sätta upp en WebSida För  agenter att svara till
- Skapa ett program för att interragera med Docker
- Skapa ett program som interagerar med agent.
- Få Interagerande agent att kunna läsa och administrerar Docker från Remote Resurs
- Få Web agent att interagera med WerbServer eller Databas
- Framtida Funktion: Historia Övervakning för Base-Lines
