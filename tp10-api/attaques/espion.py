"""Relais place entre le client et le serveur : affiche ce qui passe sur le reseau.
Usage : python attaques/espion.py PORT_ECOUTE PORT_SERVEUR"""
import socket, sys, threading

ECOUTE, CIBLE = int(sys.argv[1]), int(sys.argv[2])


def lisible(data):                                    # du texte, ou des octets illisibles ?
    return all(32 <= b < 127 or b in (9, 10, 13) for b in data[:200])


def relayer(src, dst, espionner):
    try:
        while data := src.recv(65536):
            if espionner:
                print(f"--- client -> serveur : {len(data)} octets ---")
                if lisible(data):
                    print(data[:400].decode().replace("\r", ""), flush=True)
                else:
                    print(data[:24].hex(" "), "...", flush=True)
            dst.sendall(data)
    except OSError:
        pass
    finally:
        dst.close()


serveur = socket.socket()
serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serveur.bind(("127.0.0.1", ECOUTE))
serveur.listen()
serveur.settimeout(1)                                 # Ctrl+C fonctionne aussi sous Windows
print(f"espion en ecoute sur {ECOUTE}, relaie vers {CIBLE}", flush=True)
while True:
    try:
        client, _ = serveur.accept()
    except TimeoutError:
        continue
    client.settimeout(None)
    cible = socket.create_connection(("127.0.0.1", CIBLE))
    threading.Thread(target=relayer, args=(client, cible, True), daemon=True).start()
    threading.Thread(target=relayer, args=(cible, client, False), daemon=True).start()
