import streamlit as st
from database.connection import db
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Gestionare Doctori",
    page_icon="👨‍⚕️",
    layout="wide"
)

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

def validate_email(email):
    """Validare simplă pentru email"""
    if email and '@' not in email:
        return False, "Email invalid"
    return True, "Valid"


def get_all_doctori():
    """Obține toți doctorii din baza de date"""
    try:
        query = """
            SELECT 
                d.id_doctor as ID,
                d.nume as Nume,
                d.prenume as Prenume,
                d.specializare as Specializare,
                d.grad_profesional as [Grad Profesional],
                d.telefon as Telefon,
                d.email as Email,
                s.nume_sectie as Sectie
            FROM Doctor d
            LEFT JOIN Sectie s ON d.id_sectie = s.id_sectie
            ORDER BY d.id_doctor DESC
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        st.error(f"Eroare la citirea doctorilor: {e}")
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


def get_specializari():
    """Lista de specializări medicale"""
    return [
        "Cardiologie",
        "Chirurgie Generală",
        "Neurologie",
        "Pediatrie",
        "Ortopedie",
        "Dermatologie",
        "Oftalmologie",
        "ORL",
        "Ginecologie",
        "Urologie",
        "Psihiatrie",
        "Oncologie",
        "Radiologie",
        "Anestezie și Terapie Intensivă",
        "Medicină Internă",
        "Alta"
    ]


def get_grade_profesionale():
    """Lista de grade profesionale"""
    return [
        "Medic Rezident",
        "Medic Specialist",
        "Medic Primar",
        "Șef Secție",
        "Director Medical"
    ]


def add_doctor(nume, prenume, specializare, telefon, email, grad_profesional, id_sectie):
    """Adaugă un doctor nou în baza de date"""
    try:
        # Convertim id_sectie la int Python sau None
        id_sectie_final = int(id_sectie) if id_sectie is not None else None
        
        query = """
            INSERT INTO Doctor 
            (nume, prenume, specializare, telefon, email, grad_profesional, id_sectie)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (nume, prenume, specializare, telefon, email, grad_profesional, id_sectie_final))
        return True, "✅ Doctor adăugat cu succes!"
    except Exception as e:
        return False, f"❌ Eroare: {str(e)}"


def update_doctor(id_doctor, nume, prenume, specializare, telefon, email, grad_profesional, id_sectie):
    """Actualizează datele unui doctor"""
    try:
        id_sectie_final = int(id_sectie) if id_sectie is not None else None
        id_doctor_final = int(id_doctor)
        
        query = """
            UPDATE Doctor 
            SET nume=?, prenume=?, specializare=?, telefon=?, 
                email=?, grad_profesional=?, id_sectie=?
            WHERE id_doctor=?
        """
        db.execute_query(query, (nume, prenume, specializare, telefon, email, grad_profesional, id_sectie_final, id_doctor_final))
        return True, "✅ Doctor actualizat cu succes!"
    except Exception as e:
        return False, f"❌ Eroare: {str(e)}"


def delete_doctor(id_doctor):
    """Șterge un doctor din baza de date"""
    try:
        id_doctor_final = int(id_doctor)
        
        query = "DELETE FROM Doctor WHERE id_doctor=?"
        db.execute_query(query, (id_doctor_final,))
        return True, "✅ Doctor șters cu succes!"
    except Exception as e:
        return False, f"❌ Eroare: {str(e)}"


def get_doctor_by_id(id_doctor):
    """Obține detaliile unui doctor specific"""
    try:
        query = "SELECT * FROM Doctor WHERE id_doctor=?"
        df = db.fetch_dataframe(query, params=(int(id_doctor),))
        if not df.empty:
            return df.iloc[0]
        return None
    except Exception as e:
        st.error(f"Eroare: {e}")
        return None


def get_doctor_statistics(id_doctor):
    """Obține statistici pentru un doctor"""
    try:
        query_programari = """
            SELECT COUNT(*) as total 
            FROM Programare 
            WHERE id_doctor=?
        """
        df_prog = db.fetch_dataframe(query_programari, params=(int(id_doctor),))
        total_programari = int(df_prog['total'].iloc[0]) if not df_prog.empty else 0
     
        query_diag = """
            SELECT COUNT(*) as total 
            FROM Diagnostic 
            WHERE id_doctor=?
        """
        df_diag = db.fetch_dataframe(query_diag, params=(int(id_doctor),))
        total_diagnostice = int(df_diag['total'].iloc[0]) if not df_diag.empty else 0
        
        return {
            'programari': total_programari,
            'diagnostice': total_diagnostice
        }
    except Exception as e:
        return {'programari': 0, 'diagnostice': 0}


# ===== INTERFAȚA UTILIZATOR =====

def main():
    st.title("👨‍⚕️ Gestionare Doctori")
    st.markdown("---")
    
    # Tabs pentru diferite operații
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Lista Doctori", 
        "➕ Adaugă Doctor", 
        "✏️ Modifică Doctor",
        "🔍 Caută Doctor"
    ])
    
    # ===== TAB 1: LISTA DOCTORI =====
    with tab1:
        st.markdown("### 📋 Toți Doctorii")
        
        # Butoane acțiuni
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔄 Reîmprospătează"):
                st.rerun()
        
        # Obține și afișează doctorii
        df_doctori = get_all_doctori()
        
        if not df_doctori.empty:
            st.info(f"📊 Total doctori: **{len(df_doctori)}**")
            
            # Filtrare pe specializare
            specializari_unice = ["Toate"] + sorted(df_doctori['Specializare'].unique().tolist())
            filtru_specializare = st.selectbox("Filtrează după Specializare:", specializari_unice)
            
            if filtru_specializare != "Toate":
                df_doctori = df_doctori[df_doctori['Specializare'] == filtru_specializare]
            
            # Afișează tabelul
            st.dataframe(
                df_doctori,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Email": st.column_config.TextColumn("Email", width="medium")
                }
            )
            
            # Opțiune de export
            csv = df_doctori.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarcă CSV",
                data=csv,
                file_name=f"doctori_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("📭 Nu există doctori în baza de date")
    
    # ===== TAB 2: ADAUGĂ DOCTOR =====
    with tab2:
        st.markdown("### ➕ Adaugă Doctor Nou")
        
        with st.form("form_adauga_doctor", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nume = st.text_input("Nume *", placeholder="Ionescu")
                prenume = st.text_input("Prenume *", placeholder="Maria")
                
                # Dropdown specializare cu opțiune personalizată
                specializari = get_specializari()
                specializare_selectata = st.selectbox("Specializare *", specializari)
                
                if specializare_selectata == "Alta":
                    specializare = st.text_input("Specificați Specializarea *", placeholder="Ex: Endocrinologie")
                else:
                    specializare = specializare_selectata
                
                grad_profesional = st.selectbox("Grad Profesional *", get_grade_profesionale())
            
            with col2:
                telefon = st.text_input("Telefon", placeholder="0712345678")
                email = st.text_input("Email *", placeholder="doctor@spital.ro")
                
                # Dropdown pentru secții
                df_sectii = get_sectii()
                if not df_sectii.empty:
                    sectie_options = ["Nicio secție"] + df_sectii['nume_sectie'].tolist()
                    sectie_selectata = st.selectbox("Secție", sectie_options)
                else:
                    st.warning("Nu există secții în baza de date")
                    sectie_selectata = "Nicio secție"
            
            submitted = st.form_submit_button("✅ Adaugă Doctor", use_container_width=True)
            
            if submitted:
                # Validări
                if not nume or not prenume or not specializare or not email:
                    st.error("❌ Câmpurile marcate cu * sunt obligatorii!")
                else:
                    # Validare email
                    is_valid, message = validate_email(email)
                    if not is_valid:
                        st.error(f"❌ {message}")
                    else:
                        # Determină id_sectie
                        id_sectie = None
                        if sectie_selectata != "Nicio secție":
                            id_sectie = df_sectii[df_sectii['nume_sectie'] == sectie_selectata]['id_sectie'].iloc[0]
                        
                        # Adaugă în baza de date
                        success, message = add_doctor(
                            nume, prenume, specializare,
                            telefon if telefon else None,
                            email,
                            grad_profesional,
                            id_sectie
                        )
                        
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
    
    # ===== TAB 3: MODIFICĂ DOCTOR =====
    with tab3:
        st.markdown("### ✏️ Modifică Doctor Existent")
        
        df_doctori = get_all_doctori()
        
        if not df_doctori.empty:
            # Selectează doctorul
            doctor_selectat = st.selectbox(
                "Selectează Doctor",
                options=df_doctori['ID'].tolist(),
                format_func=lambda x: f"ID {x} - Dr. {df_doctori[df_doctori['ID']==x]['Nume'].iloc[0]} {df_doctori[df_doctori['ID']==x]['Prenume'].iloc[0]} ({df_doctori[df_doctori['ID']==x]['Specializare'].iloc[0]})"
            )
            
            # Obține detaliile doctorului
            doctor = get_doctor_by_id(doctor_selectat)
            
            if doctor is not None:
                # Statistici doctor
                stats = get_doctor_statistics(doctor_selectat)
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric("📅 Total Programări", stats['programari'])
                with col_stat2:
                    st.metric("🩺 Total Diagnostice", stats['diagnostice'])
                
                st.markdown("---")
                
                with st.form("form_modifica_doctor"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nume = st.text_input("Nume *", value=doctor['nume'])
                        prenume = st.text_input("Prenume *", value=doctor['prenume'])
                        
                        # Specializare
                        specializari = get_specializari()
                        if doctor['specializare'] in specializari:
                            spec_index = specializari.index(doctor['specializare'])
                        else:
                            spec_index = specializari.index("Alta")
                        
                        specializare_selectata = st.selectbox("Specializare *", specializari, index=spec_index)
                        
                        if specializare_selectata == "Alta":
                            specializare = st.text_input("Specificați Specializarea *", value=doctor['specializare'])
                        else:
                            specializare = specializare_selectata
                        
                        # Grad profesional
                        grade = get_grade_profesionale()
                        grad_index = grade.index(doctor['grad_profesional']) if doctor['grad_profesional'] in grade else 0
                        grad_profesional = st.selectbox("Grad Profesional *", grade, index=grad_index)
                    
                    with col2:
                        telefon = st.text_input("Telefon", value=doctor['telefon'] if doctor['telefon'] else "")
                        email = st.text_input("Email *", value=doctor['email'] if doctor['email'] else "")
                        
                        # Dropdown pentru secții
                        df_sectii = get_sectii()
                        if not df_sectii.empty:
                            sectie_options = ["Nicio secție"] + df_sectii['nume_sectie'].tolist()
                            current_sectie = "Nicio secție"
                            if doctor['id_sectie']:
                                sectie_row = df_sectii[df_sectii['id_sectie'] == doctor['id_sectie']]
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
                        # Validare email
                        is_valid, message = validate_email(email)
                        if not is_valid:
                            st.error(f"❌ {message}")
                        else:
                            # Determină id_sectie
                            id_sectie = None
                            if sectie_selectata != "Nicio secție":
                                id_sectie = df_sectii[df_sectii['nume_sectie'] == sectie_selectata]['id_sectie'].iloc[0]
                            
                            success, msg = update_doctor(
                                doctor_selectat, nume, prenume, specializare,
                                telefon, email, grad_profesional, id_sectie
                            )
                            
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
                    
                    if submitted_delete:
                        # Verificăm dacă doctorul are programări sau diagnostice
                        if stats['programari'] > 0 or stats['diagnostice'] > 0:
                            st.error(f"❌ Nu poți șterge acest doctor! Are {stats['programari']} programări și {stats['diagnostice']} diagnostice asociate.")
                        else:
                            st.warning("⚠️ Ești sigur că vrei să ștergi acest doctor?")
                            if st.checkbox("DA, confirm ștergerea"):
                                success, msg = delete_doctor(doctor_selectat)
                                if success:
                                    st.success(msg)
                                else:
                                    st.error(msg)
        else:
            st.warning("📭 Nu există doctori în baza de date")
    
    # ===== TAB 4: CAUTĂ DOCTOR =====
    with tab4:
        st.markdown("### 🔍 Caută Doctor")
        
        search_term = st.text_input("Caută după Nume, Prenume sau Specializare", placeholder="Introduceți termenul de căutare")
        
        if search_term:
            df_doctori = get_all_doctori()
            
            if not df_doctori.empty:
                # Filtrare
                mask = (
                    df_doctori['Nume'].str.contains(search_term, case=False, na=False) |
                    df_doctori['Prenume'].str.contains(search_term, case=False, na=False) |
                    df_doctori['Specializare'].str.contains(search_term, case=False, na=False)
                )
                rezultate = df_doctori[mask]
                
                if not rezultate.empty:
                    st.success(f"✅ Găsite {len(rezultate)} rezultate")
                    st.dataframe(rezultate, use_container_width=True, hide_index=True)
                    
                    # Afișăm statistici pentru fiecare doctor găsit
                    st.markdown("#### 📊 Statistici Doctori Găsiți")
                    for _, row in rezultate.iterrows():
                        with st.expander(f"Dr. {row['Nume']} {row['Prenume']} - {row['Specializare']}"):
                            stats = get_doctor_statistics(row['ID'])
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Programări", stats['programari'])
                            with col2:
                                st.metric("Diagnostice", stats['diagnostice'])
                else:
                    st.warning("❌ Nu s-au găsit rezultate")
            else:
                st.info("📭 Baza de date este goală")


if __name__ == "__main__":
    main()