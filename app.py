
import streamlit as st
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from collections import defaultdict
import mimetypes
import csv
import json

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Sortify | Automated File Organizer",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# FILE CATEGORIES
# --------------------------------------------------
CATEGORIES = {
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
        ".xls", ".xlsx", ".csv", ".ppt", ".pptx", ".md"
    },
    "Images": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
        ".svg", ".tiff", ".tif", ".ico", ".heic"
    },
    "Videos": {
        ".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv",
        ".flv", ".m4v", ".mpeg", ".mpg"
    },
    "Music": {
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a",
        ".wma", ".aiff", ".opus"
    },
    "Archives": {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"
    },
    "Code": {
        ".py", ".html", ".css", ".js", ".ts", ".jsx",
        ".tsx", ".java", ".c", ".cpp", ".h", ".cs",
        ".php", ".rb", ".go", ".rs", ".json", ".xml",
        ".yaml", ".yml", ".sql", ".sh", ".bat"
    },
    "Programs": {
        ".exe", ".msi", ".apk", ".app", ".deb", ".rpm",
        ".dmg", ".iso"
    }
}

CATEGORY_ICONS = {
    "Documents": "📄",
    "Images": "🖼️",
    "Videos": "🎬",
    "Music": "🎵",
    "Archives": "🗜️",
    "Code": "💻",
    "Programs": "⚙️",
    "Others": "📦"
}


def categorize_file(filename):
    """Return a category based on a file's extension."""
    extension = Path(filename).suffix.lower()

    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category

    return "Others"


def format_size(size):
    """Convert bytes to a readable file size."""
    size = float(size)

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} TB"


def unique_zip_name(filename, used_names):
    """Prevent duplicate filenames inside the same ZIP folder."""
    path = Path(filename)
    candidate = path.name
    counter = 1

    while candidate.lower() in used_names:
        candidate = f"{path.stem}_{counter}{path.suffix}"
        counter += 1

    used_names.add(candidate.lower())
    return candidate


def build_zip(files):
    """Create a ZIP containing categorized folders."""
    output = BytesIO()
    used_names = defaultdict(set)

    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for item in files:
            category = item["category"]
            filename = unique_zip_name(
                item["name"],
                used_names[category]
            )

            archive_path = f"{category}/{filename}"
            archive.writestr(archive_path, item["data"])

    output.seek(0)
    return output.getvalue()


# --------------------------------------------------
# THEME
# --------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    theme = st.radio(
        "Appearance",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "Dark" else 1
    )
    st.session_state.theme = theme

if theme == "Dark":
    background = "#0b1120"
    panel = "#151e30"
    text_color = "#f1f5f9"
    muted = "#a5b4c8"
    border = "#29364d"
    accent = "#38bdf8"
else:
    background = "#f4f7fb"
    panel = "#ffffff"
    text_color = "#172033"
    muted = "#64748b"
    border = "#dbe3ef"
    accent = "#0284c7"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {background};
        color: {text_color};
    }}

    [data-testid="stSidebar"] {{
        background-color: {panel};
        border-right: 1px solid {border};
    }}

    h1, h2, h3, p, label {{
        color: {text_color};
    }}

    .hero {{
        padding: 26px;
        border: 1px solid {border};
        border-radius: 20px;
        background: {panel};
        margin-bottom: 22px;
    }}

    .hero-title {{
        font-size: clamp(27px, 4vw, 42px);
        font-weight: 800;
        margin-bottom: 8px;
        color: {text_color};
    }}

    .hero-subtitle {{
        color: {muted};
        font-size: 16px;
    }}

    .metric-card {{
        background: {panel};
        border: 1px solid {border};
        padding: 18px;
        border-radius: 15px;
        min-height: 105px;
    }}

    .metric-label {{
        color: {muted};
        font-size: 13px;
    }}

    .metric-value {{
        color: {text_color};
        font-size: 25px;
        font-weight: 750;
        margin-top: 6px;
    }}

    .section-card {{
        background: {panel};
        border: 1px solid {border};
        border-radius: 15px;
        padding: 17px;
        margin-bottom: 12px;
    }}

    div.stButton > button,
    div.stDownloadButton > button {{
        border-radius: 10px;
        font-weight: 650;
        min-height: 42px;
    }}

    .small-note {{
        color: {muted};
        font-size: 13px;
    }}

    [data-testid="stFileUploader"] {{
        border-radius: 12px;
    }}

    @media (max-width: 640px) {{
        .hero {{ padding: 18px; }}
        .metric-value {{ font-size: 21px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------
with st.sidebar:
    st.markdown("# 📂 Sortify")
    st.caption("Automated File Organizer")
    st.divider()
    st.markdown("### How it works")
    st.markdown(
        """
        1. Upload your files.
        2. Let Sortify classify them.
        3. Preview and filter files.
        4. Download your organized ZIP.
        """
    )
    st.divider()
    st.caption("Online edition • No local installation required")

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">📂 Smart File Organizer</div>
        <div class="hero-subtitle">
            Clean up digital clutter. Sort files automatically.
            Download everything in a neatly structured ZIP.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# UPLOAD
# --------------------------------------------------
st.subheader("01 · Upload your files")
st.write(
    "Choose one or more files from your device. "
    "Your originals are not moved or deleted."
)

uploaded_files = st.file_uploader(
    "Select files to organize",
    accept_multiple_files=True,
    help="Upload documents, images, audio, videos, code and other files."
)

if not uploaded_files:
    st.info(
        "👋 Start by uploading files. Your organized file dashboard "
        "will appear here."
    )

    st.markdown("### Supported categories")

    cols = st.columns(4)
    categories_to_show = [
        "Documents", "Images", "Videos", "Music",
        "Archives", "Code", "Programs", "Others"
    ]

    for index, category in enumerate(categories_to_show):
        with cols[index % 4]:
            st.markdown(
                f"""
                <div class="section-card">
                    <div style="font-size:27px">
                        {CATEGORY_ICONS[category]}
                    </div>
                    <strong>{category}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.stop()

# --------------------------------------------------
# PROCESS FILES
# --------------------------------------------------
files = []
seen_uploads = set()

for uploaded in uploaded_files:
    file_data = uploaded.getvalue()

    # Distinguish separate uploaded files, while avoiding
    # duplicate processing of the same filename and content.
    identity = (uploaded.name, len(file_data), hash(file_data))

    if identity in seen_uploads:
        continue

    seen_uploads.add(identity)

    files.append({
        "name": Path(uploaded.name).name,
        "category": categorize_file(uploaded.name),
        "size": len(file_data),
        "data": file_data,
        "type": uploaded.type or
                mimetypes.guess_type(uploaded.name)[0] or
                "application/octet-stream"
    })

# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------
total_files = len(files)
total_size = sum(item["size"] for item in files)
category_counts = defaultdict(int)

for item in files:
    category_counts[item["category"]] += 1

st.divider()
st.subheader("02 · Organization overview")

metric_cols = st.columns(4)

metrics = [
    ("Total files", str(total_files), "📁"),
    ("Total size", format_size(total_size), "💾"),
    ("Categories used", str(len(category_counts)), "🗂️"),
    ("Theme", theme, "🎨")
]

for col, (label, value, icon) in zip(metric_cols, metrics):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{icon} {label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# --------------------------------------------------
# CATEGORY SUMMARY
# --------------------------------------------------

# CATEGORY SUMMARY
# --------------------------------------------------
st.markdown("### Category breakdown")

categories_to_show = [
    "Documents",
    "Images",
    "Videos",
    "Music",
    "Archives",
    "Code",
    "Programs",
    "Others"
]

category_cols = st.columns(4)

for index, category in enumerate(categories_to_show):
    with category_cols[index % 4]:
        count = category_counts.get(category, 0)
        st.markdown(
            f"""
            <div class="section-card">
                <div style="font-size:24px">
                    {CATEGORY_ICONS[category]}
                </div>
                <strong>{category}</strong>
                <div style="font-size:23px;font-weight:750;
                            margin-top:8px">{count}</div>
                <div class="small-note">file(s)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# --------------------------------------------------
# SEARCH AND FILTER
# --------------------------------------------------
st.divider()
st.subheader("03 · Explore your files")

search_col, filter_col = st.columns([2, 1])

with search_col:
    search_term = st.text_input(
        "🔎 Search by filename",
        placeholder="Example: report, photo, notes..."
    )

with filter_col:
    available_categories = ["All"] + categories_to_show
    selected_category = st.selectbox(
        "Filter by category",
        available_categories
    )

filtered_files = []

for item in files:
    matches_search = search_term.lower() in item["name"].lower()
    matches_category = (
        selected_category == "All"
        or item["category"] == selected_category
    )

    if matches_search and matches_category:
        filtered_files.append(item)

st.caption(
    f"Showing {len(filtered_files)} of {total_files} uploaded files"
)

# --------------------------------------------------
# FILE TABLE
# --------------------------------------------------
if filtered_files:
    table_data = []

    for index, item in enumerate(filtered_files, start=1):
        table_data.append({
            "No.": index,
            "File name": item["name"],
            "Category": (
                f"{CATEGORY_ICONS[item['category']]} "
                f"{item['category']}"
            ),
            "File size": format_size(item["size"]),
            "Format": Path(item["name"]).suffix.lower() or "No extension"
        })

    st.dataframe(
        table_data,
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("No files match your current search or filter.")

# --------------------------------------------------
# PREVIEW
# --------------------------------------------------
st.divider()
st.subheader("04 · File preview")

if filtered_files:
    selected_name = st.selectbox(
        "Choose a file to preview",
        options=[
            f"{item['name']} — {item['category']}"
            for item in filtered_files
        ]
    )

    selected_index = [
        f"{item['name']} — {item['category']}"
        for item in filtered_files
    ].index(selected_name)

    selected_file = filtered_files[selected_index]
    filename = selected_file["name"]
    extension = Path(filename).suffix.lower()
    file_bytes = selected_file["data"]

    st.markdown(f"**Selected file:** `{filename}`")
    st.caption(
        f"Category: {selected_file['category']} · "
        f"Size: {format_size(selected_file['size'])}"
    )

    try:
        if extension in {
            ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"
        }:
            st.image(file_bytes, caption=filename, use_container_width=True)

        elif extension in {".txt", ".md", ".py", ".html", ".css",
                           ".js", ".json", ".xml", ".yaml", ".yml",
                           ".sql", ".sh", ".c", ".cpp", ".java"}:
            preview_text = file_bytes[:100_000].decode(
                "utf-8", errors="replace"
            )
            st.code(
                preview_text,
                language=(
                    "python" if extension == ".py"
                    else "json" if extension == ".json"
                    else "html" if extension == ".html"
                    else "css" if extension == ".css"
                    else "javascript" if extension == ".js"
                    else "text"
                )
            )

            if len(file_bytes) > 100_000:
                st.caption("Preview limited to the first 100 KB.")

        elif extension == ".csv":
            import pandas as pd
            import io

            try:
                dataframe = pd.read_csv(
                    io.BytesIO(file_bytes),
                    nrows=200
                )
                st.dataframe(dataframe, use_container_width=True)
            except Exception:
                st.info("The CSV could not be displayed as a table.")

        elif extension == ".pdf":
            st.info(
                "PDF preview depends on browser support. "
                "Download the file to view it."
            )

        else:
            st.info(
                "Preview is not available for this file type. "
                "You can still include it in your organized ZIP."
            )

    except Exception as error:
        st.warning(f"Preview unavailable: {error}")

    st.download_button(
        label="⬇️ Download this file",
        data=file_bytes,
        file_name=filename,
        mime=selected_file["type"],
        key="download_single_file"
    )

# --------------------------------------------------
# DOWNLOAD ORGANIZED ZIP
# --------------------------------------------------
st.divider()
st.subheader("05 · Export organized files")

st.write(
    "Your ZIP will contain separate folders such as Documents, "
    "Images, Videos, Music, Code, Archives and Others."
)

if files:
    try:
        zip_data = build_zip(files)

        st.download_button(
            label="📦 Download organized ZIP",
            data=zip_data,
            file_name="Sortify_Organized_Files.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )

        st.success(
            "Your organized ZIP is ready. Download it to save "
            "the categorized files on your device."
        )

    except Exception as error:
        st.error(f"Could not create the ZIP: {error}")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption(
    "Sortify · Automated File Organizer · "
    "Online upload mode · Original files remain unchanged."
)
