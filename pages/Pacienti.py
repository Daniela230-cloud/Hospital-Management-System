import streamlit as st
from database.connection import db
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Gestionare Pacienți",
    page_icon="👥",
    layout="wide"
)

# CSS Custom
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button {
        width: 100%;
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
        padding: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #0052a3;
    }
    </style>
""", unsafe_allow_html=True)


# ===== FUNCȚII PENTRU OPERAȚII CRUD =====

def validate_cnp(cnp):
    """Validează CNP-ul (trebuie să aibă 13 cifre)"""
    if not cnp:
        return False, "CNP este obligatoriu"
    if len(cnp) != 13:
        return False, "CNP trebuie să aibă exact 13 cifre"
    if not cnp.isdigit():
        return False, "CNP trebuie să conțină doar cifre"
    return True, "Valid"


def get_all_pacienti():
    """Obține toți pacienții din baza de date"""
    try:
        query = """
            SELECT 
                p.id_pacient as ID,
                p.nume as Nume,
                p.prenume as Prenume,
                p.CNP,
                CONVERT(VARCHAR, p.data_nasterii, 103) as [Data Nașterii],
                p.gen as Gen,
                p.telefon as Telefon,
                p.email as Email,
                s.nume_sectie as Sectie,
                CASE 
                    WHEN p.data_internare IS NOT NULL AND p.data_externare IS NULL 
                    THEN 'Internat' 
                    ELSE 'Extern' 
                END as Status
            FROM Pacient p
            LEFT JOIN Sectie s ON p.id_sectie = s.id_sectie
            ORDER BY p.id_pacient DESC
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        st.error(f"Eroare la citirea pacienților: {e}")
        return pd.DataFrame()


def get_sectii():
    """Obține lista de secții pentru dropdown"""
    try:
        query = "SELECT id_sectie, nume_sectie FROM Sectie ORDER BY nume_sectie"
        df = db.fetch_dataframe(query)
        return df
    except Exception as e:
        st.error(f"Eroare la citirea secțiilor: {e}")
        return pd.DataFrame()


def add_pacient(nume, prenume, cnp, data_nasterii, gen, adresa, telefon, email, id_sectie):
    """Adaugă un pacient nou în baza de date"""
    try:
        # Convertim id_sectie la int Python sau None
        id_sectie_final = int(id_sectie) if id_sectie is not None else None
        
        query = """
            INSERT INTO Pacient 
            (nume, prenume, CNP, data_nasterii, gen, adresa, telefon, email, id_sectie)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (nume, prenume, cnp, data_nasterii, gen, adresa, telefon, email, id_sectie_final))
        return True, "✅ Pacient adăugat cu succes!"
    except Exception as e:
        return False, f"❌ Eroare: {str(e)}"


def update_pacient(id_pacient, nume, prenume, cnp, data_nasterii, gen, adresa, telefon, email, id_sectie):
    """Actualizează datele unui pacient"""
    try:
        # Convertim id_sectie și id_pacient la int Python
        id_sectie_final = int(id_sectie) if id_sectie is not None else None
        id_pacient_final = int(id_pacient)
        
        query = """
            UPDATE Pacient 
            SET nume=?, prenume=?, CNP=?, data_nasterii=?, gen=?, 
                adresa=?, telefon=?, email=?, id_sectie=?
            WHERE id_pacient=?
        """
        db.execute_query(query, (nume, prenume, cnp, data_nasterii, gen, adresa, telefon, email, id_sectie_final, id_pacient_final))
        return True, "✅ Pacient actualizat cu succes!"
    except Exception as e:
        return False, f"❌ Eroare: {str(e)}"


def delete_pacient(id_pacient):
    """Șterge un pacient din baza de date"""
    try:
        # Convertim la int Python
        id_pacient_final = int(id_pacient)
        
        query = "DELETE FROM Pacient WHERE id_pacient=?"
        db.execute_query(query, (id_pacient_final,))
        return True, "✅ Pacient șters cu succes!"
    except Exception as e:
        return False, f"❌ Eroare: {str(e)}"


def get_pacient_by_id(id_pacient):
    """Obține detaliile unui pacient specific"""
    try:
        query = """
            SELECT * FROM Pacient WHERE id_pacient=?
        """
        df = db.fetch_dataframe(query, params=(id_pacient,))
        if not df.empty:
            return df.iloc[0]
        return None
    except Exception as e:
        st.error(f"Eroare: {e}")
        return None


# ===== INTERFAȚA UTILIZATOR =====

def main():
    st.title("👥 Gestionare Pacienți")
    st.markdown("---")
    
    # Tabs pentru diferite operații
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Lista Pacienți", 
        "➕ Adaugă Pacient", 
        "✏️ Modifică Pacient",
        "🔍 Caută Pacient"
    ])
    
    # ===== TAB 1: LISTA PACIENȚI =====
    with tab1:
        st.markdown("### 📋 Toți Pacienții")
        
        # Buton refresh
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔄 Reîmprospătează"):
                st.rerun()
        
        # Obține și afișează pacienții
        df_pacienti = get_all_pacienti()
        
        if not df_pacienti.empty:
            st.info(f"📊 Total pacienți: **{len(df_pacienti)}**")
            
            # Afișează tabelul
            st.dataframe(
                df_pacienti,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Status": st.column_config.TextColumn(
                        "Status",
                        help="Internat sau Extern"
                    )
                }
            )
            
            # Opțiune de export
            csv = df_pacienti.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarcă CSV",
                data=csv,
                file_name=f"pacienti_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("📭 Nu există pacienți în baza de date")
    
    # ===== TAB 2: ADAUGĂ PACIENT =====
    with tab2:
        st.markdown("### ➕ Adaugă Pacient Nou")
        
        with st.form("form_adauga_pacient", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nume = st.text_input("Nume *", placeholder="Popescu")
                prenume = st.text_input("Prenume *", placeholder="Ion")
                cnp = st.text_input("CNP *", placeholder="1234567890123", max_chars=13)
                data_nasterii = st.date_input("Data Nașterii *")
                gen = st.selectbox("Gen *", ["M", "F"])
            
            with col2:
                adresa = st.text_input("Adresă", placeholder="Str. Exemplu, Nr. 1")
                telefon = st.text_input("Telefon", placeholder="0712345678")
                email = st.text_input("Email", placeholder="pacient@email.com")
                
                # Dropdown pentru secții
                df_sectii = get_sectii()
                if not df_sectii.empty:
                    sectie_options = ["Nicio secție"] + df_sectii['nume_sectie'].tolist()
                    sectie_selectata = st.selectbox("Secție", sectie_options)
                else:
                    st.warning("Nu există secții în baza de date")
                    sectie_selectata = "Nicio secție"
            
            submitted = st.form_submit_button("✅ Adaugă Pacient", use_container_width=True)
            
            if submitted:
                # Validări
                if not nume or not prenume or not cnp:
                    st.error("❌ Câmpurile marcate cu * sunt obligatorii!")
                else:
                    # Validare CNP
                    is_valid, message = validate_cnp(cnp)
                    if not is_valid:
                        st.error(f"❌ {message}")
                    else:
                        # Determină id_sectie
                        id_sectie = None
                        if sectie_selectata != "Nicio secție":
                            id_sectie = df_sectii[df_sectii['nume_sectie'] == sectie_selectata]['id_sectie'].iloc[0]
                        
                        # Adaugă în baza de date
                        success, message = add_pacient(
                            nume, prenume, cnp, data_nasterii, gen,
                            adresa if adresa else None,
                            telefon if telefon else None,
                            email if email else None,
                            id_sectie
                        )
                        
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
    
    # ===== TAB 3: MODIFICĂ PACIENT =====
    with tab3:
        st.markdown("### ✏️ Modifică Pacient Existent")
        
        df_pacienti = get_all_pacienti()
        
        if not df_pacienti.empty:
            # Selectează pacientul
            pacient_selectat = st.selectbox(
                "Selectează Pacient",
                options=df_pacienti['ID'].tolist(),
                format_func=lambda x: f"ID {x} - {df_pacienti[df_pacienti['ID']==x]['Nume'].iloc[0]} {df_pacienti[df_pacienti['ID']==x]['Prenume'].iloc[0]}"
            )
            
            # Obține detaliile pacientului
            pacient = get_pacient_by_id(pacient_selectat)
            
            if pacient is not None:
                with st.form("form_modifica_pacient"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nume = st.text_input("Nume *", value=pacient['nume'])
                        prenume = st.text_input("Prenume *", value=pacient['prenume'])
                        cnp = st.text_input("CNP *", value=pacient['CNP'], max_chars=13)
                        data_nasterii = st.date_input("Data Nașterii *", value=pacient['data_nasterii'])
                        gen = st.selectbox("Gen *", ["M", "F"], index=0 if pacient['gen']=='M' else 1)
                    
                    with col2:
                        adresa = st.text_input("Adresă", value=pacient['adresa'] if pacient['adresa'] else "")
                        telefon = st.text_input("Telefon", value=pacient['telefon'] if pacient['telefon'] else "")
                        email = st.text_input("Email", value=pacient['email'] if pacient['email'] else "")
                        
                        # Dropdown pentru secții
                        df_sectii = get_sectii()
                        if not df_sectii.empty:
                            sectie_options = ["Nicio secție"] + df_sectii['nume_sectie'].tolist()
                            current_sectie = "Nicio secție"
                            if pacient['id_sectie']:
                                sectie_row = df_sectii[df_sectii['id_sectie'] == pacient['id_sectie']]
                                if not sectie_row.empty:
                                    current_sectie = sectie_row['nume_sectie'].iloc[0]
                            
                            sectie_selectata = st.selectbox("Secție", sectie_options, 
                                                           index=sectie_options.index(current_sectie))
                    
                    col_update, col_delete = st.columns(2)
                    
                    with col_update:
                        submitted_update = st.form_submit_button("✅ Actualizează", use_container_width=True)
                    
                    with col_delete:
                        submitted_delete = st.form_submit_button("🗑️ Șterge", use_container_width=True, type="secondary")
                    
                    if submitted_update:
                        # Validări
                        is_valid, message = validate_cnp(cnp)
                        if not is_valid:
                            st.error(f"❌ {message}")
                        else:
                            # Determină id_sectie
                            id_sectie = None
                            if sectie_selectata != "Nicio secție":
                                id_sectie = df_sectii[df_sectii['nume_sectie'] == sectie_selectata]['id_sectie'].iloc[0]
                            
                            success, msg = update_pacient(
                                pacient_selectat, nume, prenume, cnp, data_nasterii, gen,
                                adresa, telefon, email, id_sectie
                            )
                            
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
                    
                    if submitted_delete:
                        # Confirmare ștergere
                        st.warning("⚠️ Ești sigur că vrei să ștergi acest pacient?")
                        if st.checkbox("DA, șterge definitiv"):
                            success, msg = delete_pacient(pacient_selectat)
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
        else:
            st.warning("📭 Nu există pacienți în baza de date")
    
    # ===== TAB 4: CAUTĂ PACIENT =====
    with tab4:
        st.markdown("### 🔍 Caută Pacient")
        
        search_term = st.text_input("Caută după Nume, Prenume sau CNP", placeholder="Introduceți termenul de căutare")
        
        if search_term:
            df_pacienti = get_all_pacienti()
            
            if not df_pacienti.empty:
                # Filtrare
                mask = (
                    df_pacienti['Nume'].str.contains(search_term, case=False, na=False) |
                    df_pacienti['Prenume'].str.contains(search_term, case=False, na=False) |
                    df_pacienti['CNP'].str.contains(search_term, case=False, na=False)
                )
                rezultate = df_pacienti[mask]
                
                if not rezultate.empty:
                    st.success(f"✅ Găsite {len(rezultate)} rezultate")
                    st.dataframe(rezultate, use_container_width=True, hide_index=True)
                else:
                    st.warning("❌ Nu s-au găsit rezultate")
            else:
                st.info("📭 Baza de date este goală")


if __name__ == "__main__":
    main()