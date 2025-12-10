import streamlit as st
from database.connection import db  
import pandas as pd

st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
            
    .main { padding: 2rem; }
    .stButton>button {
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #0052a3;
    }
    </style>
""", unsafe_allow_html=True)


def get_statistics():
    """Funcție care obține statistici REALE din baza de date"""
    try:
        # 1. Total pacienți
        query_pacienti = "SELECT COUNT(*) as total FROM Pacient"
        df_pacienti = db.fetch_dataframe(query_pacienti)
        total_pacienti = int(df_pacienti['total'].iloc[0])
        
        # 2. Total doctori
        query_doctori = "SELECT COUNT(*) as total FROM Doctor"
        df_doctori = db.fetch_dataframe(query_doctori)
        total_doctori = int(df_doctori['total'].iloc[0])
        
        # 3. Programări astăzi
        query_programari = """
            SELECT COUNT(*) as total 
            FROM Programare 
            WHERE CAST(data_programare AS DATE) = CAST(GETDATE() AS DATE)
        """
        df_programari = db.fetch_dataframe(query_programari)
        programari_astazi = int(df_programari['total'].iloc[0])
        
        # 4. Pacienți internați (fără data de externare)
        query_internati = """
            SELECT COUNT(*) as total 
            FROM Pacient 
            WHERE data_internare IS NOT NULL 
            AND data_externare IS NULL
        """
        df_internati = db.fetch_dataframe(query_internati)
        pacienti_internati = int(df_internati['total'].iloc[0])
        
        return {
            'total_pacienti': total_pacienti,
            'total_doctori': total_doctori,
            'programari_astazi': programari_astazi,
            'pacienti_internati': pacienti_internati,
            'success': True
        }
    except Exception as e:
        st.error(f"❌ Eroare la citirea datelor: {str(e)}")
        return {
            'total_pacienti': 0,
            'total_doctori': 0,
            'programari_astazi': 0,
            'pacienti_internati': 0,
            'success': False
        }


def get_recent_appointments():
    """Obține ultimele 5 programări"""
    try:
        query = """
            SELECT TOP 5
                p.nume + ' ' + p.prenume as Pacient,
                d.nume + ' ' + d.prenume as Doctor,
                s.nume_sectie as Sectie,
                CONVERT(VARCHAR, pr.data_programare, 103) as Data,
                CONVERT(VARCHAR(5), pr.ora_programare, 108) as Ora,
                pr.tip_programare as Tip
            FROM Programare pr
            JOIN Pacient p ON pr.id_pacient = p.id_pacient
            JOIN Doctor d ON pr.id_doctor = d.id_doctor
            LEFT JOIN Sectie s ON pr.id_sectie = s.id_sectie
            ORDER BY pr.data_programare DESC, pr.ora_programare DESC
        """
        df = db.fetch_dataframe(query)
        return df
    except Exception as e:
        st.warning(f"Nu se pot încărca programările: {str(e)}")
        return pd.DataFrame()


def get_top_sectii():
    """Obține secțiile cu cei mai mulți pacienți"""
    try:
        query = """
            SELECT TOP 5
                s.nume_sectie as Sectie,
                COUNT(p.id_pacient) as Numar_Pacienti
            FROM Sectie s
            LEFT JOIN Pacient p ON s.id_sectie = p.id_sectie
            GROUP BY s.nume_sectie
            ORDER BY COUNT(p.id_pacient) DESC
        """
        df = db.fetch_dataframe(query)
        return df
    except Exception as e:
        st.warning(f"Nu se pot încărca secțiile: {str(e)}")
        return pd.DataFrame()


def main():
    st.title("🏥 Sistem Management Spital")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 Navigare")
        st.info("👈 Selectează o pagină din meniul lateral")
        
        st.markdown("---")
      
        if st.button("🔄 Reîmprospătează Date"):
            st.rerun()
    

    # ===== SECȚIUNEA 1: STATISTICI GENERALE =====
    st.markdown("## 📊 Statistici Generale")
    
    stats = get_statistics()
    
    if stats['success']:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👥 Pacienți Total",
                value=stats['total_pacienti']
            )
        
        with col2:
            st.metric(
                label="👨‍⚕️ Doctori Activi",
                value=stats['total_doctori']
            )
        
        with col3:
            st.metric(
                label="📅 Programări Astăzi",
                value=stats['programari_astazi']
            )
        
        with col4:
            st.metric(
                label="🏥 Pacienți Internați",
                value=stats['pacienti_internati']
            )
        
        st.success("✅ Sistem operațional - Date actualizate")
    else:
        st.error("❌ Nu se pot încărca datele. Verifică conexiunea la baza de date.")
    
    st.markdown("---")
    
    # ===== SECȚIUNEA 2: TABELE CU DATE =====
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### 📅 Ultimele Programări")
        df_programari = get_recent_appointments()
        
        if not df_programari.empty:
            st.dataframe(
                df_programari,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("📭 Nu există programări înregistrate")
    
    with col_right:
        st.markdown("### 🏥 Secții după număr de pacienți")
        df_sectii = get_top_sectii()
        
        if not df_sectii.empty:
            st.dataframe(
                df_sectii,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("📭 Nu există date despre secții")
    

    

if __name__ == "__main__":
    main()