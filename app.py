import streamlit as st
import pandas as pd
import datetime

# Load mock data (replace with actual CSV or DB calls in real usage)
@st.cache_data
def load_data():
    patients = pd.read_csv('mock_patients.csv')
    encounters = pd.read_csv('mock_encounters.csv')
    lab_results = pd.read_csv('mock_lab_results.csv')
    vitals = pd.read_csv('mock_vitals.csv')
    prescribing = pd.read_csv('mock_prescribing.csv')
    conditions = pd.read_csv('mock_conditions.csv')
    return patients, encounters, lab_results, vitals, prescribing, conditions

patients, encounters, lab_results, vitals, prescribing, conditions = load_data()

st.title("Doctor's Dashboard")

# Select a patient
selected_patient = st.selectbox("Select Patient ID", patients['patid'].unique())

# Filter data by patient
enc = encounters[encounters['patid'] == selected_patient]
cond = conditions[conditions['patid'] == selected_patient]
lab = lab_results[lab_results['patid'] == selected_patient]
vit = vitals[vitals['patid'] == selected_patient]
pres = prescribing[prescribing['patid'] == selected_patient]

# Section 1: Patient Logs
with st.expander("Patient Logs"):
    st.write("### Encounters")
    st.dataframe(enc[['encounterid', 'enc_type', 'admit_date', 'discharge_date', 'drg']])
    st.write("### Conditions")
    st.dataframe(cond[['condition', 'condition_status', 'report_date']])

# Section 2: Timeline
with st.expander("Timeline: Schedule"):
    timeline = pd.concat([
        enc[['admit_date']].rename(columns={'admit_date': 'date'}),
        lab[['result_date']].rename(columns={'result_date': 'date'}),
        pres[['rx_start_date']].rename(columns={'rx_start_date': 'date'})
    ])
    timeline['date'] = pd.to_datetime(timeline['date'])
    st.write("### Event Timeline")
    st.dataframe(timeline.sort_values('date'))

# Section 3: Discharge Instructions
with st.expander("Discharge Instructions - Follow Up"):
    st.write("### Follow-Up Flags")
    follow_ups = []
    if any(enc['discharge_disposition'] != '01'):
        follow_ups.append("Non-routine discharge. Schedule follow-up.")
    if any(lab['abn_ind'] == 'AB'):
        follow_ups.append("Abnormal lab result found.")
    if any(pres['rx_refills'] == 0):
        follow_ups.append("Prescription refill required.")
    if any(vit['original_bmi'] > 30):
        follow_ups.append("High BMI: Consider dietary/lifestyle guidance.")
    if any(vit['systolic'] > 140) or any(vit['diastolic'] > 90):
        follow_ups.append("Elevated BP: Hypertension follow-up needed.")
    st.write("\n".join(follow_ups) if follow_ups else "No urgent follow-up flags.")

# Section 4: Clinical Alerts
with st.expander("Clinical Alerts"):
    st.write("### Active Conditions and Risk Indicators")
    active = cond[cond['condition_status'] == 'AC']
    st.dataframe(active)
    alerts = []
    if any(active['condition'].str.contains("Diabetes", case=False)):
        alerts.append("Diabetes: Monitor glucose levels.")
    if any(active['condition'].str.contains("Hypertension", case=False)):
        alerts.append("Hypertension: Monitor BP.")
    st.write("\n".join(alerts) if alerts else "No immediate clinical alerts.")

# Section 5: Family + Patient History
with st.expander("Family + Patient History"):
    st.write("### Demographics")
    st.dataframe(patients[patients['patid'] == selected_patient])
    st.write("### Condition History")
    st.dataframe(cond)

# Section 6: History of Prescription
with st.expander("History of Prescription"):
    st.write("### Medication Timeline")
    st.dataframe(pres[['rx_med_name', 'rx_start_date', 'rx_end_date', 'rx_refills']])
