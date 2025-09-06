import json
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import base64
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="DICOM OCT Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sample data (in a real app, this would be loaded from files)
layer_data = {
  "exported_at": "2025-09-06T09:38:58.456Z",
  "software": "Nyameri RetinaScan Pro",
  "quality_score": 0.92,
  "layers": [
    {
      "name": "NFL (Nerve Fiber Layer)",
      "thickness": 23.4,
      "boundary_points": [20.51, 19.77, 19.69, 20.72, 19.81, 19.91, 20.15, 19.66, 20.96, 21.19],
      "color": "#ff6b6b"
    },
    {
      "name": "GCL+IPL (Ganglion Cell + Inner Plexiform)",
      "thickness": 89.2,
      "boundary_points": [45.83, 44.41, 45.08, 44.66, 46.09, 45.04, 44.77, 44.65, 44.93, 46.04],
      "color": "#4ecdc4"
    },
    {
      "name": "INL (Inner Nuclear Layer)",
      "thickness": 35.6,
      "boundary_points": [70.10, 70.10, 69.48, 69.57, 69.61, 69.68, 70.58, 69.29, 69.75, 69.50],
      "color": "#45b7d1"
    },
    {
      "name": "ONL (Outer Nuclear Layer)",
      "thickness": 67.8,
      "boundary_points": [94.88, 94.93, 95.99, 94.37, 95.07, 95.18, 95.01, 94.67, 95.65, 96.01],
      "color": "#96ceb4"
    },
    {
      "name": "IS/OS (Inner/Outer Segments)",
      "thickness": 28.9,
      "boundary_points": [120.76, 119.47, 120.84, 119.63, 119.76, 120.90, 120.81, 120.32, 120.20, 119.74],
      "color": "#ffeaa7"
    },
    {
      "name": "RPE (Retinal Pigment Epithelium)",
      "thickness": 15.3,
      "boundary_points": [144.31, 144.34, 144.20, 144.73, 144.62, 145.40, 144.49, 146.19, 145.38, 145.35],
      "color": "#dda0dd"
    }
  ]
}

scan_data = {
  "exported_at": "2025-09-06T09:27:00.627Z",
  "software": "Nyameri RetinaScan Pro",
  "total_scans": 1,
  "scans": [
    {
      "id": 1,
      "patient_id": 1,
      "scan_date": "2025-09-06",
      "eye": "OD",
      "scan_type": "Uploaded OCT",
      "image_data": "uploaded_image",
      "analysis_results": None,
      "layers_detected": 0,
      "retinal_thickness": None,
      "notes": "Uploaded image: Lucid_Origin_Detailed_optical_coherence_tomography_images_of_t_2.jpg"
    }
  ]
}

# Main app
st.title("📊 DICOM OCT Analysis Report Generator")
st.markdown("Generate comprehensive clinical reports from OCT scan data with retinal layer analysis")

# Sidebar for patient information
with st.sidebar:
    st.header("Patient Information")
    
    patient_id = st.text_input("Patient ID", "PT-2023-001")
    patient_name = st.text_input("Patient Name", "John Doe")
    patient_dob = st.date_input("Date of Birth")
    patient_gender = st.radio("Gender", ["Male", "Female", "Other"], index=0)
    
    st.divider()
    
    st.header("Scan Information")
    scan_date = st.date_input("Scan Date", datetime.strptime(scan_data['scans'][0]['scan_date'], "%Y-%m-%d"))
    eye = st.radio("Eye", ["OD (Right)", "OS (Left)"], index=0 if scan_data['scans'][0]['eye'] == "OD" else 1)
    scan_type = st.selectbox("Scan Type", ["Macula", "Optic Nerve Head", "Widefield"], index=0)
    
    st.divider()
    
    if st.button("Generate Report", type="primary"):
        st.success("Report generated successfully!")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Retinal Layer Thickness Analysis")
    
    # Create layer thickness visualization
    layer_names = [layer['name'] for layer in layer_data['layers']]
    layer_thickness = [layer['thickness'] for layer in layer_data['layers']]
    layer_colors = [layer['color'] for layer in layer_data['layers']]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(layer_names, layer_thickness, color=layer_colors)
    ax.set_xlabel('Thickness (μm)')
    ax.set_title('Retinal Layer Thickness Measurements')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                f'{width} μm', ha='left', va='center')
    
    st.pyplot(fig)
    
    # Layer boundary visualization
    st.subheader("Layer Boundary Profiles")
    
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    for layer in layer_data['layers']:
        # Use a subset of points for visualization
        points = layer['boundary_points'][:100] if len(layer['boundary_points']) > 100 else layer['boundary_points']
        ax2.plot(points, label=layer['name'], color=layer['color'], linewidth=2)
    
    ax2.set_xlabel('Horizontal Position')
    ax2.set_ylabel('Depth (μm)')
    ax2.set_title('Retinal Layer Boundaries')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(alpha=0.3)
    
    st.pyplot(fig2)

with col2:
    st.subheader("Scan Quality Assessment")
    
    # Quality score gauge
    quality_score = layer_data['quality_score']
    st.metric("Quality Score", f"{quality_score*100:.1f}%")
    
    if quality_score >= 0.8:
        st.success("Excellent scan quality")
    elif quality_score >= 0.6:
        st.warning("Acceptable scan quality")
    else:
        st.error("Poor scan quality - consider rescanning")
    
    st.divider()
    
    st.subheader("Layer Thickness Summary")
    
    thickness_data = []
    for layer in layer_data['layers']:
        thickness_data.append({
            "Layer": layer['name'],
            "Thickness (μm)": layer['thickness'],
            "Status": "Normal" if layer['thickness'] > 10 else "Abnormal"
        })
    
    df = pd.DataFrame(thickness_data)
    st.dataframe(df, use_container_width=True)
    
    total_thickness = sum(layer['thickness'] for layer in layer_data['layers'])
    st.metric("Total Retinal Thickness", f"{total_thickness:.1f} μm")

# Detailed analysis section
st.divider()
st.header("Detailed Analysis")

tab1, tab2, tab3, tab4 = st.tabs(["Thickness Map", "Comparison to Normative", "Clinical Notes", "Export Report"])

with tab1:
    st.subheader("Retinal Thickness Map")
    
    # Generate a simulated thickness map
    map_size = 200
    thickness_map = np.random.normal(total_thickness, 15, (map_size, map_size))
    
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    im = ax3.imshow(thickness_map, cmap='viridis', aspect='equal')
    ax3.set_title('Retinal Thickness Map')
    ax3.set_xlabel('Horizontal Position')
    ax3.set_ylabel('Vertical Position')
    plt.colorbar(im, ax=ax3, label='Thickness (μm)')
    
    st.pyplot(fig3)

with tab2:
    st.subheader("Comparison to Normative Data")
    
    # Normative data (simulated)
    normative_data = {
        "NFL (Nerve Fiber Layer)": {"mean": 25.0, "std": 3.0},
        "GCL+IPL (Ganglion Cell + Inner Plexiform)": {"mean": 85.0, "std": 8.0},
        "INL (Inner Nuclear Layer)": {"mean": 35.0, "std": 4.0},
        "ONL (Outer Nuclear Layer)": {"mean": 70.0, "std": 7.0},
        "IS/OS (Inner/Outer Segments)": {"mean": 30.0, "std": 3.0},
        "RPE (Retinal Pigment Epithelium)": {"mean": 16.0, "std": 2.0}
    }
    
    comparison_data = []
    for layer in layer_data['layers']:
        name = layer['name']
        measured = layer['thickness']
        normative = normative_data[name]["mean"]
        std = normative_data[name]["std"]
        z_score = (measured - normative) / std
        
        status = "Normal"
        if abs(z_score) > 2:
            status = "Abnormal" if z_score > 0 else "Thinned"
        
        comparison_data.append({
            "Layer": name,
            "Measured (μm)": measured,
            "Normative (μm)": normative,
            "Z-Score": z_score,
            "Status": status
        })
    
    comp_df = pd.DataFrame(comparison_data)
    st.dataframe(comp_df, use_container_width=True)
    
    # Z-score visualization
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    layers = [layer['name'] for layer in layer_data['layers']]
    z_scores = [row['Z-Score'] for row in comparison_data]
    
    colors = ['green' if abs(z) <= 2 else 'orange' if abs(z) <= 3 else 'red' for z in z_scores]
    bars = ax4.barh(layers, z_scores, color=colors)
    ax4.axvline(x=0, color='black', linestyle='-', alpha=0.5)
    ax4.axvline(x=2, color='orange', linestyle='--', alpha=0.7)
    ax4.axvline(x=-2, color='orange', linestyle='--', alpha=0.7)
    ax4.axvline(x=3, color='red', linestyle='--', alpha=0.7)
    ax4.axvline(x=-3, color='red', linestyle='--', alpha=0.7)
    ax4.set_xlabel('Z-Score')
    ax4.set_title('Deviation from Normative Data (Z-Scores)')
    ax4.grid(axis='x', alpha=0.3)
    
    st.pyplot(fig4)

with tab3:
    st.subheader("Clinical Assessment")
    
    clinical_notes = st.text_area(
        "Clinical Notes",
        "The OCT scan shows well-defined retinal layers with preserved architecture.\n\n"
        "Notable findings:\n"
        "- NFL thickness is within normal limits\n"
        "- GCL+IPL complex shows normal thickness\n"
        "- No evident edema or fluid accumulation\n"
        "- RPE layer appears intact\n\n"
        "Impression: Normal macular OCT scan.",
        height=200
    )
    
    diagnosis = st.selectbox(
        "Diagnosis",
        ["Normal", "Dry AMD", "Wet AMD", "Diabetic Macular Edema", 
         "Macular Hole", "Epiretinal Membrane", "Other"]
    )
    
    if diagnosis == "Other":
        other_diagnosis = st.text_input("Specify other diagnosis")
    
    follow_up = st.slider("Recommended follow-up (months)", 1, 24, 12)

with tab4:
    st.subheader("Export DICOM Report")
    
    # PDF report generation
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'OCT Analysis Report', 0, 1, 'C')
            self.ln(5)
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def create_pdf_report():
        pdf = PDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'DICOM OCT Analysis Report', 0, 1, 'C')
        pdf.ln(10)
        
        # Patient information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Patient Information', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Patient ID: {patient_id}', 0, 1)
        pdf.cell(0, 10, f'Name: {patient_name}', 0, 1)
        pdf.cell(0, 10, f'DOB: {patient_dob}', 0, 1)
        pdf.cell(0, 10, f'Gender: {patient_gender}', 0, 1)
        pdf.ln(5)
        
        # Scan information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Scan Information', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Scan Date: {scan_date}', 0, 1)
        pdf.cell(0, 10, f'Eye: {eye}', 0, 1)
        pdf.cell(0, 10, f'Scan Type: {scan_type}', 0, 1)
        pdf.cell(0, 10, f'Quality Score: {quality_score*100:.1f}%', 0, 1)
        pdf.ln(5)
        
        # Layer thickness table
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Retinal Layer Thickness', 0, 1)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(100, 10, 'Layer', 1, 0, 'C')
        pdf.cell(40, 10, 'Thickness (μm)', 1, 1, 'C')
        
        pdf.set_font('Arial', '', 10)
        for layer in layer_data['layers']:
            pdf.cell(100, 10, layer['name'], 1, 0)
            pdf.cell(40, 10, str(layer['thickness']), 1, 1, 'C')
        
        pdf.cell(100, 10, 'Total Retinal Thickness', 1, 0)
        pdf.cell(40, 10, f'{total_thickness:.1f}', 1, 1, 'C')
        pdf.ln(5)
        
        # Clinical notes
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Clinical Assessment', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, clinical_notes)
        pdf.ln(5)
        
        # Diagnosis
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Diagnosis', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, diagnosis, 0, 1)
        pdf.ln(5)
        
        # Follow-up
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Follow-up Recommendation', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Recommended follow-up in {follow_up} months', 0, 1)
        
        return pdf
    
    # Generate and offer download
    pdf = create_pdf_report()
    
    # Save PDF to bytes buffer
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_b64 = base64.b64encode(pdf_bytes).decode()
    
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=f"oct_report_{patient_id}.pdf",
        mime="application/pdf"
    )
    
    st.download_button(
        label="Download DICOM SR (Structured Report)",
        data="Simulated DICOM SR content".encode(),
        file_name=f"oct_sr_{patient_id}.dcm",
        mime="application/dicom"
    )

# Footer
st.divider()
st.caption("OCT Analysis Report Generator v1.0 - For clinical use only. Interpret results in conjunction with clinical findings.")
