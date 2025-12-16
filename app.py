import streamlit as st
import google.genai as genai
import json
import time

print("Démarrage de l'application Le Génie...")
# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Le Génie 🧞‍♂️", page_icon="🧞‍♂️", layout="centered")

# --- STYLE CSS (DESIGN) ---
st.markdown(
    """
<style>
    .user-msg {background-color: #e6f3ff; padding: 10px; border-radius: 10px; margin-bottom: 10px;}
    .genie-msg {background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #6a11cb;}
    .offer-card {border: 2px solid #28a745; background-color: #f9fff9; padding: 15px; border-radius: 10px; margin-top: 10px;}
    .stButton>button {width: 100%; border-radius: 20px;}
    .urgent {color: red; font-weight: bold;}
</style>
""",
    unsafe_allow_html=True,
)

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "offres_disponibles" not in st.session_state:
    st.session_state.offres_disponibles = []  # Liste des offres reçues par le client
if "demande_active" not in st.session_state:
    st.session_state.demande_active = None  # La demande en cours pour les pros

# --- BARRE LATÉRALE (RÉGLAGES) ---
with st.sidebar:
    st.title("⚙️ Réglages")
    api_key = st.text_input("Colle ta Clé Google API ici :", type="password")

    st.divider()
    st.subheader("🎭 Changer de Rôle")
    role = st.radio("Qui êtes-vous ?", ["Client (Utilisateur)", "Prestataire (Pro)"])

    st.divider()
    st.error("🚨 BOUTON SOS / SÉCURITÉ")
    if st.button("SIGNALER UN PROBLÈME"):
        st.toast("Signalement envoyé à l'administration !", icon="🛡️")


# --- FONCTION INTELLIGENTE (IA) ---
def analyser_demande(texte_utilisateur):
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"""
        Tu es un Génie assistant service au Maroc. Analyse cette demande : "{texte_utilisateur}".
        Si c'est une demande de service, réponds UNIQUEMENT avec ce format JSON :
        {{
            "type": "Mécano/Plombier/Coursier/Location",
            "urgence": "Haute/Moyenne/Basse",
            "resume": "Résumé court en français",
            "conseil": "Une phrase rassurante courte"
        }}
        Si ce n'est pas clair, renvoie juste null.
        """
        response = model.generate_content(prompt)
        # Nettoyage basique pour extraire le JSON
        clean_text = response.text.replace("```json", "").replace("```", "")
        return json.loads(clean_text)
    except:
        return None


# ==========================================
# VUE 1 : INTERFACE CLIENT (UTILISATEUR)
# ==========================================
if role == "Client (Utilisateur)":
    st.title("🧞‍♂️ Le Génie")
    st.caption("Parlez en Darija, Arabe ou Français.")

    # Afficher l'historique
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='user-msg'>👤 <b>Moi:</b> {msg['content']}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='genie-msg'>🧞‍♂️ <b>Génie:</b> {msg['content']}</div>",
                unsafe_allow_html=True,
            )

    # Zone de saisie
    user_input = st.chat_input("Ex: Khoya tomobil sketat lia f Agdal...")

    if user_input:
        # 1. Afficher le message utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(
            f"<div class='user-msg'>👤 <b>Moi:</b> {user_input}</div>",
            unsafe_allow_html=True,
        )

        # 2. L'IA Analyse
        if not api_key:
            st.warning("⚠️ Mets ta clé API à gauche d'abord !")
        else:
            with st.spinner("Le Génie réfléchit..."):
                analyse = analyser_demande(user_input)

            if analyse:
                reponse_genie = f"{analyse['conseil']} J'ai envoyé ta demande aux pros : **{analyse['type']}**."
                st.session_state.messages.append(
                    {"role": "assistant", "content": reponse_genie}
                )
                st.markdown(
                    f"<div class='genie-msg'>🧞‍♂️ <b>Génie:</b> {reponse_genie}</div>",
                    unsafe_allow_html=True,
                )

                # ENVOYER LA DEMANDE CÔTÉ PRO
                st.session_state.demande_active = {
                    "type": analyse["type"],
                    "desc": analyse["resume"],
                    "urgence": analyse["urgence"],
                    "date": time.strftime("%H:%M"),
                }
            else:
                st.error("Désolé, je n'ai pas compris. Essaie de préciser.")

    # 3. Afficher les offres reçues des Pros
    if st.session_state.offres_disponibles:
        st.divider()
        st.subheader("✅ Offres reçues")
        for offre in st.session_state.offres_disponibles:
            cols = st.columns([3, 1])
            with cols[0]:
                st.success(
                    f"**{offre['pro']}** propose : **{offre['prix']} DH** (Arrive en {offre['temps']} min)"
                )
            with cols[1]:
                if st.button("ACCEPTER", key=f"btn_{offre['prix']}"):
                    st.balloons()
                    st.success("🎉 Offre validée ! Le pro arrive.")
                    st.info(f"📞 Contact : {offre['tel']}")

# ==========================================
# VUE 2 : INTERFACE PRESTATAIRE (PRO)
# ==========================================
elif role == "Prestataire (Pro)":
    st.title("🛠️ Espace Pro")
    st.caption("En attente de missions...")

    if st.session_state.demande_active:
        demande = st.session_state.demande_active

        st.markdown(
            f"""
        <div class="offer-card">
            <h3 class="urgent">🔔 NOUVELLE MISSION : {demande["type"]}</h3>
            <p><strong>Détail :</strong> {demande["desc"]}</p>
            <p><strong>Urgence :</strong> {demande["urgence"]}</p>
            <p><small>Reçu à {demande["date"]}</small></p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.write("### Faire une offre :")
        col1, col2, col3 = st.columns(3)
        with col1:
            prix = st.number_input("Prix (DH)", min_value=0, value=50)
        with col2:
            temps = st.number_input("Temps (min)", min_value=5, value=30)
        with col3:
            st.write("")  # Espace
            st.write("")  # Espace
            if st.button("🚀 ENVOYER L'OFFRE"):
                # Créer l'offre et l'envoyer au client
                nouvelle_offre = {
                    "pro": "Garage Express (Toi)",
                    "prix": prix,
                    "temps": temps,
                    "tel": "0600123456",
                }
                st.session_state.offres_disponibles.append(nouvelle_offre)
                st.toast("Offre envoyée au client !", icon="✅")
    else:
        st.info("Aucune demande active pour le moment. Reste connecté.")
