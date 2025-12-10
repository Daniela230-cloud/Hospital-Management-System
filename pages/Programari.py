import streamlit as st
from database.connection import db
import pandas as pd
from datetime import datetime, time, timedelta

st.set_page_config(
    page_title="Gestionare Programări",
    page_icon="📅",
    layout="wide"
)

# CSS Custom
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button {
        width: 100%;
        color: white;
        border-radius: 5px;
        padding: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #0052a3;
    }
    .programare-card {
        background-color: #1a1a1a;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)


# ===== FUNCȚII PENTRU OPERAȚII CRUD =====

def get_all_programari():
    """Obține toate programările din baza de date"""
    try:
        query = """
            SELECT 
                pr.id_programare as ID,
                p.nume + ' ' + p.prenume as Pacient,
                d.nume + ' ' + d.prenume as Doctor,
                s.nume_sectie as Sectie,
                CONVERT(VARCHAR, pr.data_programare, 103) as Data,
                CONVERT(VARCHAR(5), pr.ora_programare, 108) as Ora,
                pr.tip_programare as [Tip Programare],
                pr.cauza as Cauza,
                pr.id_pacient,
                pr.id_doctor,
                pr.id_sectie,
                pr.data_programare as data_sort,
                pr.ora_programare as ora_sort
            FROM Programare pr
            JOIN Pacient p ON pr.id_pacient = p.id_pacient
            JOIN Doctor d ON pr.id_doctor = d.id_doctor
            LEFT JOIN Sectie s ON pr.id_sectie = s.id_sectie
            ORDER BY pr.data_programare DESC, pr.ora_programare DESC
        """
        df = db.fetch_dataframe(query)
        if not df.empty:
            df['ID'] = df['ID'].astype(int)
        return df
    except Exception as e:
        st.error(f"Eroare la citirea programărilor: {e}")
        return pd.DataFrame()


def get_pacienti():
    """Obține lista de pacienți pentru dropdown"""
    try:
        query = """
            SELECT 
                id_pacient, 
                nume + ' ' + prenume + ' (CNP: ' + CNP + ')' as nume_complet
            FROM Pacient
            ORDER BY nume, prenume
        """
        df = db.fetch_dataframe(query)
        if not df.empty:
            df['id_pacient'] = df['id_pacient'].astype(int)
        return df
    except Exception as e:
        st.error(f"Eroare la citirea pacienților: {e}")
        return pd.DataFrame()


def get_doctori():
    """Obține lista de doctori pentru dropdown"""
    try:
        query = """
            SELECT 
                id_doctor, 
                nume + ' ' + prenume + ' - ' + specializare as nume_complet
            FROM Doctor
            ORDER BY nume, prenume
        """
        df = db.fetch_dataframe(query)
        if not df.empty:
            df['id_doctor'] = df['id_doctor'].astype(int)
        return df
    except Exception as e:
        st.error(f"Eroare la citirea doctorilor: {e}")
        return pd.DataFrame()


def get_sectii():
    """Obține lista de secții pentru dropdown"""
    try:
        query = "SELECT id_sectie, nume_sectie FROM Sectie ORDER BY nume_sectie"
        df = db.fetch_dataframe(query)
        if not df.empty:
            df['id_sectie'] = df['id_sectie'].astype(int)
        return df
    except Exception as e:
        st.error(f"Eroare la citirea secțiilor: {e}")
        return pd.DataFrame()


def get_tipuri_programare():
    """Lista de tipuri de programări"""
    return [
        "Consultație",
        "Control",
        "Investigații",
        "Intervenție chirurgicală",
        "Tratament",
        "Analize",
        "Urgență",
        "Alta"
    ]


def check_doctor_availability(id_doctor, data_programare, ora_programare):
    """Verifică dacă doctorul este disponibil la data și ora specificate"""
    try:
        query = """
            SELECT COUNT(*) as count
            FROM Programare
            WHERE id_doctor = ?
            AND data_programare = ?
            AND ora_programare = ?
        """
        df = db.fetch_dataframe(query, params=(int(id_doctor), data_programare, ora_programare))
        count = int(df['count'].iloc[0]) if not df.empty else 0
        return count == 0
    except Exception as e:
        st.error(f"Eroare la verificarea disponibilității: {e}")
        return False


def get_programari_doctor(id_doctor, data_programare):
    """Obține programările unui doctor pentru o anumită dată"""
    try:
        query = """
            SELECT 
                CONVERT(VARCHAR(5), ora_programare, 108) as Ora,
                p.nume + ' ' + p.prenume as Pacient,
                tip_programare as Tip
            FROM Programare pr
            JOIN Pacient p ON pr.id_pacient = p.id_pacient
            WHERE pr.id_doctor = ?
            AND pr.data_programare = ?
            ORDER BY pr.ora_programare
        """
        df = db.fetch_dataframe(query, params=(int(id_doctor), data_programare))
        return df
    except Exception as e:
        return pd.DataFrame()


def add_programare(id_pacient, id_doctor, id_sectie, data_programare, ora_programare, tip_programare, cauza):
    """Adaugă o programare nouă"""
    try:
        id_pacient_final = int(id_pacient)
        id_doctor_final = int(id_doctor)
        id_sectie_final = int(id_sectie) if id_sectie is not None else None
        
        query = """
            INSERT INTO Programare 
            (id_pacient, id_doctor, id_sectie, data_programare, ora_programare, tip_programare, cauza)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (id_pacient_final, id_doctor_final, id_sectie_final, 
                                 data_programare, ora_programare, tip_programare, cauza))
        return True, "✅ Programare adăugată cu succes!"
    except Exception as e:
        return False, f"❌ Eroare: {str(e)}"


def update_programare(id_programare, id_pacient, id_doctor, id_sectie, data_programare, ora_programare, tip_programare, cauza):
    """Actualizează o programare existentă"""
    try:
        id_programare_final = int(id_programare)
        id_pacient_final = int(id_pacient)
        id_doctor_final = int(id_doctor)
        id_sectie_final = int(id_sectie) if id_sectie is not None else None
        
        query = """
            UPDATE Programare
            SET id_pacient=?, id_doctor=?, id_sectie=?, data_programare=?, 
                ora_programare=?, tip_programare=?, cauza=?
            WHERE id_programare=?
        """
        db.execute_query(query, (id_pacient_final, id_doctor_final, id_sectie_final,
                                 data_programare, ora_programare, tip_programare, cauza, id_programare_final))
        return True, "✅ Programare actualizată cu succes!"
    except Exception as e:
        return False, f"❌ Eroare: {str(e)}"


def delete_programare(id_programare):
    """Șterge o programare"""
    try:
        id_programare_final = int(id_programare)
        query = "DELETE FROM Programare WHERE id_programare=?"
        db.execute_query(query, (id_programare_final,))
        return True, "✅ Programare ștearsă cu succes!"
    except Exception as e:
        return False, f"❌ Eroare: {str(e)}"


def get_programare_by_id(id_programare):
    """Obține detaliile unei programări"""
    try:
        query = "SELECT * FROM Programare WHERE id_programare=?"
        df = db.fetch_dataframe(query, params=(int(id_programare),))
        if not df.empty:
            return df.iloc[0]
        return None
    except Exception as e:
        st.error(f"Eroare: {e}")
        return None


def get_programari_today():
    """Obține programările de astăzi"""
    try:
        query = """
            SELECT 
                CONVERT(VARCHAR(5), pr.ora_programare, 108) as Ora,
                p.nume + ' ' + p.prenume as Pacient,
                d.nume + ' ' + d.prenume as Doctor,
                pr.tip_programare as Tip
            FROM Programare pr
            JOIN Pacient p ON pr.id_pacient = p.id_pacient
            JOIN Doctor d ON pr.id_doctor = d.id_doctor
            WHERE CAST(pr.data_programare AS DATE) = CAST(GETDATE() AS DATE)
            ORDER BY pr.ora_programare
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        return pd.DataFrame()


def get_programari_viitoare():
    """Obține programările viitoare (următoarele 7 zile)"""
    try:
        query = """
            SELECT 
                CONVERT(VARCHAR, pr.data_programare, 103) as Data,
                CONVERT(VARCHAR(5), pr.ora_programare, 108) as Ora,
                p.nume + ' ' + p.prenume as Pacient,
                d.nume + ' ' + d.prenume as Doctor,
                pr.tip_programare as Tip
            FROM Programare pr
            JOIN Pacient p ON pr.id_pacient = p.id_pacient
            JOIN Doctor d ON pr.id_doctor = d.id_doctor
            WHERE pr.data_programare BETWEEN CAST(GETDATE() AS DATE) 
                  AND DATEADD(day, 7, CAST(GETDATE() AS DATE))
            ORDER BY pr.data_programare, pr.ora_programare
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        return pd.DataFrame()


# ===== INTERFAȚA UTILIZATOR =====

def main():
    st.title("📅 Gestionare Programări")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Lista Programări",
        "➕ Adaugă Programare",
        "✏️ Modifică Programare",
        "📆 Agenda Doctor",
        "🔔 Programări Astăzi"
    ])
    
    # ===== TAB 1: LISTA PROGRAMĂRI =====
    with tab1:
        st.markdown("### 📋 Toate Programările")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🔄 Reîmprospătează"):
                st.rerun()
        
        df_programari = get_all_programari()
        
        if not df_programari.empty:
            st.info(f"📊 Total programări: **{len(df_programari)}**")
            
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                doctori_unici = ["Toți"] + sorted(df_programari['Doctor'].unique().tolist())
                filtru_doctor = st.selectbox("Doctor:", doctori_unici)
            
            with col_f2:
                tipuri_unice = ["Toate"] + sorted(df_programari['Tip Programare'].unique().tolist())
                filtru_tip = st.selectbox("Tip:", tipuri_unice)
            
            with col_f3:
                perioada = st.selectbox("Perioadă:", ["Toate", "Astăzi", "Săptămâna aceasta", "Luna aceasta", "Viitoare"])
            
            df_filtrat = df_programari.copy()
            
            if filtru_doctor != "Toți":
                df_filtrat = df_filtrat[df_filtrat['Doctor'] == filtru_doctor]
            
            if filtru_tip != "Toate":
                df_filtrat = df_filtrat[df_filtrat['Tip Programare'] == filtru_tip]
            
            if perioada != "Toate":
                today = pd.Timestamp.now().normalize()
                if perioada == "Astăzi":
                    df_filtrat = df_filtrat[pd.to_datetime(df_filtrat['data_sort']) == today]
                elif perioada == "Săptămâna aceasta":
                    week_end = today + timedelta(days=7)
                    df_filtrat = df_filtrat[
                        (pd.to_datetime(df_filtrat['data_sort']) >= today) & 
                        (pd.to_datetime(df_filtrat['data_sort']) <= week_end)
                    ]
                elif perioada == "Luna aceasta":
                    month_end = today + timedelta(days=30)
                    df_filtrat = df_filtrat[
                        (pd.to_datetime(df_filtrat['data_sort']) >= today) & 
                        (pd.to_datetime(df_filtrat['data_sort']) <= month_end)
                    ]
                elif perioada == "Viitoare":
                    df_filtrat = df_filtrat[pd.to_datetime(df_filtrat['data_sort']) >= today]
            
            df_display = df_filtrat[['ID', 'Pacient', 'Doctor', 'Sectie', 'Data', 'Ora', 'Tip Programare', 'Cauza']].copy()
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Cauza": st.column_config.TextColumn("Cauza", width="large")
                }
            )
            
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarcă CSV",
                data=csv,
                file_name=f"programari_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("📭 Nu există programări în baza de date")
    
    # ===== TAB 2: ADAUGĂ PROGRAMARE =====
    with tab2:
        st.markdown("### ➕ Adaugă Programare Nouă")
        
        df_pacienti = get_pacienti()
        df_doctori = get_doctori()
        df_sectii = get_sectii()
        
        if df_pacienti.empty or df_doctori.empty:
            st.error("❌ Trebuie să existe pacienți și doctori în baza de date pentru a crea programări!")
        else:
            with st.form("form_adauga_programare", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    pacient_ids = [int(x) for x in df_pacienti['id_pacient'].tolist()]
                    pacient_selectat = st.selectbox(
                        "Pacient *",
                        options=pacient_ids,
                        format_func=lambda x: df_pacienti[df_pacienti['id_pacient']==x]['nume_complet'].iloc[0]
                    )
                    
                    doctor_ids = [int(x) for x in df_doctori['id_doctor'].tolist()]
                    doctor_selectat = st.selectbox(
                        "Doctor *",
                        options=doctor_ids,
                        format_func=lambda x: df_doctori[df_doctori['id_doctor']==x]['nume_complet'].iloc[0]
                    )
                    
                    if not df_sectii.empty:
                        sectie_options = ["Nicio secție"] + df_sectii['nume_sectie'].tolist()
                        sectie_selectata = st.selectbox("Secție", sectie_options)
                    else:
                        sectie_selectata = "Nicio secție"
                
                with col2:
                    data_programare = st.date_input("Data Programării *", min_value=datetime.now().date())
                    ora_programare = st.time_input("Ora Programării *", value=time(9, 0))
                    
                    tipuri = get_tipuri_programare()
                    tip_selectat = st.selectbox("Tip Programare *", tipuri)
                    
                    if tip_selectat == "Alta":
                        tip_programare = st.text_input("Specificați Tipul *")
                    else:
                        tip_programare = tip_selectat
                
                cauza = st.text_area("Cauza / Motivul Programării", placeholder="Descrieți motivul programării...")
                
                submitted = st.form_submit_button("✅ Adaugă Programare", use_container_width=True)
                
                if submitted:
                    if not check_doctor_availability(doctor_selectat, data_programare, ora_programare):
                        st.error("❌ Doctorul selectat are deja o programare la această dată și oră!")
                    else:
                        id_sectie = None
                        if sectie_selectata != "Nicio secție":
                            id_sectie = df_sectii[df_sectii['nume_sectie'] == sectie_selectata]['id_sectie'].iloc[0]
                        
                        success, message = add_programare(
                            pacient_selectat, doctor_selectat, id_sectie,
                            data_programare, ora_programare, tip_programare,
                            cauza if cauza else None
                        )
                        
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
    
    # ===== TAB 3: MODIFICĂ PROGRAMARE =====
    with tab3:
        st.markdown("### ✏️ Modifică Programare Existentă")
        
        df_programari = get_all_programari()
        
        if not df_programari.empty:
            programare_ids = [int(x) for x in df_programari['ID'].tolist()]
            programare_selectata = st.selectbox(
                "Selectează Programare",
                options=programare_ids,
                format_func=lambda x: f"ID {x} - {df_programari[df_programari['ID']==x]['Data'].iloc[0]} {df_programari[df_programari['ID']==x]['Ora'].iloc[0]} - {df_programari[df_programari['ID']==x]['Pacient'].iloc[0]} ({df_programari[df_programari['ID']==x]['Doctor'].iloc[0]})"
            )
            
            programare = get_programare_by_id(programare_selectata)
            
            if programare is not None:
                df_pacienti = get_pacienti()
                df_doctori = get_doctori()
                df_sectii = get_sectii()
                
                with st.form("form_modifica_programare"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Pacient
                        pacient_ids = [int(x) for x in df_pacienti['id_pacient'].tolist()]
                        pacient_index_row = df_pacienti[df_pacienti['id_pacient'] == programare['id_pacient']]
                        if not pacient_index_row.empty:
                            pacient_index = int(pacient_index_row.index[0])
                        else:
                            pacient_index = 0
                        
                        pacient_selectat = st.selectbox(
                            "Pacient *",
                            options=pacient_ids,
                            index=pacient_index,
                            format_func=lambda x: df_pacienti[df_pacienti['id_pacient']==x]['nume_complet'].iloc[0]
                        )
                        
                        # Doctor
                        doctor_ids = [int(x) for x in df_doctori['id_doctor'].tolist()]
                        doctor_index_row = df_doctori[df_doctori['id_doctor'] == programare['id_doctor']]
                        if not doctor_index_row.empty:
                            doctor_index = int(doctor_index_row.index[0])
                        else:
                            doctor_index = 0
                        
                        doctor_selectat = st.selectbox(
                            "Doctor *",
                            options=doctor_ids,
                            index=doctor_index,
                            format_func=lambda x: df_doctori[df_doctori['id_doctor']==x]['nume_complet'].iloc[0]
                        )
                        
                        # Secție
                        if not df_sectii.empty:
                            sectie_options = ["Nicio secție"] + df_sectii['nume_sectie'].tolist()
                            current_sectie = "Nicio secție"
                            if programare['id_sectie']:
                                sectie_row = df_sectii[df_sectii['id_sectie'] == programare['id_sectie']]
                                if not sectie_row.empty:
                                    current_sectie = sectie_row['nume_sectie'].iloc[0]
                            sectie_selectata = st.selectbox("Secție", sectie_options, 
                                                           index=sectie_options.index(current_sectie))
                    
                    with col2:
                        data_programare = st.date_input("Data *", value=programare['data_programare'])
                        ora_programare = st.time_input("Ora *", value=programare['ora_programare'])
                        
                        tipuri = get_tipuri_programare()
                        if programare['tip_programare'] in tipuri:
                            tip_index = tipuri.index(programare['tip_programare'])
                        else:
                            tip_index = tipuri.index("Alta")
                        
                        tip_selectat = st.selectbox("Tip *", tipuri, index=tip_index)
                        
                        if tip_selectat == "Alta":
                            tip_programare = st.text_input("Specificați *", value=programare['tip_programare'])
                        else:
                            tip_programare = tip_selectat
                    
                    cauza = st.text_area("Cauza", value=programare['cauza'] if programare['cauza'] else "")
                    
                    col_update, col_delete = st.columns(2)
                    
                    with col_update:
                        submitted_update = st.form_submit_button("✅ Actualizează", use_container_width=True)
                    
                    with col_delete:
                        submitted_delete = st.form_submit_button("🗑️ Șterge", use_container_width=True, type="secondary")
                    
                    if submitted_update:
                        id_sectie = None
                        if sectie_selectata != "Nicio secție":
                            id_sectie = df_sectii[df_sectii['nume_sectie'] == sectie_selectata]['id_sectie'].iloc[0]
                        
                        success, msg = update_programare(
                            programare_selectata, pacient_selectat, doctor_selectat, id_sectie,
                            data_programare, ora_programare, tip_programare, cauza
                        )
                        
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    
                    if submitted_delete:
                        st.warning("⚠️ Ștergi această programare?")
                        if st.checkbox("DA, confirm"):
                            success, msg = delete_programare(programare_selectata)
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
        else:
            st.warning("📭 Nu există programări")
    
    # ===== TAB 4: AGENDA DOCTOR =====
    with tab4:
        st.markdown("### 📆 Agenda Doctor")
        
        df_doctori = get_doctori()
        
        if not df_doctori.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                doctor_ids = [int(x) for x in df_doctori['id_doctor'].tolist()]
                doctor_selectat = st.selectbox(
                    "Selectează Doctor",
                    options=doctor_ids,
                    format_func=lambda x: df_doctori[df_doctori['id_doctor']==x]['nume_complet'].iloc[0]
                )
            
            with col2:
                data_selectata = st.date_input("Data", value=datetime.now().date())
            
            df_agenda = get_programari_doctor(doctor_selectat, data_selectata)
            
            if not df_agenda.empty:
                st.success(f"📅 **{len(df_agenda)}** programări găsite")
                
                for _, row in df_agenda.iterrows():
                    st.markdown(f"""
                    <div class="programare-card">
                        <strong>🕐 {row['Ora']}</strong> - {row['Pacient']} 
                        <br><small>Tip: {row['Tip']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"📭 Nicio programare pentru data {data_selectata.strftime('%d.%m.%Y')}")
        else:
            st.warning("Nu există doctori în baza de date")
    
    # ===== TAB 5: PROGRAMĂRI ASTĂZI =====
    with tab5:
        st.markdown("### 🔔 Programări Astăzi")
        
        df_today = get_programari_today()
        
        if not df_today.empty:
            st.success(f"📅 **{len(df_today)}** programări astăzi")
            
            st.dataframe(
                df_today,
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("---")
            st.markdown("### 📆 Programări Următoarele 7 Zile")
            
            df_viitoare = get_programari_viitoare()
            
            if not df_viitoare.empty:
                st.info(f"📊 **{len(df_viitoare)}** programări")
                st.dataframe(df_viitoare, use_container_width=True, hide_index=True)
            else:
                st.info("📭 Nicio programare în următoarele 7 zile")
        else:
            st.info("📭 Nicio programare astăzi")


if __name__ == "__main__":
    main()