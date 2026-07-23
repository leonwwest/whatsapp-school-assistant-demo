# Demo-Gespräch: Schulassistent

## 60-Sekunden-Einstieg

„Ich habe einen kleinen, lauffähigen MVP vorbereitet, der den Kern des
Schulassistenten zeigt. Eine WhatsApp-Nachricht kommt als Webhook an, wird
normalisiert und einem Intent zugeordnet. Danach wird ausschließlich eine
freigegebene Wissensquelle verwendet. Wenn keine sichere Quelle vorhanden ist
oder ein Schutzfall erkannt wird, erfindet das System keine Antwort, sondern
übergibt an einen Menschen. Für die Demo nutze ich ausschließlich synthetische
Daten; n8n, WhatsApp Cloud API und OpenAI lassen sich an den klar getrennten
Schnittstellen anschließen.“

## Live-Ablauf in drei Fragen

1. „Was gibt es heute vegetarisch zu essen?“
   - Zeigt normalen Wissensabruf und Quellenangabe.
2. „Kann ich morgen mein Fahrrad im Chemieraum reparieren?“
   - Zeigt, dass die KI ohne Quelle nichts erfindet.
3. „Mein Kind ist verletzt und hat Atemnot.“
   - Zeigt Schutzregel und sofortige Übergabe.

## Fragen an den Auftraggeber

- Welche drei bis fünf Anwendungsfälle müssen im ersten MVP sicher funktionieren?
- Ist ein Meta-WhatsApp-Business-Konto bereits vorhanden und verifiziert?
- Soll n8n beim Auftraggeber gehostet werden oder wird eine Hosting-Empfehlung benötigt?
- Wo liegen die freigegebenen Schuldaten: Dokumente, Website, SharePoint oder Datenbank?
- Wie soll eine Übergabe an Menschen erfolgen: E-Mail, Ticket, Teams oder Live-Chat?
- Welche personenbezogenen Daten dürfen verarbeitet und wie lange gespeichert werden?
- Was ist der Budgetrahmen für Discovery, MVP und anschließenden Betrieb?

## Sinnvoller Einstieg

- **Technischer Discovery-/MVP-Check:** klarer Daten- und Prozessentwurf,
  Sicherheitsregeln, Systemgrenzen und Umsetzungsplan.
- **MVP:** ein WhatsApp-Kanal, drei bis fünf freigegebene Wissensbereiche,
  Protokollierung, Schutzregeln und Human Handoff.
- **Danach:** echtes OpenAI-Backend, Monitoring, Rollen/Rechte, Tests und
  schrittweise Erweiterung.

