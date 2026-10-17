
# Dashboard Analisis Kualitas Udara Beijing

Proyek analisis data PM2.5 dari 12 stasiun pemantauan di Beijing (Maret 2013 - Februari 2017) menggunakan Air Quality Dataset. Hasil analisis ditampilkan dalam dashboard interaktif dengan Streamlit.

## Struktur Folder

```
submission
├── dashboard
│   ├── main_data.csv
│   └── dashboard.py
├── data
│   └── (12 file CSV stasiun)
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment

```
pip install -r requirements.txt
```

## Menjalankan Dashboard

```
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka di browser pada http://localhost:8501.
